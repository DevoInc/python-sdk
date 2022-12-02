import os
import socket
import sys
import time
import unittest
import argparse
from unittest import TestSuite

from devo.common import load_env_file

from tests.api.cli import TestApi as API_CLI
from tests.api.query import TestApi as API_QUERY
from tests.api.tasks import TestApi as API_TASKS
from tests.api.test_errors import ErrorManagementCase as API_ERRORS
from tests.api.test_parsers_dates import ParserDateCase as API_PARSER_DATE
from tests.api.test_proccesors import TestApi as API_PROCESSORS
from tests.api.test_timeout_token import TimeoutTokenCase as API_KEEPALIVE
from tests.common.configuration import TestConfiguration as COMMON_CONFIGURATION
from tests.common.date_parser import TestDateParser as COMMON_DATE_PARSER
from tests.sender.cli import TestSender as SENDER_CLI
from tests.sender.read_csv import TestCSVRFC as SENDER_CSV
from tests.sender.number_lookup import TestLookup as SENDER_NUMBER_LOOKUP
from tests.sender.send_data import TestSender as SENDER_SEND_DATA
from tests.sender.send_lookup import TestLookup as SENDER_SEND_LOOKUP

from tests.sender.local_servers import SSLServer, TCPServer

module_paths = {
    'API_CLI': API_CLI,
    'API_QUERY': API_QUERY,
    'API_TASKS': API_TASKS,
    'API_ERRORS': API_ERRORS,
    'API_PARSER_DATE': API_PARSER_DATE,
    'API_PROCESSORS': API_PROCESSORS,
    'API_KEEPALIVE': API_KEEPALIVE,
    'COMMON_CONFIGURATION': COMMON_CONFIGURATION,
    'COMMON_DATE_PARSER': COMMON_DATE_PARSER,
    'SENDER_CLI': SENDER_CLI,
    'SENDER_CSV': SENDER_CSV,
    'SENDER_NUMBER_LOOKUP': SENDER_NUMBER_LOOKUP,
    'SENDER_SEND_DATA': SENDER_SEND_DATA,
    'SENDER_SEND_LOOKUP': SENDER_SEND_LOOKUP
}


def run_test_suite(selected_modules, excluded_modules):
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

    if not selected_modules:
        selected_modules = list(module_paths.keys())

    suites = []
    loader = unittest.defaultTestLoader

    # Run tests for selected module and non excluded modules
    for module in selected_modules:
        if module not in excluded_modules:
            print("Loading module %s" % module)
            suites.append(loader.loadTestsFromTestCase(module_paths[module]))

    suite = TestSuite(suites)
    print("Running %d test cases" % suite.countTestCases())

    runner = TrackingTextTestRunner(verbosity=2)
    runner.run(suite)
    os.chdir(original_cwd)

    return failed


def wait_for_ready_server(address, port):
    num_tries = 3

    while num_tries > 0:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((address, port))
            sock.close()
            break
        except socket.error:
            num_tries -= 1
            time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage",
                        type=bool,
                        const=True,
                        default=False,
                        nargs='?',
                        help="Generate coverage")
    parser.add_argument("-m",
                        "--modules",
                        type=str,
                        const=True,
                        default=None,
                        nargs='?',
                        help="Run tests for selected modules: " +
                        ', '.join(module_paths.keys()))
    parser.add_argument("-M",
                        "--exclude-modules",
                        type=str,
                        const=True,
                        default=None,
                        nargs='?',
                        help="Exclude tests for modules: " +
                        ', '.join(module_paths.keys()))

    args = parser.parse_args()

    if args.modules and \
        any([module.strip() not in module_paths.keys()
             for module in args.modules.split(',')]):
        print('Invalid module name in inclussion list.\n\n'
              'Please use one of the following: ' +
              ', '.join(module_paths.keys()))
        sys.exit(1)

    if args.exclude_modules and \
        any([module.strip() not in module_paths.keys()
             for module in args.exclude_modules.split(',')]):
        print('Invalid module name in exclusion list.\n\n'
              'Please use one of the following: ' +
              ', '.join(module_paths.keys()))
        sys.exit(1)


    local_ssl_server = SSLServer()
    local_tcp_server = TCPServer()

    wait_for_ready_server(local_ssl_server.ip, local_ssl_server.port)

    if args.coverage:
        try:
            import coverage
        except ImportError:
            print(
                "Could not import coverage. Please install it and try again.")
            sys.exit(1)
        cov = coverage.coverage(source=['devo'])
        cov.start()
        failed = run_test_suite(args.module)
        cov.stop()
        cov.html_report(directory='coverage_report')
    else:
        failed = run_test_suite(
            [module.strip() for module in args.modules.split(',')]
            if args.modules else [],
            [module.strip() for module in args.exclude_modules.split(',')]
            if args.exclude_modules else [])

    local_ssl_server.close_server()
    local_tcp_server.close_server()
    sys.exit(failed)
