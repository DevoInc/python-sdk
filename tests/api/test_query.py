import json
import os
import types
import unittest
from time import gmtime, strftime

import stopit

from devo.api import Client, ClientConfig, DevoClientException


class TestApi(unittest.TestCase):
    def setUp(self):
        self.query = os.getenv(
            "DEVO_API_QUERY", "from siem.logtrust.web.activity select " "method limit 1"
        )
        self.query_no_results = (
            'from siem.logtrust.web.activity where method = "OTHER" select'
            " method limit 1"
        )
        self.app_name = "testing-app_name"
        self.uri = os.getenv(
            "DEVO_API_ADDRESS", "https://apiv2-us.devo.com/search/query"
        )
        self.key = os.getenv("DEVO_API_KEY", None)
        self.secret = os.getenv("DEVO_API_SECRET", None)
        self.token = os.getenv("DEVO_API_TOKEN", None)
        self.query_id = os.getenv("DEVO_API_QUERYID", None)
        self.user = os.getenv("DEVO_API_USER", "python-sdk-user")
        self.comment = os.getenv("DEVO_API_COMMENT", None)

    def test_from_dict(self):
        api = Client(
            config={
                "key": self.key,
                "secret": self.secret,
                "address": self.uri,
                "user": self.user,
                "app_name": self.app_name,
            }
        )

        self.assertTrue(isinstance(api, Client))

    def test_query(self):
        config = ClientConfig(stream=False, response="json")

        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=config,
            retries=3,
        )

        result = api.query(query=self.query)
        self.assertIsNotNone(result)
        self.assertTrue(len(json.loads(result)["object"]) > 0)

    def test_token(self):
        api = Client(
            auth={"token": self.token},
            address=self.uri,
            config=ClientConfig(stream=False, response="json"),
            retries=3,
        )
        result = api.query(query=self.query)
        self.assertIsNotNone(result)
        self.assertTrue(len(json.loads(result)["object"]) > 0)

    def test_query_id(self):
        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(stream=False, response="json"),
            retries=5,
        )
        result = api.query(query_id=self.query_id)
        self.assertIsNotNone(result)
        self.assertNotEqual(result, {})
        self.assertEqual(type(len(json.loads(result)["object"])), type(1))

    def test_query_yesterday_to_today(self):
        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(stream=False, response="json"),
            retries=3,
        )
        result = api.query(
            query=self.query, dates={"from": "yesterday()", "to": "today()"}
        )
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)["object"]), 1)

    def test_query_from_seven_days(self):
        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(stream=False, response="json"),
            retries=3,
        )
        result = api.query(
            query=self.query, dates={"from": "now()-7*day()", "to": "now()"}
        )
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)["object"]), 1)

    def test_query_from_fixed_dates(self):
        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(stream=False, response="json"),
            retries=3,
        )
        result = api.query(
            query=self.query,
            dates={
                "from": strftime("%Y-%m-%d", gmtime()),
                "to": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            },
        )
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)["object"]), 1)

    def test_stream_query(self):
        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(response="json/simple"),
            retries=3,
        )
        result = api.query(query=self.query)
        self.assertTrue(isinstance(result, types.GeneratorType))
        result = list(result)
        self.assertEqual(len(result), 1)

    def test_stream_query_no_results_bounded_dates(self):
        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(response="json/simple"),
            retries=3,
        )
        result = api.query(
            query=self.query_no_results, dates={"from": "1h", "to": "now()"}
        )
        self.assertTrue(isinstance(result, types.GeneratorType))
        result = list(result)
        self.assertEqual(len(result), 0)

    def test_stream_query_no_results_unbounded_dates(self):
        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(response="json/simple"),
            retries=3,
        )
        result = api.query(query=self.query_no_results)
        self.assertTrue(isinstance(result, types.GeneratorType))
        try:
            with stopit.ThreadingTimeout(3) as to_ctx_mgr:
                result = list(result)
        except DevoClientException:
            # This exception is sent because
            # devo.api.client.Client._make_request catches the
            # stopit.TimeoutException, but the latter is not
            # wrapped, so we cannot obtain it from here.
            self.assertEqual(to_ctx_mgr.state, to_ctx_mgr.TIMED_OUT)

    def test_pragmas(self):
        """Test the api when the pragma comment.free is used"""
        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(response="json", stream=False),
            retries=3,
        )
        api.config.set_user(user=self.user)
        api.config.set_app_name(app_name=self.app_name)
        result = api.query(query=self.query, comment=self.comment)
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)["object"]), 1)

    def test_pragmas_not_comment_free(self):
        """Test the api when the pragma comment.free is not used"""
        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(response="json", stream=False),
            retries=3,
        )
        api.config.set_user(user=self.user)
        api.config.set_app_name(app_name=self.app_name)
        result = api.query(query=self.query)
        self.assertIsNotNone(result)
        self.assertEqual(len(json.loads(result)["object"]), 1)

    @unittest.skip("This is an internal functionality, not intended for external use")
    def test_unsecure_http_query(self):
        """
        This test is intended for checking unsecure HTTP requests. Devo will
        NEVER provide an unsecure HTTP endpoint for API REST services.
        Therefore, you are not going to need to use or test this functionality.
        In order to enable UNSECURE_HTTP environment var should be TRUE.
        The endpoint is served by https://httpbin.org/. You can run with
        `docker run -p 80:80 kennethreitz/httpbin`. It will expose an HTTP
        service at port 80.
        The URL `http://localhost:80/anything` will answer with the content of
        the request.
        """
        os.environ["UNSECURE_HTTP"] = "TRUE"
        config = ClientConfig(stream=False, response="json")

        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address="localhost:80/anything",
            config=config,
            retries=3,
        )

        result = api.query(query=self.query)
        self.assertIsNotNone(result)
        self.assertIn("json", json.loads(result))
        self.assertIn("query", json.loads(result)["json"])

    def test_stream_mode_not_supported_xls(self):
        """Test the api stream mode is not supported for xls format"""

        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(response="xls"),
        )

        stremaAvailable = Client.stream_available(api.config.response)
        self.assertIsNotNone(stremaAvailable)
        self.assertEqual(stremaAvailable, False)

    def test_stream_mode_not_supported_json(self):
        """Test the api stream mode is not supported for json format"""

        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(response="json"),
        )

        stremaAvailable = Client.stream_available(api.config.response)
        self.assertIsNotNone(stremaAvailable)
        self.assertEqual(stremaAvailable, False)

    def test_stream_mode_not_supported_json_compact(self):
        """Test the api stream mode is not supported for json/compact format"""

        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(response="json/compact"),
        )

        stremaAvailable = Client.stream_available(api.config.response)
        self.assertIsNotNone(stremaAvailable)
        self.assertEqual(stremaAvailable, False)

    def test_stream_mode_not_supported_msgpack(self):
        """Test the api stream mode is not supported for msgpack format"""

        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(response="msgpack"),
        )

        stremaAvailable = Client.stream_available(api.config.response)
        self.assertIsNotNone(stremaAvailable)
        self.assertEqual(stremaAvailable, False)

    def test_xls_future_queries(self):
        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(stream=False, response="xls"),
        )

        with self.assertRaises(Exception) as context:
            _ = api.query(
                query=self.query, dates={"from": "now()", "to": "now()+60*second()"}
            )

        self.assertIsInstance(context.exception, DevoClientException)
        self.assertEqual(
            context.exception.args[0],
            "Modes 'xls' and 'msgpack' does not support future"
            " queries because KeepAlive tokens are not available"
            " for those resonses type",
        )

    def test_msgpack_future_queries(self):
        api = Client(
            auth={"key": self.key, "secret": self.secret},
            address=self.uri,
            config=ClientConfig(stream=False, response="msgpack"),
        )

        with self.assertRaises(Exception) as context:
            _ = api.query(
                query=self.query, dates={"from": "now()", "to": "now()+60*second()"}
            )

        self.assertIsInstance(context.exception, DevoClientException)
        self.assertEqual(
            context.exception.args[0],
            "Modes 'xls' and 'msgpack' does not support future "
            "queries because KeepAlive tokens are not available "
            "for those resonses type",
        )


if __name__ == "__main__":
    unittest.main()
