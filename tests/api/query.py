from time import gmtime, strftime
import unittest
import os
import json
from devo.api import Client
from devo.common import Buffer


class TestApi(unittest.TestCase):
    def setUp(self):
        self.query = 'from demo.ecommerce.data select * limit 1'
        self.uri = os.getenv('DEVO_API_URL',
                             'https://api-us.logtrust.com/search/query')
        self.key = os.getenv('DEVO_API_KEY', None)
        self.secret = os.getenv('DEVO_API_SECRET', None)
        self.token = os.getenv('DEVO_API_TOKEN', None)
        self.query_id = os.getenv('DEVO_API_QUERYID', None)

    def test_query(self):
        api = Client(self.key, self.secret, self.uri)
        result = api.query(query=self.query, stream=False, response="json")
        self.assertIsNotNone(result)
        self.assertTrue(len(json.loads(result)['object']) > 0)
        api.close()

    def test_query_id(self):
        api = Client(self.key, self.secret, self.uri)
        result = api.query(query_id=self.query_id,
                              stream=False, response="json")
        self.assertIsNotNone(result)
        self.assertNotEquals(result, {})
        self.assertEqual(type(len(json.loads(result)['object'])), type(1))
        api.close()

    def test_query_yesterday_to_today(self):
        api = Client(self.key, self.secret, self.uri)
        result = api.query(query=self.query, dates={'from': 'yesterday()', 'to':'today()'},
                           stream=False, response="json")
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)

    def test_query_from_seven_days(self):
        api = Client(self.key, self.secret, self.uri)
        result = api.query(query=self.query, dates={'from': 'now()-7*day()', 'to':'now()'},
                           stream=False, response="json")
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)

    def test_query_from_fixed_dates(self):
        api = Client(self.key, self.secret, self.uri)
        result = api.query(query=self.query,
                           dates={'from': strftime("%Y-%m-%d", gmtime()),
                                 'to': strftime("%Y-%m-%d %H:%M:%S", gmtime())},
                           stream=False, response="json")
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)['object']), 1)

    def test_stream_query(self):
        api = Client(self.key, self.secret, self.uri)
        result = api.query(query=self.query, response="json/simple")
        self.assertTrue(isinstance(result, Buffer))
        api.close()


if __name__ == '__main__':
    unittest.main()
