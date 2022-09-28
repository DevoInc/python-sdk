import unittest

from devo.api import Client,DevoClientException
from unittest.mock import MagicMock

from devo.api.client import SIMPLECOMPACT_TO_ARRAY, SIMPLECOMPACT_TO_OBJ,DEFAULT


class TimeoutTokenCase(unittest.TestCase):
    def _query(self, response_type, result,
                      processor,stream):
        client = Client(retries=0, config={'address': "URI", "stream": stream,
                                           "response": response_type,
                                           "processor": processor})
        if stream:
            client._make_request = MagicMock(return_value=(None,result,None))
        else:
            client._make_request = MagicMock(return_value=(result,None,None))
        return client.query()
    def test_error_stream_json_simple_compact_to_array(self):
        result = iter([b'{"m":{"parameters":{"type":"str","index":0}},'
                       b'"metadata":[{"name":"parameters","type":"str"}]}',
                       b'{"e":[500,"Error Processing Query"]}'])
        response = "json/simple/compact"
        processor = SIMPLECOMPACT_TO_ARRAY

        response = self._query(response, result, processor,True)

        self.assertIsNotNone(response)
        with self.assertRaises(Exception) as context:
            response = list(response)

        self.assertEqual("('Query lauched reported the following error -----> Error Processing Query', '500')",str(context.exception))

    def test_error_stream_json_simple_compact_to_obj(self):
        result = iter([b'{"m":{"parameters":{"type":"str","index":0}},'
                       b'"metadata":[{"name":"parameters","type":"str"}]}',
                       b'{"e":[500,"Error Processing Query"]}'])
        response = "json/simple/compact"
        processor = SIMPLECOMPACT_TO_OBJ

        response = self._query(response, result, processor,True)

        self.assertIsNotNone(response)
        with self.assertRaises(Exception) as context:
            response = list(response)

        self.assertEqual("('Query lauched reported the following error -----> Error Processing Query', '500')",str(context.exception))

    def test_error_handling_json_simple_stream(self):
        result = iter([b'{"eventdate":1519989776059,"level":"INFO","srcPort":48902}',
                       b'{"eventdate":1519989778311,"level":"INFO","srcPort":55516}',
                       b'{"eventdate":1519989778790,"level":"INFO","srcPort":49206}',
                       b'["error",500,"A very bad query error"]'])
        response = "json/simple"
        response = self._query(response, result, DEFAULT,True)

        with self.assertRaises(Exception) as context:
            response = list(response)

            self.assertEqual("('Query lauched reported the following error -----> A very bad query error', '500')",str(context.exception))

    def test_error_handling_json_simple_compact_stream(self):
        result = iter([b'{"m":{"eventdate":{"type":"timestamp","index":0},"level":{"type":"str","index":1},"srcPort":{"type":"int4","index":2}}}',
                       b'{"d":[1519989516834,"INFO",49756]}',
                       b'{"d":[1519989516874,"INFO",51472]}',
                       b'{"d":[1519989517774,"INFO",49108]}',
                       b'{"e":[500,"A very bad query error"]}'])
        response = "json/simple/compact"
        response = self._query(response, result, DEFAULT,True)

        with self.assertRaises(Exception) as context:
            response = list(response)

            self.assertEqual("('Query lauched reported the following error -----> A very bad query error', '500')",str(context.exception))

    def test_error_handling_csv_stream(self):
        result = iter([b'eventdate,level,srcPort',
                        b'2018-03-02 12:25:55.896,INFO,51872',
                        b'2018-03-02 12:25:56.378,INFO,51870',
                        b'2018-03-02 12:25:58.784,INFO,49282',
                        b'devo.api.error,500,A very bad query error'])
        response = "csv"
        response = self._query(response, result, DEFAULT,True)

        with self.assertRaises(Exception) as context:
            response = list(response)

            self.assertEqual("('Query lauched reported the following error -----> A very bad query error', '500')",str(context.exception))


    def test_error_handling_tsv_stream(self):
        result = iter([b'eventdate  level  srcPort',
                        b'2018-03-02 12:26:07.764  INFO  49286',
                        b'2018-03-02 12:26:07.765  INFO  49288',
                        b'2018-03-02 12:26:10.062  INFO  52230',
                        b'devo.api.error  500  A very bad query error'])
        response = "tsv"
        response = self._query(response, result, DEFAULT,True)

        with self.assertRaises(Exception) as context:
            response = list(response)

            self.assertEqual("('Query lauched reported the following error -----> A very bad query error', '500')",str(context.exception))

    def test_error_handling_json_no_stream(self):

        result = '{"msg": "","status": 0,"timestamp": 1527781735684,"cid": "qWw2iXJoT9","object": [{"eventdate": 1519989592201,"level": "INFO","srcPort": 45850},{"eventdate": 1519989592313,"level": "INFO","srcPort": 51718}, {"eventdate": 1519989592335,"level": "INFO","srcPort": 51772}],"error": [500,"A very bad query error"]}'
        response = "json"

        with self.assertRaises(Exception) as context:
             response = self._query(response, result, DEFAULT,False)

        self.assertIsNotNone(context.exception)     
        self.assertEqual("('Query lauched reported the following error -----> A very bad query error', '500')",str(context.exception))  

    def test_error_handling_json_compact_no_stream(self):

        result = '{"msg": "","status": 0,"object": {"m": {"eventdate": {"type": "timestamp","index": 0},"level": {"type": "str","index": 1},"srcPort": {"type": "int4","index": 2}},"metadata": [{"name": "eventdate","type": "timestamp"},{"name": "level","type": "str"},{"name": "srcPort","type": "int4"}],"d": [[1519989828006, "INFO", 51870],[1519989828392, "INFO", 51868],[1519989830837, "INFO", 55514]]},"e": [500,"A very bad query error"]}}'
        response = "json/compact"

        with self.assertRaises(Exception) as context:
             response = self._query(response, result, DEFAULT,False)
             
        self.assertIsNotNone(context.exception)     
        self.assertEqual("('Query lauched reported the following error -----> A very bad query error', '500')",str(context.exception))
if __name__ == '__main__':
    unittest.main()

