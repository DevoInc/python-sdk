import json
import os
import unittest
import types
from time import gmtime, strftime
from devo.api import Client


class TestApi(unittest.TestCase):
    def setUp(self):
        self.query = 'from demo.ecommerce.data select * limit 1'
        self.app_name = "testing-app_name"
        self.uri = os.getenv('DEVO_API_URL',
                             'https://api-us.logtrust.com/search/query')
        self.key = os.getenv('DEVO_API_KEY', None)
        self.secret = os.getenv('DEVO_API_SECRET', None)
        self.token = os.getenv('DEVO_AUTH_TOKEN', None)
        self.query_id = os.getenv('DEVO_API_QUERYID', None)
        self.user = os.getenv('DEVO_API_USER', "python-sdk-user")
        self.comment = os.getenv('DEVO_API_COMMENT', None)

    def test_from_config(self):
        api = Client.from_config(
            {'key': self.key, 'secret': self.secret, 'url': self.uri,
             'user': self.user, 'app_name': self.app_name}
            )

        self.assertTrue(isinstance(api, Client))

    def test_query(self):
        api = Client(key=self.key, secret=self.secret, url=self.uri)
        result = api.query(query=self.query, stream=False, response="json")
        self.assertIsNotNone(result)
        self.assertTrue(len(json.loads(result)['object']) > 0)

    def test_token(self):
        api = Client(token=self.token, url=self.uri)
        result = api.query(query=self.query, stream=False, response="json")
        self.assertIsNotNone(result)
        self.assertTrue(len(json.loads(result)['object']) > 0)

    def test_query_id(self):
        api = Client(key=self.key, secret=self.secret, url=self.uri)
        result = api.query(query_id=self.query_id,
                           stream=False, response="json/compact")
        self.assertIsNotNone(result)
        self.assertNotEqual(result, {})
        self.assertEqual(type(len(json.loads(result)['object'])), type(1))

    def test_query_yesterday_to_today(self):
        api = Client(key=self.key, secret=self.secret, url=self.uri)
        result = api.query(query=self.query,
                           dates={'from': 'yesterday()', 'to': 'today()'},
                           stream=False, response="json")
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)

    def test_query_from_seven_days(self):
        api = Client(key=self.key, secret=self.secret, url=self.uri)
        result = api.query(query=self.query,
                           dates={'from': 'now()-7*day()', 'to': 'now()'},
                           stream=False, response="json")
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)

    def test_query_from_fixed_dates(self):
        api = Client(key=self.key, secret=self.secret, url=self.uri)
        result = api.query(query=self.query,
                           dates={'from': strftime("%Y-%m-%d", gmtime()),
                                  'to': strftime(
                                      "%Y-%m-%d %H:%M:%S",
                                      gmtime())},
                           stream=False, response="json")
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)

    def test_stream_query(self):
        api = Client(key=self.key, secret=self.secret, url=self.uri)
        result = api.query(query=self.query, response="json/simple")
        self.assertTrue(isinstance(result, types.GeneratorType))
        result = list(result)
        self.assertEqual(len(result), 1)

    def test_pragmas(self):
        """Test the api when the pragma comment.free is used"""
        api = Client(key=self.key, secret=self.secret, url=self.uri,
                     user=self.user, app_name=self.app_name, stream=False)
        result = api.query(
            query=self.query,
            response="json",
            comment=self.comment)
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)

    def test_pragmas_not_comment_free(self):
        """Test the api when the pragma comment.free is not used"""
        api = Client(key=self.key, secret=self.secret, url=self.uri,
                     user=self.user, app_name=self.app_name, stream=False)
        result = api.query(
            query=self.query,
            response="json")
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)


if __name__ == '__main__':
    unittest.main()
