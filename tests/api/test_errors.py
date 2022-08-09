import unittest

from devo.api import Client
from unittest.mock import MagicMock

from devo.api.client import SIMPLECOMPACT_TO_ARRAY, SIMPLECOMPACT_TO_OBJ


class TimeoutTokenCase(unittest.TestCase):
    def _query_stream(self, response_type, result,
                      processor):
        client = Client(retries=0, config={'address': "URI", "stream": True,
                                           "response": response_type,
                                           "processor": processor})
        client._make_request = MagicMock(return_value=result)
        return client.query()

    def test_error_stream_json_simple_compact_to_array(self):
        result = iter([b'{"m":{"parameters":{"type":"str","index":0}},'
                       b'"metadata":[{"name":"parameters","type":"str"}]}',
                       b'{"e":[500,"Error Processing Query"]}'])
        response = "json/simple/compact"
        processor = SIMPLECOMPACT_TO_ARRAY

        response = self._query_stream(response, result, processor)

        self.assertIsNotNone(response)
        with self.assertRaises(expected_exception=RuntimeError) \
                as context:
            response = list(response)

        self.assertEqual("Error 500 processing query: Error Processing Query",
                         context.exception.args[0])

    def test_error_stream_json_simple_compact_to_obj(self):
        result = iter([b'{"m":{"parameters":{"type":"str","index":0}},'
                       b'"metadata":[{"name":"parameters","type":"str"}]}',
                       b'{"e":[500,"Error Processing Query"]}'])
        response = "json/simple/compact"
        processor = SIMPLECOMPACT_TO_OBJ

        response = self._query_stream(response, result, processor)

        self.assertIsNotNone(response)
        with self.assertRaises(expected_exception=RuntimeError) \
                as context:
            response = list(response)

        self.assertEqual("Error 500 processing query: Error Processing Query",
                         context.exception.args[0])
