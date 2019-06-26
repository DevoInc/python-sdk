import json
import os
import unittest
import types
from time import gmtime, strftime
from devo.api import Client, ClientConfig


class TestApi(unittest.TestCase):
    def setUp(self):
        self.query = 'from demo.ecommerce.data select * limit 1'
        self.app_name = "testing-app_name"
        self.uri = os.getenv('DEVO_API_ADDRESS',
                             'https://apiv2-us.devo.com/search/query')
        self.key = os.getenv('DEVO_API_KEY', None)
        self.secret = os.getenv('DEVO_API_SECRET', None)
        self.token = os.getenv('DEVO_API_TOKEN', None)
        self.query_id = os.getenv('DEVO_API_QUERYID', None)
        self.user = os.getenv('DEVO_API_USER', "python-sdk-user")
        self.comment = os.getenv('DEVO_API_COMMENT', None)

    def test_from_dict(self):
        api = Client(config=
            {'key': self.key, 'secret': self.secret, 'address': self.uri,
             'user': self.user, 'app_name': self.app_name}
            )

        self.assertTrue(isinstance(api, Client))

    def test_query(self):
        config = ClientConfig(stream=False, response="json")

        api = Client(auth={"key": self.key, "secret": self.secret},
                     address=self.uri,
                     config=config)

        result = api.query(query=self.query)
        self.assertIsNotNone(result)
        self.assertTrue(len(json.loads(result)['object']) > 0)

    def test_token(self):
        api = Client(auth={"token": self.token},
                     address=self.uri,
                     config=ClientConfig(stream=False, response="json"))
        result = api.query(query=self.query)
        self.assertIsNotNone(result)
        self.assertTrue(len(json.loads(result)['object']) > 0)

    test_token
    def test_query_id(self):
        api = Client(auth={"key": self.key, "secret": self.secret},
                     address=self.uri,
                     config=ClientConfig(stream=False, response="json"))
        result = api.query(query_id=self.query_id)
        self.assertIsNotNone(result)
        self.assertNotEqual(result, {})
        self.assertEqual(type(len(json.loads(result)['object'])), type(1))

    def test_query_yesterday_to_today(self):
        api = Client(auth={"key": self.key, "secret": self.secret},
                     address=self.uri,
                     config=ClientConfig(stream=False, response="json"))
        result = api.query(query=self.query,
                           dates={'from': 'yesterday()', 'to': 'today()'})
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)

    def test_query_from_seven_days(self):
        api = Client(auth={"key": self.key, "secret": self.secret},
                     address=self.uri,
                     config=ClientConfig(stream=False, response="json"))
        result = api.query(query=self.query,
                           dates={'from': 'now()-7*day()', 'to': 'now()'})
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)

    def test_query_from_fixed_dates(self):
        api = Client(auth={"key": self.key, "secret": self.secret},
                     address=self.uri,
                     config=ClientConfig(stream=False, response="json"))
        result = api.query(query=self.query,
                           dates={'from': strftime("%Y-%m-%d", gmtime()),
                                  'to': strftime(
                                      "%Y-%m-%d %H:%M:%S",
                                      gmtime())})
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)

    def test_stream_query(self):
        api = Client(auth={"key": self.key, "secret": self.secret},
                     address=self.uri,
                     config=ClientConfig(response="json/simple"))
        result = api.query(query=self.query)
        self.assertTrue(isinstance(result, types.GeneratorType))
        result = list(result)
        self.assertEqual(len(result), 1)

    def test_pragmas(self):
        """Test the api when the pragma comment.free is used"""
        api = Client(auth={"key": self.key, "secret": self.secret},
                     address=self.uri,
                     config=ClientConfig(response="json",
                                         stream=False))
        api.config.set_user(user=self.user)
        api.config.set_app_name(app_name=self.app_name)
        result = api.query(query=self.query, comment=self.comment)
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)

    def test_pragmas_not_comment_free(self):
        """Test the api when the pragma comment.free is not used"""
        api = Client(auth={"key": self.key, "secret": self.secret},
                     address=self.uri,
                     config=ClientConfig(response="json",
                                         stream=False))
        api.config.set_user(user=self.user)
        api.config.set_app_name(app_name=self.app_name)
        result = api.query(query=self.query)
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)


if __name__ == '__main__':
    unittest.main()
