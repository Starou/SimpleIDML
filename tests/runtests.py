import os
import sys
import unittest

PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PACKAGE_DIR, 'src')
TESTS_DIR = os.path.join(PACKAGE_DIR, 'tests')
REGRESSION_TEST_DIR = os.path.join(TESTS_DIR, 'regressiontests')

sys.path.insert(0, SRC_DIR)


def load_suite_tests(only=None):
    only_module, only_test_case = None, None
    if only:
        args = only.split(".")
        only_module = args[0]
        only_test_case = args[1:] and args[1] or None
        only_function = args[2:] and args[2] or None
    suites = []
    for dirpath, dirnames, filenames in os.walk(REGRESSION_TEST_DIR):
        for f in filenames:
            basename, ext = os.path.splitext(f)
            rel_path = dirpath[len(os.path.dirname(REGRESSION_TEST_DIR)) + 1:]
            if (ext == '.py') and (not only_module or (only_module == basename)):
                modname = '.'.join(rel_path.split('/') + [basename])
                package = __import__(modname, globals(), locals(), [], 0)
                mod = sys.modules[modname]
                if hasattr(mod, 'suite'):
                    suite = mod.suite()
                    if only_test_case:
                        suite._tests = [t for t in suite._tests
                                        if t.__class__.__name__ == only_test_case]
                        if only_function:
                            suite._tests = [t for t in suite._tests
                                            if t._testMethodName == only_function]
                    suites.append(suite)
    return suites


if __name__ == '__main__':
    only = None
    if len(sys.argv) > 1:
        only = sys.argv[1]
    suites = load_suite_tests(only=only)
    suite = unittest.TestSuite(suites)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
