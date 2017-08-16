
from __future__ import print_function

# python suggests to use the format 2.2rc1, instead of python 2.2r01.
__version__ = "2.2.3"

VERSION = __version__

AUTHOR = 'Ximing.CHEN@gemalto.com, wenbin.du@gemalto.com'

'''
Change list:

== 2.1.rc01 ==
All the basic functions are running, such as,
* AT command and command set by vendor and product;
* log;
* interface;
* unitary;
* STT decoder
* memory leak tool;

== 2.1rc02 ==
* change version label format, to 2.xrcy.
* TD01: Improve support reconnection of USB port, in case of module restart, in Interface level.
* TD02: Add support of OMADM related functions.

== 2.1rc03 ==
* integrate memory leak checking into pyATUnitary
* serial port auto-detect
* add Unitary.X to run unitary cases.
* add AT parser
* add support of BGS5

== 2.1 ==
* auto capture trace
* re-format serial URL config like a URL.
* support project filter in pyATUnitary
* bug fix.

== 2.2rc1 ==
* support test case content from excel.

== 2.2.1 ==
* support init.xls, and loopcount, project, type.
* bug fix: Serial interface setting timeout issue.

== 2.2.2 ==
* bug fix: when generating XLS test class, part of EXCEL file name was removed.
* bug fix: grammer error in wrapper.
* bug fix: line with empty configitem shall be skipped.
+ optimize the loopcount output.
+ add more log output to pyATUnitaryXLS
+ load xls files in multiple process to speed up.
* bug fix of debug trace lost in case of restart.

== 2.2.3 ==
* bug fix: with xlrd, IndexError for empty sheet.
* bug fix: with xlrd, unify the behaviour with openpyxl on empty cell, and
    the difference of string value type from windows&linux.
* bug fix: loopcount counting is not correct when only some fails.
+ oct/hex support in excel file.
+ new STT decoder for socket functions
* bug fix: excel loading issue.
+ new utility git2cc.
* bug fix: init.xls not loaded issue.
+ new command line parameter -n/--name to set test report file name for X.
+ add new command line parameter -o: operator filter for test case

Known issues
* HTML test report display wrongly from a web server
* Some interfaces are missing for driver test

'''
