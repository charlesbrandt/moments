#!/usr/bin/env python2.3
#
# SchoolTool - common information systems platform for school administration
# Copyright (c) 2003 Shuttleworth Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
SchoolTool test runner.

Syntax: test.py [options] [pathname-regexp [test-regexp]]

There are two kinds of tests:
  - unit tests (or programmer tests) test the internal workings of various
    components of the system
  - functional tests (acceptance tests, customer tests) test only externaly
    visible system behaviour

You can choose to run unit tests (this is the default mode), functional tests
(by giving a -f option to test.py) or both (by giving both -u and -f options).

Test cases are located in the directory tree starting at the location of this
script, in subdirectories named 'tests' for unit tests and 'ftests' for
functional tests, in Python modules named 'test*.py'.  They are then filtered
according to pathname and test regexes.  Alternatively, packages may just have
'tests.py' and 'ftests.py' instead of subpackages 'tests' and 'ftests'
respectively.

A leading "!" in a regexp is stripped and negates the regexp.  Pathname
regexp is applied to the whole path (package/package/module.py). Test regexp
is applied to a full test id (package.package.module.class.test_method).

Options:
  -h, --help            print this help message
  -v                    verbose (print dots for each test run)
  -vv                   very verbose (print test names)
  -q                    quiet (do not print anything on success)
  -w                    enable warnings about omitted test cases
  -d                    invoke pdb when an exception occurs
  -p                    show progress bar (can be combined with -v or -vv)
  -u                    select unit tests (default)
  -f                    select functional tests
  --level n             select only tests at level n or lower
  --all-levels          select all tests
  --list-files          list all selected test files
  --list-tests          list all selected test cases
  --list-hooks          list all loaded test hooks
  --coverage            create code coverage reports
  --search-in dir       limit directory tree walk to dir (optimisation)
  --immediate-errors    show errors as soon as they happen (default)
  --delayed-errors      show errors after all unit tests were run
