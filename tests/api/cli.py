import unittest
from click.testing import CliRunner
from devo.api.scripts.client_cli import query
from devo.api.client import ERROR_MSGS


class TestApi(unittest.TestCase):
    def setUp(self):
        pass

    def test_query_args(self):
        runner = CliRunner()
        result = runner.invoke(query, [])
        self.assertIn(ERROR_MSGS['no_query'], result.stdout)

    def test_bad_credentials(self):
        runner = CliRunner()
        result = runner.invoke(query, ["--debug",
                                       "--from", "2018-01-01",
                                       "--query", "from demo.ecommerce.data "
                                                  "select timestamp limit 1"])
        self.assertIn(ERROR_MSGS['no_auth'],
                      result.stdout)


if __name__ == '__main__':
    unittest.main()
