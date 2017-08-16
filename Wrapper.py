#! /usr/bin/env python
# -*- coding: utf8 -*-

'''
module for AT wrapper.
'''
from __future__ import print_function

import os, re
from time import time
from pyAT2.AT.CmdSet.CmdSetBase import CmdSetBase as CSB

from RespParser import Parser, ParserDataOnly

class Wrapper(object):
    '''
    wrapper class for AT command set.

    the limitation to use static function for AT commands is, I cannot find it,
    there is no way to overlay a class attribute.
    '''
    DEBUGMODE = False

    #
    # mode for STK. For the const needed in Unitary.CONFIG, MUST be defined
    # here. This is a limitation. Lucky thing is, there are not so many const.
    AR = 0
    ER = 1

    # string pattern for AT command. If it is not an AT, it will be processed
    # first as an API. There is no other options.
    VALID_AT_NAME = re.compile(r"^[a-z0-9_]+$")

    def __init__(self, path=None):
        '''
        the default command set will be loaded..
        '''
        self.interface = None
        # to let wrapper simplify the AT response, default is True.
        self.parsers = [None]

        # to get command set objects and there exported attribute list.
        # when path is none, standard AT command shall be loaded.
        self.cmd_set_obj, attr_set = CSB.loadStdCmdSet(path)

        # add attribute dynamically to wrapper class.
        for key in attr_set:
            setattr(Wrapper, key, attr_set[key])

        # check debug mode
        if 'CSB;' in os.environ.get("PYAT_DEBUG", '').upper():
            CSB.DEBUGMODE = True


    def parserPush(self, obj):
        '''
        add AT response parser.

        Parameters
        --------------------------------
        obj: Parser object

        Returns
        --------------------------------
        True/False.

        Raises
        --------------------------------

        '''
        if isinstance(obj, Parser):
            self.parsers.append(obj)
            return True
        return False

    def parserPop(self):
        '''
        remove the parser being used.

        Parameters
        --------------------------------

        Returns
        --------------------------------
        True/False.

        Raises
        --------------------------------

        '''
        if len(self.parsers) > 1:
            del self.parsers[-1]
            return True
        return False

    def attachInterface(self, interface):
        '''
        attach communication interface.
        '''
        if self.interface is not None:
            del self.interface

        self.interface = interface

    def getInterface(self):
        return self.interface

    def testInterface(self, retry=3):
        '''
        to test interface if it responds any AT command.

        exec_cmd shall not be used here. The purpose of this function is to see
        if there is any data in and out on the target interface..
        '''
        res = False

        prev_to = self.interface.get_timeout()
        self.interface.set_timeout(0.5)
        retry *= 2
        while retry > 0:
            retry -= 1

            self.interface.write("at\r", nologging=True)
            line = self.interface.read(nologging=True)
            if line is not None:
                res = True
                break

        self.interface.set_timeout(prev_to)
        return res


    def readLinesP(self, pattern_in, timeout=60):
        '''
        to read and wait until a pattern string is read or timeout reached.

        Parameters
        --------------------------------
        pattern_in: regex.

        timeout: float, time seconds

        Returns
        --------------------------------
        response: str, all the data read during this function.

        last: str, the last line read. If timeout reached, this value shall
            be None.

        Raises
        --------------------------------

        '''
        if isinstance(pattern_in, str) or isinstance(pattern_in, unicode):
            pattern = re.compile(pattern_in)
        else:
            pattern = pattern_in

        prev_to = self.interface.get_timeout()
        # timeout is not used directly...
        self.interface.set_timeout(timeout/10)

        time_st = time()

        resp = ""
        lastline = None
        while True:
            # total timeout...
            if time()-time_st > timeout:
                lastline = None
                break

            lastline = self.interface.read()
            if lastline is None:
                continue

            resp += lastline
            if pattern.match(lastline) is not None:
                break

        self.interface.set_timeout(prev_to)
        return resp, lastline


    def send(self, at_cmd, **options):
        '''
        to send a at command.
        '''
        resp = CSB.exec_cmd(self.interface, at_cmd, CSB.EXEC, **options)
        parser = self.parsers[-1]
        if parser is not None:
            resp = parser.parse(at_cmd, resp)

        return resp


    def loadVendorCmdSet(self):
        '''
        first to get vendor ID and module ID
        '''
        self.parserPush(ParserDataOnly())
        vid = self.cgmi()
        if vid is None or len(vid) == 0:
            raise ValueError("Failed to get vendor ID!")
        mid = self.cgmm()
        if mid is None or len(mid) == 0:
            raise ValueError("Failed to get module ID!")
        self.parserPop()

        vid = vid[-1]
        mid = mid[-1]
        cmd, attr_set = CSB.loadVendorCmdSet(vid, mid)

        self.cmd_set_obj = dict(self.cmd_set_obj.items() + cmd.items())
        for key in attr_set:
            setattr(Wrapper, key, attr_set[key])



    def __getattr__(self, name):

        def method(*args, **options):
            '''
            function to execute a unknown function or AT command.

            Parameters
            --------------------------------
            args: list of parameters

            Returns
            --------------------------------
            execution result.

            Raises
            --------------------------------
            AttributeError

            '''
            found = False
            is_function = False
            resp = None
            at_cmd = name

            # step 1, to check if it could be a function name, which contains
            # any character in upper case.
            # this is useful as their input parameters will be different.
            # So far the only way to identify an API or at is from the name.
            # There is no other feasible way, maybe, this can be enforced...
            if Wrapper.VALID_AT_NAME.match(at_cmd) is None:
                is_function = True

            # step 2, to try the mehtod with all the installed modules.
            for key in sorted(self.cmd_set_obj, key=lambda x: x[1]):
                obj = self.cmd_set_obj[key][0]
                try:
                    if is_function:
                        try:
                            resp = getattr(obj, at_cmd)(*args, **options)
                            found = True
                            break

                        # TypeError is for wrong parameter, AttributeError is there is no such API.
                        except (AttributeError, TypeError):
                            pass

                    if not found:
                        resp = getattr(obj, at_cmd)(self.interface, *args, **options)
                        found = True
                        break

                except AttributeError:
                    continue

            if not found:
                # the naming rule is forced. API must be found!
                if self.DEBUGMODE:
                    print('WRAP: %s is not found in known funcitons.'%(name), is_function)

                if is_function:
                    raise AttributeError("%s is not recongized as an API."%(at_cmd))

                if self.interface is None:
                    raise AttributeError("Interface is not set for %s."%(at_cmd))

                at_cmd, mode = CSB.get_default_config(at_cmd)
                resp = CSB.exec_cmd(self.interface, at_cmd, mode, *args, **options)

            # re-format the response.
            if not is_function:
                try:
                    parser = self.parsers[-1]
                    if parser is not None and resp is not None:
                        resp = parser.parse(at_cmd, resp)
                except TypeError:
                    pass

            return resp

        return method

