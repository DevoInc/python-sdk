import os
import sys
import unittest
import argparse
from devo.common import load_env_file
from tests.sender.local_servers import ssl_server, tcp_server

failed = False


def run_test_suite():
    def mark_failed():
        global failed
        failed = True

    class _TrackingTextTestResult(unittest._TextTestResult):
        def addError(self, test, err):
            unittest._TextTestResult.addError(self, test, err)
            mark_failed()

        def addFailure(self, test, err):
            unittest._TextTestResult.addFailure(self, test, err)
            mark_failed()

    class TrackingTextTestRunner(unittest.TextTestRunner):
        def _makeResult(self):
            return _TrackingTextTestResult(
                self.stream, self.descriptions, self.verbosity)

    load_env_file(os.path.abspath(os.getcwd()) + os.sep + "environment.env")
    original_cwd = os.path.abspath(os.getcwd())
    os.chdir('.%stests%s' % (os.sep, os.sep))
    suite = unittest.defaultTestLoader.discover('.', pattern="*.py")
    runner = TrackingTextTestRunner(verbosity=2)
    runner.run(suite)
    os.chdir(original_cwd)

    return failed


class CoverageCommand():
    """setup.py command to run code coverage of the test suite."""
    def run(self):
        try:
            import coverage
        except ImportError:
            print("Could not import coverage. Please install it and try again.")
            exit(1)
        cov = coverage.coverage(source=['devo'])
        cov.start()
        run_test_suite()
        cov.stop()
        cov.html_report(directory='coverage_report')


class TestCommand():
    def run(self):
        """setup.py command to run the whole test suite."""
        failed = run_test_suite()
        if failed:
            sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=bool, const=True,
                        default=False, nargs='?', help="Generate coverage.")
    args = parser.parse_args()
    local_ssl_server = ssl_server()
    local_tcp_server = tcp_server()
    if args.coverage:
        CoverageCommand().run()
    else:
        TestCommand().run()

    local_ssl_server.close_server()
    local_tcp_server.close_server()
