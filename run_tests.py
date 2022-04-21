import os
import sys
import unittest
import argparse
from devo.common import load_env_file
from tests.sender.local_servers import SSLServer, TCPServer


def run_test_suite(selected_module):
    def mark_failed():
        nonlocal failed
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

    failed = False
    load_env_file(os.path.abspath(os.getcwd()) + os.sep + "environment.env")
    original_cwd = os.path.abspath(os.getcwd())
    os.chdir('.%stests%s' % (os.sep, os.sep))

    # Run tests for selected module
    if selected_module in ['API_CLI', 'API_QUERY', 'API_TASKS', 'COMMON_CONFIGURATION',
                           'COMMON_DATE_PARSER', 'SENDER_CLI', 'SENDER_NUMBER_LOOKUP',
                           'SENDER_SEND_DATA', 'SENDER_SEND_LOOKUP']:
        dir_paths = {
            'API_CLI': ['api', 'cli.py'],
            'API_QUERY': ['api', 'query.py'],
            'API_TASKS': ['api', 'tasks.py'],
            'COMMON_CONFIGURATION': ['common', 'configuration.py'],
            'COMMON_DATE_PARSER': ['common', 'date_parser.py'],
            'SENDER_CLI': ['sender', 'cli.py'],
            'SENDER_NUMBER_LOOKUP': ['sender', 'number_lookup.py'],
            'SENDER_SEND_DATA': ['sender', 'send_data.py'],
            'SENDER_SEND_LOOKUP': ['sender', 'send_lookup.py']
        }
        configured_path = '.' + os.sep + dir_paths[selected_module][0]
        configured_pattern = dir_paths[selected_module][1]
    else:
        configured_path = '.'
        configured_pattern = '*.py'

    suite = unittest.defaultTestLoader.discover(configured_path,
                                                configured_pattern)

    runner = TrackingTextTestRunner(verbosity=2)
    runner.run(suite)
    os.chdir(original_cwd)

    return failed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage",
                        type=bool,
                        const=True,
                        default=False,
                        nargs='?',
                        help="Generate coverage")
    parser.add_argument("-m",
                        "--module",
                        type=str,
                        const=True,
                        default=None,
                        nargs='?',
                        help="Select a module to test \
        [API_CLI | API_QUERY | API_TASKS | COMMON_CONFIGURATION | COMMON_DATE_PARSER | SENDER_CLI | SENDER_NUMBER_LOOKUP | SENDER_SEND_DATA | SENDER_SEND_LOOKUP]"
                        )
    args = parser.parse_args()
    local_ssl_server = SSLServer()
    local_tcp_server = TCPServer()
    if args.coverage:
        try:
            import coverage
        except ImportError:
            print("Could not import coverage. Please install it and try again.")
            exit(1)
        cov = coverage.coverage(source=['devo'])
        cov.start()
        failed = run_test_suite(args.module)
        cov.stop()
        cov.html_report(directory='coverage_report')
    else:
        failed = run_test_suite(args.module)

    local_ssl_server.close_server()
    local_tcp_server.close_server()
    sys.exit(failed)
