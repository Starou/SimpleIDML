import unittest
import os, sys

REGRESSION_TEST_DIRNAME='regressiontests'
REGRESSION_TEST_DIR = os.path.join(os.path.dirname(__file__), REGRESSION_TEST_DIRNAME)

sys.path.insert(0,'../src/')


def load_suite_tests(only=None):
    only_module, only_test_case = None, None
    if only:
        only_module, only_test_case = only.split(".")
    suites = []
    for dirpath, dirnames, filenames in os.walk(REGRESSION_TEST_DIR):
        for f in filenames:
            basename, ext = os.path.splitext(f)
            if (ext == '.py') and (not only_module or (only_module == basename)):
                modname = "%s.%s" % ('.'.join(dirpath.split('/')), basename)
                package = __import__(modname, globals(), locals(), [], -1)
                mod = sys.modules[modname]
                if hasattr(mod, 'suite'):
                    suite = mod.suite()
                    if only_test_case:
                        suite._tests = [t for t in suite._tests if t.__class__.__name__ == only_test_case]
                    suites.append(suite)
    return suites


if __name__ == '__main__':
    only = None
    if len(sys.argv) > 1:
        only = sys.argv[1]
    suites = load_suite_tests(only=only)
    suite = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=2).run(suite)
