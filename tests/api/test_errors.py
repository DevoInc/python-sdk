import unittest
from unittest.mock import MagicMock

import responses
from devo.api import Client, DevoClientException
from devo.api.client import (DEFAULT, NO_KEEPALIVE_TOKEN,
                             SIMPLECOMPACT_TO_ARRAY, SIMPLECOMPACT_TO_OBJ,
                             DevoClientDataResponseException,
                             DevoClientRequestException)


class ErrorManagementCase(unittest.TestCase):
    def _query(self, response_type, result, processor, stream):
        client = Client(
            retries=0,
            config={
                "address": "URI",
                "stream": stream,
                "response": response_type,
                "processor": processor,
            },
        )
        if stream:
            client._make_request = MagicMock(return_value=(None, result, None))
        else:
            client._make_request = MagicMock(return_value=(result, None, None))
        return client.query()

    def _query_mocking_request(self, response_type, result, processor, stream, status):
        client = Client(
            retries=0,
            config={
                "address": "URI",
                "stream": stream,
                "response": response_type,
                "processor": processor,
                "keepAliveToken": NO_KEEPALIVE_TOKEN,
            },
            auth={"token": "TOKEN"},
        )
        responses.add(responses.POST, "https://uri/search/query", body=result, status=status)

        return client.query()

    @responses.activate
    def test_error_ALL_1(self):
        result = (
            '{"timestamp":1669737806151,"cid":"b46bde339628","msg":\n'
            '        "Error Launching Query","status":500,"object":["Error Launching Query"\n'
            '        ,"com.devo.malote.syntax.ParseException: Encountered '
            '\\" \\"not\\" \\"not \\"\\" at line 1, column 17.\\n'
            'Was expecting one of:\\n    <ID> ...\\n    <QID> ...\\n    "]}'
        )
        for stream in [True, False]:
            for response in [
                "json",
                "json/compact",
                "json/simple",
                "json/simple/compact",
                "msgpack",
                "csv",
                "tsv",
                "xls",
            ]:
                if not stream or Client.stream_available(response):
                    processor = SIMPLECOMPACT_TO_ARRAY
                    with self.assertRaises(DevoClientException) as context:
                        response = self._query_mocking_request(
                            response, result, processor, stream, 500
                        )
                        if stream:
                            list(response)
                    self.assertIsInstance(context.exception, DevoClientRequestException)
                    self.assertTrue(context.exception.args[0].startswith("Error Launching Query"))
                    self.assertEqual(500, context.exception.status)
                    self.assertEqual("b46bde339628", context.exception.cid)
                    self.assertEqual(1669737806151, context.exception.timestamp)
                    self.assertEqual(
                        "Error Launching Query: "
                        "com.devo.malote.syntax.ParseException: Encountered"
                        ' " "not" "not "" at line 1, column 17.\nWas'
                        " expecting one of:\n    <ID> ...\n    <QID> ...\n"
                        "    ",
                        context.exception.args[0],
                    )

    @responses.activate
    def test_error_ALL_2(self):
        result = """{"timestamp":1669742043045,"cid":"a41119cc9b2d",
            "error":"server_error","status":500}"""
        for stream in [True, False]:
            for response in [
                "json",
                "json/compact",
                "json/simple",
                "json/simple/compact",
                "msgpack",
                "csv",
                "tsv",
                "xls",
            ]:
                if not stream or Client.stream_available(response):
                    processor = SIMPLECOMPACT_TO_ARRAY
                    with self.assertRaises(DevoClientException) as context:
                        response = self._query_mocking_request(
                            response, result, processor, False, 500
                        )
                        if stream:
                            list(response)
                    self.assertIsInstance(context.exception, DevoClientRequestException)
                    self.assertEqual("server_error", context.exception.message)
                    self.assertEqual(500, context.exception.status)
                    self.assertEqual("a41119cc9b2d", context.exception.cid)
                    self.assertEqual(1669742043045, context.exception.timestamp)
                    self.assertEqual("server_error", context.exception.cause)
                    self.assertEqual("server_error", context.exception.args[0])

    @responses.activate
    def test_error_ALL_3(self):
        result = """{
            "msg": "The table TABLE is not found in the domain DOMAIN",
            "code": 624,
            "timestamp": 1610956615646,
            "cid": "243a25d36cc5",
            "context": {
                "table": "TABLE",
                "domain": "DOMAIN"
            }
        }"""
        for stream in [True, False]:
            for response in [
                "json",
                "json/compact",
                "json/simple",
                "json/simple/compact",
                "msgpack",
                "csv",
                "tsv",
                "xls",
            ]:
                if not stream or Client.stream_available(response):
                    processor = SIMPLECOMPACT_TO_ARRAY
                    with self.assertRaises(DevoClientException) as context:
                        response = self._query_mocking_request(
                            response, result, processor, False, 500
                        )
                        if stream:
                            list(response)
                    self.assertIsInstance(context.exception, DevoClientRequestException)
                    self.assertEqual(
                        "The table TABLE is not found in the domain DOMAIN",
                        context.exception.message,
                    )
                    self.assertEqual(500, context.exception.status)
                    self.assertEqual("243a25d36cc5", context.exception.cid)
                    self.assertEqual(1610956615646, context.exception.timestamp)
                    self.assertEqual(624, context.exception.code)
                    self.assertEqual(
                        {
                            "msg": "The table TABLE is not found in the domain DOMAIN",
                            "code": 624,
                            "timestamp": 1610956615646,
                            "cid": "243a25d36cc5",
                            "context": {"table": "TABLE", "domain": "DOMAIN"},
                        },
                        context.exception.cause,
                    )
                    self.assertEqual(
                        "The table TABLE is not found in the domain DOMAIN",
                        context.exception.args[0],
                    )

    def test_error_stream_json_simple_compact_to_array(self):
        result = iter(
            [
                b'{"m":{"parameters":{"type":"str","index":0}},'
                b'"metadata":[{"name":"parameters","type":"str"}]}',
                b'{"e":[500,"Error Processing Query"]}',
            ]
        )
        response = "json/simple/compact"
        processor = SIMPLECOMPACT_TO_ARRAY

        response = self._query(response, result, processor, True)

        self.assertIsNotNone(response)
        with self.assertRaises(DevoClientException) as context:
            response = list(response)
        self.assertIsInstance(context.exception, DevoClientDataResponseException)
        self.assertIn(
            "Error while receiving query data: Error Processing Query",
            context.exception.message,
        )
        self.assertEqual(500, context.exception.code)
        self.assertEqual('{"e":[500,"Error Processing Query"]}', context.exception.cause)

    def test_error_stream_json_simple_compact_to_obj(self):
        result = iter(
            [
                b'{"m":{"parameters":{"type":"str","index":0}},'
                b'"metadata":[{"name":"parameters","type":"str"}]}',
                b'{"e":[500,"Error Processing Query"]}',
            ]
        )
        response = "json/simple/compact"
        processor = SIMPLECOMPACT_TO_OBJ

        response = self._query(response, result, processor, True)

        self.assertIsNotNone(response)
        with self.assertRaises(DevoClientException) as context:
            response = list(response)
        self.assertIsInstance(context.exception, DevoClientDataResponseException)
        self.assertIn(
            "Error while receiving query data: Error Processing Query",
            context.exception.message,
        )
        self.assertEqual(500, context.exception.code)
        self.assertEqual('{"e":[500,"Error Processing Query"]}', context.exception.cause)

    def test_error_handling_json_simple_stream(self):
        result = iter(
            [
                b'{"eventdate":1519989776059,"level":"INFO","srcPort":48902}',
                b'{"eventdate":1519989778311,"level":"INFO","srcPort":55516}',
                b'{"eventdate":1519989778790,"level":"INFO","srcPort":49206}',
                b'["error",500,"A very bad query error"]',
            ]
        )
        response = "json/simple"
        response = self._query(response, result, DEFAULT, True)

        with self.assertRaises(DevoClientException) as context:
            response = list(response)
        self.assertIsInstance(context.exception, DevoClientDataResponseException)
        self.assertIn(
            "Error while receiving query data: A very bad query error",
            context.exception.message,
        )
        self.assertEqual(500, context.exception.code)
        self.assertEqual('["error",500,"A very bad query error"]', context.exception.cause)

    def test_error_handling_json_simple_compact_stream(self):
        result = iter(
            [
                b'{"m":{"eventdate":{"type":"timestamp","index":0},"level":'
                b'{"type":"str","index":1},"srcPort":{"type":"int4","index":2}}}',
                b'{"d":[1519989516834,"INFO",49756]}',
                b'{"d":[1519989516874,"INFO",51472]}',
                b'{"d":[1519989517774,"INFO",49108]}',
                b'{"e":[500,"A very bad query error"]}',
            ]
        )
        response = "json/simple/compact"
        response = self._query(response, result, DEFAULT, True)

        with self.assertRaises(DevoClientException) as context:
            response = list(response)
        self.assertIsInstance(context.exception, DevoClientDataResponseException)
        self.assertIn(
            "Error while receiving query data: A very bad query error",
            context.exception.message,
        )
        self.assertEqual(500, context.exception.code)
        self.assertEqual('{"e":[500,"A very bad query error"]}', context.exception.cause)

    def test_error_handling_csv_stream(self):
        result = iter(
            [
                b"eventdate,level,srcPort",
                b"2018-03-02 12:25:55.896,INFO,51872",
                b"2018-03-02 12:25:56.378,INFO,51870",
                b"2018-03-02 12:25:58.784,INFO,49282",
                b"devo.api.error,500,A very bad query error",
            ]
        )
        response = "csv"
        response = self._query(response, result, DEFAULT, True)

        with self.assertRaises(DevoClientException) as context:
            response = list(response)
        self.assertIsInstance(context.exception, DevoClientDataResponseException)
        self.assertIn(
            "Error while receiving query data: A very bad query error",
            context.exception.message,
        )
        self.assertEqual(500, context.exception.code)
        self.assertEqual("devo.api.error,500,A very bad query error", context.exception.cause)

    def test_error_handling_tsv_stream(self):
        result = iter(
            [
                b"eventdate  level  srcPort",
                b"2018-03-02 12:26:07.764  INFO  49286",
                b"2018-03-02 12:26:07.765  INFO  49288",
                b"2018-03-02 12:26:10.062  INFO  52230",
                b"devo.api.error  500  A very bad query error",
            ]
        )
        response = "tsv"
        response = self._query(response, result, DEFAULT, True)

        with self.assertRaises(DevoClientException) as context:
            response = list(response)
        self.assertIsInstance(context.exception, DevoClientDataResponseException)
        self.assertIn(
            "Error while receiving query data: A very bad query error",
            context.exception.message,
        )
        self.assertEqual(500, context.exception.code)
        self.assertEqual("devo.api.error  500  A very bad query error", context.exception.cause)

    def test_error_handling_json_no_stream(self):
        result = (
            '{"msg": "","status": 0,"timestamp": 1527781735684,'
            '"cid": "qWw2iXJoT9","object": ['
            '{"eventdate": 1519989592201,"level": "INFO","srcPort": 45850},'
            '{"eventdate": 1519989592313,"level": "INFO","srcPort": 51718}, '
            '{"eventdate": 1519989592335,"level": "INFO","srcPort": 51772}],'
            '"error": [500,"A very bad query error"]}'
        )
        response = "json"

        with self.assertRaises(DevoClientException) as context:
            response = self._query(response, result, DEFAULT, False)
        self.assertIsInstance(context.exception, DevoClientDataResponseException)
        self.assertIn(
            "Error while receiving query data: A very bad query error",
            context.exception.message,
        )
        self.assertEqual(500, context.exception.code)
        self.assertEqual('"error": [500,"A very bad query error"]', context.exception.cause)

    def test_error_handling_json_compact_no_stream(self):
        result = (
            '{"msg": "","status": 0,"object": {"m": '
            '{"eventdate": {"type": "timestamp","index": 0},'
            '"level": {"type": "str","index": 1},'
            '"srcPort": {"type": "int4","index": 2}},'
            '"metadata": ['
            '{"name": "eventdate","type": "timestamp"},'
            '{"name": "level","type": "str"},'
            '{"name": "srcPort","type": "int4"}],'
            '"d": ['
            '[1519989828006, "INFO", 51870],'
            '[1519989828392, "INFO", 51868],'
            '[1519989830837, "INFO", 55514]]},'
            '"e": [500,"A very bad query error"]}}'
        )
        response = "json/compact"

        with self.assertRaises(DevoClientException) as context:
            response = self._query(response, result, DEFAULT, False)
        self.assertIsInstance(context.exception, DevoClientDataResponseException)
        self.assertIn(
            "Error while receiving query data: A very bad query error",
            context.exception.message,
        )
        self.assertEqual(500, context.exception.code)
        self.assertEqual('"e": [500,"A very bad query error"]', context.exception.cause)


if __name__ == "__main__":
    unittest.main()
