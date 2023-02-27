import os
import tempfile
import unittest

from click.testing import CliRunner
from devo.api.client import ERROR_MSGS, DevoClientException
from devo.api.scripts.client_cli import query
from devo.common import Configuration


class TestApi(unittest.TestCase):

    def setUp(self):
        self.query = 'from siem.logtrust.web.activity select method limit 1'
        self.app_name = "testing-app_name"
        self.uri = os.getenv('DEVO_API_ADDRESS',
                             'https://apiv2-us.devo.com/search/query')
        self.key = os.getenv('DEVO_API_KEY', None)
        self.secret = os.getenv('DEVO_API_SECRET', None)
        self.token = os.getenv('DEVO_AUTH_TOKEN', None)
        self.query_id = os.getenv('DEVO_API_QUERYID', None)
        self.user = os.getenv('DEVO_API_USER', "python-sdk-user")
        self.comment = os.getenv('DEVO_API_COMMENT', None)

        configuration = Configuration()
        configuration.set(
            "api", {
                "query": self.query,
                "address": self.uri,
                "key": self.key,
                "secret": self.secret,
                "token": self.token,
                "query_id": self.query_id,
                "user": self.user,
                "comment": self.comment,
                "app_name": self.app_name
            })

        self.config_path = os.path.join(tempfile.gettempdir(),
                                        "devo_api_tests_config.json")
        configuration.save(path=self.config_path)

    def test_query_args(self):
        runner = CliRunner()
        result = runner.invoke(query, [])
        self.assertIn('Usage: query [OPTIONS]', result.stdout)

    def test_not_credentials(self):
        runner = CliRunner()
        result = runner.invoke(query, [
            "--debug", "--from", "1d", "--query",
            self.query,
            "--address", self.uri
        ])

        self.assertIsInstance(result.exception, DevoClientException)
        self.assertIn(ERROR_MSGS['no_auth'],
                      result.exception.args[0]['cause'])

    def test_bad_url(self):
        runner = CliRunner()
        result = runner.invoke(query, [
            "--debug", "--from", "1d", "--query",
            self.query,
            "--address", "error-apiv2-us.logtrust"
                                                     ".com/search/query",
            "--key", self.key, "--secret", self.secret
        ])
        self.assertIsInstance(result.exception, DevoClientException)
        errorMsg = 'Failed to establish a new connection'
        self.assertIn(errorMsg, result.exception.args[0]['msg'])

    def test_bad_credentials(self):
        runner = CliRunner()
        result = runner.invoke(query, [
            "--debug", "--from", "1d", "--query",
            self.query,
            "--address", self.uri, "--key", "aaa",
            "--secret", self.secret
        ])
        self.assertIsInstance(result.exception, DevoClientException)
        self.assertEqual(result.exception.args[0]['cause']['error']['code'], 12)

    def test_normal_query(self):
        runner = CliRunner()
        result = runner.invoke(query, [
            "--debug", "--from", "1d", "--query",
            self.query,
            "--address", self.uri, "--key",
            self.key, "--secret", self.secret
        ])

        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('{"m":{"method":{"type":"str","index":0',
                      result.output)

    def test_with_config_file(self):
        if self.config_path:
            runner = CliRunner()

            result = runner.invoke(query, [
                "--debug", "--from", "1d", "--query",
                self.query,
                "--config", self.config_path
            ])
            self.assertIsNone(result.exception)
            self.assertEqual(result.exit_code, 0)
            self.assertIn('{"m":{"method":{"type":"str","index":0',
                          result.output)


if __name__ == '__main__':
    unittest.main()
