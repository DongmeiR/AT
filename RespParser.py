#! /usr/bin/env python
# -*- coding: utf8 -*-

'''
AT resposne parser module.
'''

from __future__ import print_function

import re

PATTERN_ERROR = re.compile(r"^ERROR|^\+CME ERROR|^\+CMS ERROR")
PATTERN_OK = re.compile(r"^OK")

class Parser(object):

    def parse(self, atcmd, resp):
        '''
        atcmd shall be the orignal command input.
        it has two possible format, for exam: at[+^]name, or name

        assumption: there is no other pre-processing...
        '''
        if isinstance(resp, str) or isinstance(resp, unicode):
            resp = filter(None, re.split(r"\r|\n", resp))

            if len(resp) > 0:
                # this is echo back. ignore it.
                pattern = re.compile(".." + self._check_at_cmd(atcmd))

                if pattern.match(resp[0]):
                    resp = resp[1:]

        return resp


    @staticmethod
    def split(string_data, pattern=r',', convert=True):
        '''

        -----

        '''
        res = []
        res_t = filter(None, re.split(pattern, string_data))

        for ele in res_t:
            val = ele
            if len(val) >= 2:
                if val[0] == '"' and val[-1] == '"':
                    val = val[1:-1]
                elif val[0] == '\'' and val[-1] == '\'':
                    val = val[1:-1]
            if convert:
                try:
                    val = int(val)
                except ValueError:
                    pass

            res.append(val)

        return res


    def _check_at_cmd(self, atcmd):
        atcmd = re.split(r"\?|\=", atcmd)[0]
        temp = re.match(r"^([aA][tT])?([\^\+\@])?(.*)", atcmd)
        if temp is not None:
            temp = temp.groups()
            if len(temp) == 3:
                atcmd = "." + temp[-1]
        return atcmd


class ParserDataOnly(Parser):

    '''
    return types:
    []:  OK without resp
    [...] OK with resp, OK is not included..
    str: error
    '''
    def parse(self, atcmd, resp):

        resp = super(ParserDataOnly, self).parse(atcmd, resp)
        if isinstance(resp, list) and len(resp) > 0:
            if PATTERN_ERROR.match(resp[-1]):
                return resp[-1]

            if PATTERN_OK.match(resp[-1]):
                return resp[:-1]

        # the content is unknown...
        return resp


class ParserSimple(ParserDataOnly):

    '''
    return types:
    []:  OK without resp
    [...] OK with resp, OK is not included..  --> to process it further...
    str: error
    '''
    def parse(self, atcmd, resp):

        resp = super(ParserSimple, self).parse(atcmd, resp)
        if isinstance(resp, list) and len(resp) > 0:
            # to generate the filter pattern.
            pattern_str = self._check_at_cmd(atcmd).upper()
            pattern = re.compile("%s: (.*)"%(pattern_str))
            resp_new = []
            for ele in resp:
                res = pattern.match(ele)
                if res is not None:
                    resp_new.append(res.group(1))
                else:
                    resp_new.append(ele)

            resp = resp_new

        return resp

