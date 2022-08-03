import time
import unittest
from math import floor
from unittest import mock

from requests import Response

from devo.api import Client
from unittest.mock import MagicMock, Mock


class TimeoutTokenCase(unittest.TestCase):
    def test_json_token_stream(self):
        # As captured from real query
        result = iter([b'    ', b'    ', '{"eventdate":1659537120000,"count":50}', b'    ',
                         '{"eventdate":1659537180000,"count":105}'])

        client = Client(retries=0, config={'address': "URI"})
        client._make_request = MagicMock(return_value=result)
        response = client.query()
        self.assertEqual(50, next(response))
        self.assertEqual(105, next(response))
        self.assertEqual(True, False)  # add assertion here

    def test_json_token_notstream(self):
        result = '    {"msg":"","timestamp":1659539571639,"cid":"a6fe6a6ec8bc","status":0,"object":[{"eventdate":1659539580000,"count":84}  ,{"eventdate":1659539640000,"count":52}]}'

        client = Client(retries=0, config={'address': "URI"})
        client.config.stream=False
        with mock.patch('devo.api.Client._make_request') as patched_make_request:
            patched_make_request.return_value.text = result

            response = client.query()
            self.assertIsNotNone(response)

    def test_query(self):
        client = Client(retries=0, config={'address': "https://apiv2-eu.devo.com/search/query",
                                           'token': '31cf15b73dd232a35a467d44a4723d3b', 'stream': False,
                                           'response': "json"})
        response = client.query(query="from siem.logtrust.web.activity group every 1m select count()",
                                dates={'from': str((floor(time.time()) + 60)*1000), 'to': str((floor(time.time()) + 120)*1000)})
        self.assertIsNotNone(response)

if __name__ == '__main__':
    unittest.main()