"""
#
# This script borrows ideas from Zope 3's test runner heavily.  It is smaller
# and cleaner though, at the expense of more limited functionality.
#

import re
import os
import sys
import time
import types
import getopt
import unittest
import traceback
import linecache
import pdb
from sets import Set

__metaclass__ = type


class Options:
    """Configurable properties of the test runner."""

    # test location
    basedir = ''                # base directory for tests (defaults to
                                # basedir of argv[0] + 'src'), must be absolute
    search_in = ()              # list of subdirs to traverse (defaults to
                                # basedir)
    follow_symlinks = True      # should symlinks to subdirectories be
                                # followed? (hardcoded, may cause loops)

    # which tests to run
    unit_tests = False          # unit tests (default if both are false)
    functional_tests = False    # functional tests

    # test filtering
    level = 1                   # run only tests at this or lower level
                                # (if None, runs all tests)
    pathname_regex = ''         # regexp for filtering filenames
    test_regex = ''             # regexp for filtering test cases

    # actions to take
    list_files = False          # --list-files
    list_tests = False          # --list-tests
    list_hooks = False          # --list-hooks
    run_tests = True            # run tests (disabled by --list-foo)
    postmortem = False          # invoke pdb when an exception occurs

    # output verbosity
    verbosity = 0               # verbosity level (-v)
    quiet = 0                   # do not print anything on success (-q)
    warn_omitted = False        # produce warnings when a test case is
                                # not included in a test suite (-w)
    print_import_time = True    # print time taken to import test modules
                                # (currently hardcoded)
    progress = False            # show running progress (-p)
    coverage = False            # produce coverage reports (--coverage)
    coverdir = 'coverage'       # where to put them (currently hardcoded)
    immediate_errors = True     # show tracebacks twice (--immediate-errors,
                                # --delayed-errors)
    screen_width = 80           # screen width (autodetected)


def compile_matcher(regex):
    """Returns a function that takes one argument and returns True or False.

    Regex is a regular expression.  Empty regex matches everything.  There
    is one expression: if the regex starts with "!", the meaning of it is
    reversed.
    """
    if not regex:
        return lambda x: True
    elif regex == '!':
        return lambda x: False
    elif regex.startswith('!'):
        rx = re.compile(regex[1:])
        return lambda x: rx.search(x) is None
    else:
        rx = re.compile(regex)
        return lambda x: rx.search(x) is not None


def walk_with_symlinks(top, func, arg):
    """Like os.path.walk, but follows symlinks on POSIX systems.

    If the symlinks create a loop, this function will never finish.
    """
    try:
        names = os.listdir(top)
    except os.error:
        return
    func(arg, top, names)
    exceptions = ('.', '..')
    for name in names:
        if name not in exceptions:
            name = os.path.join(top, name)
            if os.path.isdir(name):
                walk_with_symlinks(name, func, arg)


def get_test_files(cfg):
    """Returns a list of test module filenames."""
    matcher = compile_matcher(cfg.pathname_regex)
    results = []
    test_names = []
    if cfg.unit_tests:
        test_names.append('tests')
    if cfg.functional_tests:
        test_names.append('ftests')
    baselen = len(cfg.basedir) + 1
    def visit(ignored, dir, files):
        # Ignore files starting with a dot.
        # Do not not descend into subdirs containing with a dot.
        remove = []
        for idx, file in enumerate(files):
            if file.startswith('.'):
                remove.append(idx)
            elif '.' in file and os.path.isdir(os.path.join(dir, file)):
                remove.append(idx)
        remove.reverse()
        for idx in remove:
            del files[idx]
        # Look for tests.py and/or ftests.py
        if os.path.basename(dir) not in test_names:
            for name in test_names:
                if name + '.py' in files:
                    path = os.path.join(dir, name + '.py')
                    if matcher(path[baselen:]):
                        results.append(path)
            return
        if '__init__.py' not in files:
            print >> sys.stderr, "%s is not a package" % dir
            return
        for file in files:
            if file.startswith('test') and file.endswith('.py'):
                path = os.path.join(dir, file)
                if matcher(path[baselen:]):
                    results.append(path)
    if cfg.follow_symlinks:
        walker = walk_with_symlinks
    else:
        walker = os.path.walk
    for dir in cfg.search_in:
        walker(dir, visit, None)
    results.sort()
    return results


def import_module(filename, cfg, tracer=None):
    """Imports and returns a module."""
    filename = os.path.splitext(filename)[0]
    modname = filename[len(cfg.basedir):].replace(os.path.sep, '.')
    if modname.startswith('.'):
        modname = modname[1:]
    if tracer is not None:
        mod = tracer.runfunc(__import__, modname)
    else:
        mod = __import__(modname)
    components = modname.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def filter_testsuite(suite, matcher, level=None):
    """Returns a flattened list of test cases that match the given matcher."""
    if not isinstance(suite, unittest.TestSuite):
        raise TypeError('not a TestSuite', suite)
    results = []
    for test in suite._tests:
        if level is not None and getattr(test, 'level', 0) > level:
            continue
        if isinstance(test, unittest.TestCase):
            testname = test.id() # package.module.class.method
            if matcher(testname):
                results.append(test)
        else:
            filtered = filter_testsuite(test, matcher, level)
            results.extend(filtered)
    return results


def get_all_test_cases(module):
    """Returns a list of all test case classes defined in a given module."""
    results = []
    for name in dir(module):
        if not name.startswith('Test'):
            continue
        item = getattr(module, name)
        if (isinstance(item, (type, types.ClassType)) and
            issubclass(item, unittest.TestCase)):
            results.append(item)
    return results


def get_test_classes_from_testsuite(suite):
    """Returns a set of test case classes used in a test suite."""
    if not isinstance(suite, unittest.TestSuite):
        raise TypeError('not a TestSuite', suite)
    results = Set()
    for test in suite._tests:
        if isinstance(test, unittest.TestCase):
            results.add(test.__class__)
        else:
            classes = get_test_classes_from_testsuite(test)
            results.update(classes)
    return results


def get_test_cases(test_files, cfg, tracer=None):
    """Returns a list of test cases from a given list of test modules."""
    matcher = compile_matcher(cfg.test_regex)
    results = []
    startTime = time.time()
    for file in test_files:
        module = import_module(file, cfg, tracer=tracer)
        try:
            func = module.test_suite
        except AttributeError:
            print >> sys.stderr
            print >> sys.stderr, ("%s: WARNING: there is no test_suite"
                                  " function" % file)
            print >> sys.stderr
            continue
        if tracer is not None:
            test_suite = tracer.runfunc(func)
        else:
            test_suite = func()
        if test_suite is None:
            continue
        if cfg.warn_omitted:
            all_classes = Set(get_all_test_cases(module))
            classes_in_suite = get_test_classes_from_testsuite(test_suite)
            difference = all_classes - classes_in_suite
            for test_class in difference:
                # surround the warning with blank lines, otherwise it tends
                # to get lost in the noise
                print >> sys.stderr
                print >> sys.stderr, ("%s: WARNING: %s not in test suite"
                                      % (file, test_class.__name__))
                print >> sys.stderr
        if (cfg.level is not None and
            getattr(test_suite, 'level', 0) > cfg.level):
            continue
        filtered = filter_testsuite(test_suite, matcher, cfg.level)
        results.extend(filtered)
    stopTime = time.time()
    timeTaken = float(stopTime - startTime)
    if cfg.print_import_time:
        nmodules = len(test_files)
        print "Imported %d modules in %.3fs" % (nmodules, timeTaken)
        print
    return results


def get_test_hooks(test_files, cfg, tracer=None):
    """Returns a list of test hooks from a given list of test modules."""
    results = []
    dirs = Set(map(os.path.dirname, test_files))
    for dir in list(dirs):
        if os.path.basename(dir) == 'ftests':
            dirs.add(os.path.join(os.path.dirname(dir), 'tests'))
    dirs = list(dirs)
    dirs.sort()
    for dir in dirs:
        filename = os.path.join(dir, 'checks.py')
        if os.path.exists(filename):
            module = import_module(filename, cfg, tracer=tracer)
            if tracer is not None:
                hooks = tracer.runfunc(module.test_hooks)
            else:
                hooks = module.test_hooks()
            results.extend(hooks)
    return results


def extract_tb(tb, limit=None):
    """Improved version of traceback.extract_tb.

    Includes a dict with locals in every stack frame instead of the line.
    """
    list = []
    while tb is not None and (limit is None or len(list) < limit):
        frame = tb.tb_frame
        code = frame.f_code
        name = code.co_name
        filename = code.co_filename
        lineno = tb.tb_lineno
        locals = frame.f_locals
        list.append((filename, lineno, name, locals))
        tb = tb.tb_next
    return list

def format_exception(etype, value, tb, limit=None, basedir=None):
    """Improved version of traceback.format_exception.

    Includes Zope-specific extra information in tracebacks.
    """
    list = []
    if tb:
        list = ['Traceback (most recent call last):\n']
        w = list.append

        for filename, lineno, name, locals in extract_tb(tb, limit):
            w('  File "%s", line %s, in %s\n' % (filename, lineno, name))
            line = linecache.getline(filename, lineno)
            if line:
                w('    %s\n' % line.strip())
            tb_info = locals.get('__traceback_info__')
            if tb_info is not None:
                w('  Extra information: %s\n' % repr(tb_info))
            tb_supplement = locals.get('__traceback_supplement__')
            if tb_supplement is not None:
                tb_supplement = tb_supplement[0](*tb_supplement[1:])
                # XXX these should be hookable
                from zope.tales.tales import TALESTracebackSupplement
                from zope.pagetemplate.pagetemplate \
                        import PageTemplateTracebackSupplement
                if isinstance(tb_supplement, PageTemplateTracebackSupplement):
                    template = tb_supplement.manageable_object.pt_source_file()
                    if template:
                        w('  Template "%s"\n' % template)
                elif isinstance(tb_supplement, TALESTracebackSupplement):
                    w('  Template "%s", line %s, column %s\n'
                      % (tb_supplement.source_url, tb_supplement.line,
                         tb_supplement.column))
                    line = linecache.getline(tb_supplement.source_url,
                                             tb_supplement.line)
                    if line:
                        w('    %s\n' % line.strip())
                    w('  Expression: %s\n' % tb_supplement.expression)
                else:
                    w('  __traceback_supplement__ = %r\n' % (tb_supplement, ))
    list += traceback.format_exception_only(etype, value)
    return list


class CustomTestResult(unittest._TextTestResult):
    """Customised TestResult.

    It can show a progress bar, and displays tracebacks for errors and failures
    as soon as they happen, in addition to listing them all at the end.
    """

    __super = unittest._TextTestResult
    __super_init = __super.__init__
    __super_startTest = __super.startTest
    __super_stopTest = __super.stopTest
    __super_printErrors = __super.printErrors
    __super_printErrorList = __super.printErrorList

    def __init__(self, stream, descriptions, verbosity, count, cfg, hooks):
        self.__super_init(stream, descriptions, verbosity)
        self.count = count
        self.cfg = cfg
        self.hooks = hooks
        if cfg.progress:
            self.dots = False
            self._lastWidth = 0
            self._maxWidth = cfg.screen_width - len("xxxx/xxxx (xxx.x%): ") - 1

    def startTest(self, test):
        n = self.testsRun + 1
        if self.cfg.progress:
            # verbosity == 0: 'xxxx/xxxx (xxx.x%)'
            # verbosity == 1: 'xxxx/xxxx (xxx.x%): test name'
            # verbosity >= 2: 'xxxx/xxxx (xxx.x%): test name ... ok'
            self.stream.write("\r%4d" % n)
            if self.count:
                self.stream.write("/%d (%5.1f%%)"
                                  % (self.count, n * 100.0 / self.count))
            if self.showAll: # self.cfg.verbosity == 1
                self.stream.write(": ")
            elif self.cfg.verbosity:
                name = self.getShortDescription(test)
                width = len(name)
                if width < self._lastWidth:
                    name += " " * (self._lastWidth - width)
                self.stream.write(": %s" % name)
                self._lastWidth = width
            self.stream.flush()
        self.__super_startTest(test)  # increments testsRun by one and prints
        self.testsRun = n # override the testsRun calculation
        for hook in self.hooks:
            hook.startTest(test)

    def stopTest(self, test):
        for hook in self.hooks:
            hook.stopTest(test)
        self.__super_stopTest(test)

    def getDescription(self, test):
        return test.id() # package.module.class.method

    def getShortDescription(self, test):
        s = test.id() # package.module.class.method
        if len(s) > self._maxWidth:
            namelen = len(s.split('.')[-1])
            left = max(0, (self._maxWidth - namelen) / 2 - 1)
            right = self._maxWidth - left - 3
            s = "%s...%s" % (s[:left], s[-right:])
        return s

    def printErrors(self):
        if self.cfg.progress and not (self.dots or self.showAll):
            self.stream.writeln()
        if self.cfg.immediate_errors and (self.errors or self.failures):
            self.stream.writeln(self.separator1)
            self.stream.writeln("Tests that failed")
            self.stream.writeln(self.separator2)
        self.__super_printErrors()

    def formatError(self, err):
        return "".join(format_exception(basedir=self.cfg.basedir, *err))

    def printTraceback(self, kind, test, err):
        self.stream.writeln()
        self.stream.writeln(self.separator1)
        self.stream.writeln("%s: %s" % (kind, self.getDescription(test)))
        self.stream.writeln(self.separator2)
        self.stream.writeln(self.formatError(err))
        self.stream.writeln()

    def addFailure(self, test, err):
        if self.cfg.immediate_errors:
            self.printTraceback("FAIL", test, err)
        if self.cfg.postmortem:
            pdb.post_mortem(sys.exc_info()[2])
        self.failures.append((test, self.formatError(err)))

    def addError(self, test, err):
        if self.cfg.immediate_errors:
            self.printTraceback("ERROR", test, err)
        if self.cfg.postmortem:
            pdb.post_mortem(sys.exc_info()[2])
        self.errors.append((test, self.formatError(err)))

    def printErrorList(self, flavour, errors):
        if self.cfg.immediate_errors:
            for test, err in errors:
                description = self.getDescription(test)
                self.stream.writeln("%s: %s" % (flavour, description))
        else:
            self.__super_printErrorList(flavour, errors)


class CustomTestRunner(unittest.TextTestRunner):
    """Customised TestRunner.

    See CustomisedTextResult for a list of extensions.
    """

    __super = unittest.TextTestRunner
    __super_init = __super.__init__
    __super_run = __super.run

    def __init__(self, cfg, hooks=None, stream=sys.stderr, count=None):
        self.__super_init(verbosity=cfg.verbosity, stream=stream)
        self.cfg = cfg
        if hooks is not None:
            self.hooks = hooks
        else:
            self.hooks = []
        self.count = count

    def run(self, test):
        """Run the given test case or test suite."""
        if self.count is None:
            self.count = test.countTestCases()
        result = self._makeResult()
        startTime = time.time()
        test(result)
        stopTime = time.time()
        timeTaken = float(stopTime - startTime)
        result.printErrors()
        run = result.testsRun
        if not self.cfg.quiet:
            self.stream.writeln(result.separator2)
            self.stream.writeln("Ran %d test%s in %.3fs" %
                                (run, run != 1 and "s" or "", timeTaken))
            self.stream.writeln()
        if not result.wasSuccessful():
            self.stream.write("FAILED (")
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                self.stream.write("failures=%d" % failed)
            if errored:
                if failed: self.stream.write(", ")
                self.stream.write("errors=%d" % errored)
            self.stream.writeln(")")
        elif not self.cfg.quiet:
            self.stream.writeln("OK")
        return result

    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity,
                                cfg=self.cfg, count=self.count,
                                hooks=self.hooks)


def main(argv):
    """Main program."""

    # Environment
    if sys.version_info < (2, 3):
        print >> sys.stderr, '%s: need Python 2.3 or later' % argv[0]
        print >> sys.stderr, 'your python is %s' % sys.version
        return 1

    # Defaults
    cfg = Options()
    cfg.basedir = os.path.join(os.path.dirname(argv[0]), 'src')
    cfg.basedir = os.path.abspath(cfg.basedir)

    # Figure out terminal size
    try:
        import curses
    except ImportError:
        pass
    else:
        try:
            curses.setupterm()
            cols = curses.tigetnum('cols')
            if cols > 0:
                cfg.screen_width = cols
        except curses.error:
            pass

    # Option processing
    try:
        opts, args = getopt.gnu_getopt(argv[1:], 'hvpqufwd',
                               ['list-files', 'list-tests', 'list-hooks',
                                'level=', 'all-levels', 'coverage',
                                'search-in=', 'immediate-errors',
                                'delayed-errors', 'help'])
    except getopt.error, e:
        print >> sys.stderr, '%s: %s' % (argv[0], e)
        print >> sys.stderr, 'run %s -h for help' % argv[0]
        return 1
    for k, v in opts:
        if k in ['-h', '--help']:
            print __doc__
            return 0
        elif k == '-v':
            cfg.verbosity += 1
            cfg.quiet = False
        elif k == '-p':
            cfg.progress = True
            cfg.quiet = False
        elif k == '-q':
            cfg.verbosity = 0
            cfg.progress = False
            cfg.quiet = True
        elif k == '-u':
            cfg.unit_tests = True
        elif k == '-f':
            cfg.functional_tests = True
        elif k == '-d':
            cfg.postmortem = True
        elif k == '-w':
            cfg.warn_omitted = True
        elif k == '--list-files':
            cfg.list_files = True
            cfg.run_tests = False
        elif k == '--list-tests':
            cfg.list_tests = True
            cfg.run_tests = False
        elif k == '--list-hooks':
            cfg.list_hooks = True
            cfg.run_tests = False
        elif k == '--coverage':
            cfg.coverage = True
        elif k == '--level':
            try:
                cfg.level = int(v)
            except ValueError:
                print >> sys.stderr, '%s: invalid level: %s' % (argv[0], v)
                print >> sys.stderr, 'run %s -h for help' % argv[0]
                return 1
        elif k == '--all-levels':
            cfg.level = None
        elif k == '--search-in':
            dir = os.path.abspath(v)
            if not dir.startswith(cfg.basedir):
                print >> sys.stderr, ('%s: argument to --search-in (%s) must'
                                      ' be a subdir of %s'
                                      % (argv[0], v, cfg.basedir))
                return 1
            cfg.search_in += (dir, )
        elif k == '--immediate-errors':
            cfg.immediate_errors = True
        elif k == '--delayed-errors':
            cfg.immediate_errors = False
        else:
            print >> sys.stderr, '%s: invalid option: %s' % (argv[0], k)
            print >> sys.stderr, 'run %s -h for help' % argv[0]
            return 1
    if args:
        cfg.pathname_regex = args[0]
    if len(args) > 1:
        cfg.test_regex = args[1]
    if len(args) > 2:
        print >> sys.stderr, '%s: too many arguments: %s' % (argv[0], args[2])
        print >> sys.stderr, 'run %s -h for help' % argv[0]
        return 1
    if not cfg.unit_tests and not cfg.functional_tests:
        cfg.unit_tests = True

    if not cfg.search_in:
        cfg.search_in = (cfg.basedir, )

    # Do not print "Imported %d modules in %.3fs" if --list-XXX was specified
    if cfg.list_tests or cfg.list_hooks or cfg.list_files:
        cfg.print_import_time = False

    # Set up the python path
    sys.path[0] = cfg.basedir
    # XXX The following bit is SchoolTool specific: we need the Zope3 tree in
    #     sys.path, in addition to basedir.
    sys.path.insert(1, os.path.join(os.path.dirname(cfg.basedir),
                                    'Zope3', 'src'))

    # Set up tracing before we start importing things
    tracer = None
    if cfg.run_tests and cfg.coverage:
        import trace
        # trace.py in Python 2.3.1 is buggy:
        # 1) Despite sys.prefix being in ignoredirs, a lot of system-wide
        #    modules are included in the coverage reports
        # 2) Some module file names do not have the first two characters,
        #    and in general the prefix used seems to be arbitrary
        # These bugs are fixed in src/trace.py which should be in PYTHONPATH
        # before the official one.
        ignoremods = ['test']
        ignoredirs = [sys.prefix, sys.exec_prefix]
        tracer = trace.Trace(count=True, trace=False,
                    ignoremods=ignoremods, ignoredirs=ignoredirs)

    # Finding and importing
    test_files = get_test_files(cfg)
    if cfg.list_tests or cfg.run_tests:
        test_cases = get_test_cases(test_files, cfg, tracer=tracer)
    if cfg.list_hooks or cfg.run_tests:
        test_hooks = get_test_hooks(test_files, cfg, tracer=tracer)

    # Configure the logging module
    import logging
    logging.basicConfig()
    logging.root.setLevel(logging.CRITICAL)

    # Running
    success = True
    if cfg.list_files:
        baselen = len(cfg.basedir) + 1
        print "\n".join([fn[baselen:] for fn in test_files])
    if cfg.list_tests:
        print "\n".join([test.id() for test in test_cases])
    if cfg.list_hooks:
        print "\n".join([str(hook) for hook in test_hooks])
    if cfg.run_tests:
        runner = CustomTestRunner(cfg, test_hooks, count=len(test_cases))
        suite = unittest.TestSuite()
        suite.addTests(test_cases)
        if tracer is not None:
            success = tracer.runfunc(runner.run, suite).wasSuccessful()
            results = tracer.results()
            results.write_results(show_missing=True, coverdir=cfg.coverdir)
        else:
            success = runner.run(suite).wasSuccessful()

    # That's all
    if success:
        return 0
    else:
        return 1


if __name__ == '__main__':
    exitcode = main(sys.argv)
    sys.exit(exitcode)
