import unittest
import os
from click.testing import CliRunner
from devo.common import Configuration
from devo.api.scripts.client_cli import query
from devo.api.client import ERROR_MSGS, DevoClientException


class TestApi(unittest.TestCase):
    def setUp(self):
        self.query = 'from demo.ecommerce.data select * limit 1'
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
        configuration.set("api", {
            "query": self.query, "address": self.uri,
            "key": self.key, "secret": self.secret, "token": self.token,
            "query_id": self.query_id, "user": self.user,
            "comment": self.comment, "app_name": self.app_name
        })
        self.config_path = "/tmp/devo_api_tests_config.json"
        configuration.save(path=self.config_path)

    def test_query_args(self):
        runner = CliRunner()
        result = runner.invoke(query, [])
        self.assertIn(ERROR_MSGS['no_endpoint'], result.stdout)

    def test_not_credentials(self):
        runner = CliRunner()
        result = runner.invoke(query, ["--debug",
                                       "--from", "2018-01-01",
                                       "--query", "from demo.ecommerce.data "
                                                  "select timestamp limit 1",
                                       "--address", self.uri])

        self.assertIsInstance(result.exception, DevoClientException)
        self.assertEqual(result.exception.args[0]['status'], 500)
        self.assertIn(ERROR_MSGS['no_auth'],
                      result.exception.args[0]['object'])

    def test_bad_url(self):
        runner = CliRunner()
        result = runner.invoke(query, ["--debug",
                                       "--from", "2018-01-01",
                                       "--query", "from demo.ecommerce.data "
                                                  "select timestamp limit 1",
                                       "--address", "error-apiv2-us.logtrust"
                                                ".com/search/query",
                                       "--key", self.key,
                                       "--secret", self.secret])
        self.assertIsInstance(result.exception, DevoClientException)
        self.assertEqual(result.exception.args[0]['status'], 500)

    def test_bad_credentials(self):
        runner = CliRunner()
        result = runner.invoke(query, ["--debug",
                                       "--from", "2018-01-01",
                                       "--query", "from demo.ecommerce.data "
                                                  "select timestamp limit 1",
                                       "--address", self.uri,
                                       "--key", "aaa",
                                       "--secret", self.secret])

        self.assertIsInstance(result.exception, DevoClientException)
        self.assertEqual(result.exception.args[0]['status'], 401)

    def test_normal_query(self):
        runner = CliRunner()
        result = runner.invoke(query, ["--debug",
                                       "--from", "2018-01-01",
                                       "--query", "from demo.ecommerce.data "
                                                  "select timestamp limit 1",
                                       "--address", self.uri,
                                       "--key", self.key,
                                       "--secret", self.secret])

        self.assertIsNone(result.exception)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('{"m":{"timestamp":{"type":"str","index":0',
                      result.output)

    def test_with_config_file(self):
        if self.config_path:
            runner = CliRunner()
            result = runner.invoke(query, ["--debug",
                                           "--from", "2018-01-01",
                                           "--query",
                                           "from demo.ecommerce.data "
                                           "select timestamp limit 1",
                                           "--config", self.config_path])

            self.assertIsNone(result.exception)
            self.assertEqual(result.exit_code, 0)
            self.assertIn('{"m":{"timestamp":{"type":"str","index":0',
                          result.output)


if __name__ == '__main__':
    unittest.main()
