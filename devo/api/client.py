# -*- coding: utf-8 -*-
"""Main class for pull data from Devo API (Client)."""
import hmac
import hashlib
import time
import json
import socket
import ssl
import requests
import sys
from devo.common import DateParser, Buffer

PY3 = sys.version_info[0] > 2


class DevoClientException(Exception):
    """ Default Devo Client Exception """
    pass


if PY3:
    class ConnectionError(OSError):
        """ Connection error. """
        def __init__(self, *args, **kwargs):  # real signature unknown
            pass


class Client(object):
    """
    The Devo SERach REst Api main class
    """
    URL_AWS_EU = 'https://api-eu.logtrust.com'
    URL_VDC = 'https://spainapi.logtrust.com'
    URL_AWS_USA = 'https://api-us.logtrust.com'
    URL_QUERY_COMPLEMENT = '/search/query'

    def __init__(self, key=None, secret=None, url=None, buffer=None, **kwargs):
        """
        Initialize the API
        :param key: Key string
        :param secret: Secret string
        :param url: URL for the service
        :param buffer: URL for the service
        """
        self.time_start = int(round(time.time() * 1000))
        if key:
            self.key = str(key)
        elif "api_key" in kwargs.keys():
            self.key = str(kwargs['api_key'])
        elif "apiKey" in kwargs.keys():
            self.key = str(kwargs['apiKey'])
        else:
            raise DevoClientException("Devo-Client|No key passed")

        if secret:
            self.secret = str(secret)
        elif "api_secret" in kwargs.keys():
            self.secret = str(kwargs['api_secret'])
        elif "apiSecret" in kwargs.keys():
            self.secret = str(kwargs['apiSecret'])
        else:
            raise DevoClientException("Devo-Client|No secret passed.")

        self.response = "json/simple/compact"
        self.url, self.query_url = self.set_url_query(url)
        self.socket = None
        self.socket_timeout = 30
        self.buffer = buffer
        self.retries = 3
        self.timeout = 30
        self.sleep = 5

    def set_url_query(self, url):
        """
        Set URL to ask
        :param url: string, full or only one part
        :return: Complete url for call api
        """
        if url is None:
            return self.URL_AWS_EU, self.URL_QUERY_COMPLEMENT
        return self.get_url_parts(url)

    def get_url_parts(self, url):
        """
        Split the two parts of the api url
        :param url: Url of the api
        """
        return self.verify_url_complement(url.split("//")[-1]
                                          .split("/", maxsplit=1)
                                          if PY3
                                          else url.split("//")[-1]
                                          .split("/", 1))

    def verify_url_complement(self, url_list):
        """
        Verify if only has main domain or full url
        :param url_list: One or two part of the url
        """
        return url_list if len(url_list) == 2 \
            else [url_list[0], self.URL_QUERY_COMPLEMENT]

    @staticmethod
    def from_config(config):
        """
        Create Client object from config file values
        :param config: lt-common config standar
        """
        return Client(**config)

    @staticmethod
    def generate_dates(dates):
        """
        Generate and merge dates object
        :param dates: object with optios for query, see doc
        :return: updated opts
        """
        default = {'from': 'yesterday()', 'to': None}

        if not dates:
            return default

        default.update(dates)
        return default

    # API Methods
    def query(self, **kwargs):
        """
        Query API by a custom query
        :param kwargs: query -> Query to perform
        :param kwargs: query_id -> Query ID to perform the query
        :param kwargs: dates -> Dict with "from" and "to" keys
        :param kwargs: proccessor -> proccessor for each row of the response,
        if stream
        :param kwargs: stream -> if stream or full response: Object with
        options of query: proccessor, if stream
        :param kwargs: response -> response format
        :return: Result of the query (dict) or Buffer object
        """

        query = kwargs.get('query', None)
        query_id = kwargs.get('query_id', None)
        dates = self.generate_dates(kwargs.get('dates', None))
        stream = kwargs.get('stream', True)
        processor = kwargs.get('processor', None)

        opts = {'limit': kwargs.get('limit', None),
                'response': kwargs.get('response', self.response),
                'offset': kwargs.get('offset', None),
                'destination': kwargs.get('destination', None)}

        if self.stream_available(opts['response']) or not stream:
            return self._call(
                self._get_payload(query, query_id, dates, opts),
                processor
            )
        else:
            if self.socket is None:
                self.connect()

            if self.buffer is None:
                self.buffer = Buffer()

            self.buffer.create_thread(
                target=self._call_stream,
                kwargs=({'payload': self._get_payload(query, query_id,
                                                      dates, opts)})
            )

            self.buffer.start()
            return self.buffer

    @staticmethod
    def stream_available(resp):
        """
        Verify if can stream resp from API by type of resp in opts
        :param resp: str
        :return: bool
        """
        return resp == "json" or resp == "json/compact"

    # API Call
    def _call(self, payload, processor):
        """
        Make the call
        :param payload: The payload
        :param processor: Callback for process returned object/s
        :return: Response from API
        """
        tries = 0
        while tries < self.retries:
            try:
                response = requests.post("https://%s/%s" %
                                         (self.url, self.query_url),
                                         data=payload,
                                         headers=self._get_no_stream_headers(payload),
                                         verify=True, timeout=self.timeout)
            except ConnectionError as error:
                return {"status": 404, "error": error}

            if response:
                if response.status_code != 200 or\
                        "error" in response.text[0:15].lower():
                    return {"status": response.status_code,
                            "error": response.text}
                else:
                    if processor is not None:
                        return processor(response.text)
                    return response.text
            else:
                tries += 1
                time.sleep(self.sleep)
        return {}

    def _call_stream(self, payload=None):
        """
        Make the call
        :param payload: The payload
        """
        self.socket.send(self._get_stream_headers(payload))
        result, data = self.buffer.proccess_first_line(self.socket.recv(5000))
        if result:
            while True:
                self.buffer.proccess_recv(self.socket.recv(5000))
        else:
            raise DevoClientException("Devo-Client|%s" % str(data))

    @staticmethod
    def _get_payload(query, query_id, dates, opts):
        """
        Create the Payload
        :param query: Query string
        :param dates: from -> Date from
        :param dates: to -> Date to
        :param opts: response -> response of the output
        :param opts: limit -> limit of rows for response
        :param opts: offset -> number, set the start of response
        :param opts: destination -> Destination for the results
        :return: Return the formed payload
        """
        payload = {"from": int(DateParser.default_from(dates['from']) / 1000),
                   "to": int(DateParser.default_to(dates['to']) / 1000)
                         if dates['to'] is not None else None,
                   "query": query, "queryId": query_id,
                   "mode": {"type": opts['response']}}

        if query:
            payload['query'] = query

        if query_id:
            payload['queryId'] = query_id

        if opts['limit']:
            payload['limit'] = opts['limit']

        if opts['offset']:
            payload['offset'] = opts['offset']

        if opts["destination"]:
            payload['destination'] = opts['destination']

        return json.dumps(payload)

    def _get_no_stream_headers(self, data):
        """
        Create headers for post call
        :param data: returned value from _get_payload()
        :return: Return the formed http headers
        """
        tstamp = str(int(time.time()) * 1000)
        sign = self._get_sign(data, tstamp)
        return {
            'Content-Type': 'application/json',
            'x-logtrust-apikey': self.key,
            'x-logtrust-timestamp': tstamp,
            'x-logtrust-sign': sign
        }

    def _get_stream_headers(self, payload):
        """
        Create headers for stream query call
        :param payload: returned value from _get_payload()
        :return: Return the formed headers
        """
        tstamp = str(int(time.time()) * 1000)
        return ("POST /%s HTTP/1.1\r\n"
                "Host: %s\r\n"
                "Content-Type: application/json\r\n"
                "Content-Length: %s \r\n"
                "x-logtrust-apikey: %s\r\n"
                "x-logtrust-timestamp: %s\r\n"
                "x-logtrust-sign: %s\r\n"
                "Cache-Control: no-cache\r\n"
                "\r\n"
                "%s\r\n"
                % (self.query_url, self.url, str(len(payload)),
                   self.key, tstamp, self._get_sign(payload, tstamp),
                   payload)).encode("utf-8")

    def _get_sign(self, data, tstamp):
        """
        Generate the sign for the request
        :param data: returned value from _get_payload()
        :param tstamp: Epoch timestamp
        :return: The sign in hex response
        """
        sign = hmac.new(self.secret.encode("utf-8"),
                        (self.key + data + tstamp).encode("utf-8"),
                        hashlib.sha256)
        return sign.hexdigest()

    def connect(self):
        """
        Connect to SSL socket.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.socket_timeout)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            try:
                self.socket = ssl.wrap_socket(self.socket,
                                              cert_reqs=ssl.CERT_NONE)
            except ssl.SSLError:
                raise ssl.SSLError
            self.socket.connect((self.url, 443))
            self.time_start = int(round(time.time() * 1000))

        except socket.error as error:
            self.close()
            raise DevoClientException("Devo-Client| %s" % str(error))

    def close(self):
        """
        Forces socket closure
        """
        if self.socket is not None:
            self.socket.close()
            self.socket = None
