# -*- coding: utf-8 -*-
"""Main class for pull data from Devo API (Client)."""
import hmac
import hashlib
import time
import json
from socket import timeout as socket_timeout
import requests
from devo.common import Buffer, default_from, default_to
from .base import Base, DevoClientException, CLIENT_DEFAULT_USER, \
    CLIENT_DEFAULT_APP_NAME, URL_JOB, URL_JOBS, URL_JOB_START, URL_JOB_STOP, \
    URL_JOB_REMOVE


class Client(Base):
    """
    The Devo SERach REst Api main class
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the API with this params, all optionals
        :param key: Key string
        :param secret: Secret string
        :param token: Auth Token
        :param url: URL for the service
        :param buffer: Buffer object, if want another diferent queue
        """
        Base.__init__(self, *args, **kwargs)
        self.user = kwargs.get('user', CLIENT_DEFAULT_USER)
        self.app_name = kwargs.get('app_name', CLIENT_DEFAULT_APP_NAME)
        self.token = kwargs.get("token",
                                kwargs.get(
                                    "auth_token",
                                    kwargs.get("authToken", None)))

        self.jwt = kwargs.get("jwt", None)

        self.response = "json/simple/compact"
        self.buffer = kwargs.get("buffer", None)

    @staticmethod
    def from_config(config):
        """
        Create Client object from config file values
        :param config: lt-common config standar
        """
        return Client(**config)

    # API Methods
    def query(self, **kwargs):
        """
        Query API by a custom query
        :param kwargs: query -> Query to perform
        :param kwargs: query_id -> Query ID to perform the query
        :param kwargs: dates -> Dict with "from" and "to" keys
        :param kwargs: processor -> processor for each row of the response,
        if stream
        :param kwargs: stream -> if stream or full response: Object with
        options of query: processor, if stream
        :param kwargs: response -> response format
        :return: Result of the query (dict) or Buffer object
        """

        query = kwargs.get('query', None)
        query_id = kwargs.get('query_id', None)
        dates = self._generate_dates(kwargs.get('dates', None))
        stream = kwargs.get('stream', True)
        processor = kwargs.get('processor', None)
        if query is not None:
            query += self._generate_pragmas(comment=kwargs.get('comment', None))

        opts = {'limit': kwargs.get('limit', None),
                'response': kwargs.get('response', self.response),
                'offset': kwargs.get('offset', None),
                'destination': kwargs.get('destination', None)
                }

        if not self._stream_available(opts['response']) or not stream:
            if not dates['to']:
                dates['to'] = "now()"

            return self._call(
                self._get_payload(query, query_id, dates, opts),
                processor
            )

        if self.socket is None:
            self.connect()
        elif not self.status():
            self.connect()

        if self.buffer is None:
            self.buffer = Buffer(api_response=opts['response'])
        self.buffer.create_thread(
            target=self._call_stream,
            kwargs=({'payload': self._get_payload(query, query_id,
                                                  dates, opts)})
        )

        self.buffer.start()
        return self.buffer

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
                response = requests.post(
                    "https://{}/{}".format(self.url, self.query_url),
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

                if processor is not None:
                    return processor(response.text)
                return response.text
            tries += 1
            time.sleep(self.sleep)
        return {}

    def _call_stream(self, payload=None):
        """
        Make the call
        :param payload: The payload
        """
        if self.socket is not None:
            self.socket.send(self._get_stream_headers(payload))
        if not self.buffer.close and not self.buffer.error\
           and self.socket is not None:
            result, data = self.buffer.process_first_line(
                self.socket.recv(4096))
            if result:
                try:
                    while self.buffer.buffering(self.socket.recv(4096)):
                        pass
                except socket_timeout:
                    while not self.buffer.is_empty() or self.buffer.close:
                        time.sleep(1)
            else:
                self.buffer.close = True

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
        payload = {"from": int(default_from(dates['from']) / 1000),
                   "to": int(default_to(dates['to']) / 1000) if
                         dates['to'] is not None else None,
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
        if self.key and self.secret:
            sign = self._get_sign(data, tstamp)
            return {
                'Content-Type': 'application/json',
                'x-logtrust-apikey': self.key,
                'x-logtrust-timestamp': tstamp,
                'x-logtrust-sign': sign
            }

        if self.token:
            return {
                'Content-Type': 'application/json',
                'x-logtrust-timestamp': tstamp,
                'Authorization': "Bearer %s" % self.token
            }

        if self.jwt:
            return {
                'Content-Type': 'application/json',
                'x-logtrust-timestamp': tstamp,
                'Authorization': "jwt %s" % self.jwt
            }

        raise DevoClientException("Devo-Client|Client dont have key&secret"
                                  " or auth token/jwt")

    def _get_stream_headers(self, payload):
        """
        Create headers for stream query call
        :param payload: returned value from _get_payload()
        :return: Return the formed headers
        """
        tstamp = str(int(time.time()) * 1000)

        headers = ("POST /%s HTTP/2.0\r\n"
                   "Host: %s\r\n"
                   "Content-Type: application/json\r\n"
                   "Content-Length: %s \r\n"
                   "Cache-Control: no-cache\r\n"
                   "x-logtrust-timestamp: %s\r\n"
                   % (self.query_url, self.url, str(len(payload)), tstamp))

        if self.key and self.secret:
            return ("%s"
                    "x-logtrust-apikey: %s\r\n"
                    "x-logtrust-sign: %s\r\n"
                    "\r\n%s\r\n"
                    % (headers, self.key, self._get_sign(payload, tstamp),
                       payload)).encode("utf-8")
        if self.token:
            return ("%s"
                    "Authorization: Bearer %s\r\n"
                    "\r\n%s\r\n"
                    % (headers, self.token, payload)).encode("utf-8")
        if self.jwt:
            return ("%s"
                    "Authorization: jwt %s\r\n"
                    "\r\n%s\r\n"
                    % (headers, self.jwt, payload)).encode("utf-8")

        self.buffer.error = "Client dont have key&secret or auth token/jwt"
        raise DevoClientException("Devo-Client|Client dont have key&secret"
                                  " or auth token/jwt")

    def _get_sign(self, data, tstamp):
        """
        Generate the sign for the request
        :param data: returned value from _get_payload()
        :param tstamp: Epoch timestamp
        :return: The sign in hex response
        """
        if not self.secret or not self.key:
            raise DevoClientException("You need a API Key and API "
                                      "secret to make this")
        sign = hmac.new(self.secret.encode("utf-8"),
                        (self.key + data + tstamp).encode("utf-8"),
                        hashlib.sha256)
        return sign.hexdigest()

    def _generate_pragmas(self, comment=None):
        """
        Generate pragmas to add to query
        :comment: Pragma comment free
        :user: Pragma comment user
        :app_name: Pragma comment id. App name.
        """
        str_pragmas = ' pragma comment.id:"{}" ' \
                      'pragma comment.user:"{}"'\
            .format(self.app_name, self.user)

        if comment:
            return str_pragmas + ' pragma comment.free:"{}"'.format(comment)

        return str_pragmas

    def _call_jobs(self, url):
        """
        Make the call
        :param payload: The payload
        :param processor: Callback for process returned object/s
        :return: Response from API
        """
        tries = 0
        while tries < self.retries:
            try:
                response = requests.get("https://{}".format(url),
                                        headers=self._get_jobs_headers(),
                                        verify=True, timeout=self.timeout)
            except ConnectionError as error:
                return {"status": 404, "error": error}

            if response:
                if response.status_code != 200 or\
                        "error" in response.text[0:15].lower():
                    return {"status": response.status_code,
                            "error": response.text}
                try:
                    return json.loads(response.text)
                except json.decoder.JSONDecodeError:
                    return response.text
            tries += 1
            time.sleep(self.sleep)
        return {}

    def _get_jobs_headers(self):
        tstamp = str(int(time.time()) * 1000)

        return {'x-logtrust-timestamp':tstamp,
                'x-logtrust-apikey': self.key,
                'x-logtrust-sign': self._get_sign("", tstamp)
                }

    def get_jobs(self, type=None, name=None):
        """Get list of jobs by type and name, default All
        :param type: category of jobs
        :param name: name of jobs
        :return: json"""
        plus = "" if not type \
            else "/{}".format(type if not name
                              else "{}/{}".format(type, name))

        return self._call_jobs("{}{}{}".format(self.url, URL_JOBS, plus))

    def get_job(self, job_id):
        """Get all info of job
        :param job_id: job id
        :return: json"""
        return self._call_jobs("{}{}{}".format(self.url, URL_JOB, job_id))

    def stop_job(self, job_id):
        """ Stop one job by ID
        :param job_id: id of job
        :return: bool"""
        return self._call_jobs("{}{}{}{}".format(self.url, URL_JOB,
                                                 URL_JOB_STOP, job_id))

    def start_job(self, job_id):
        """ Start one job by ID
        :param job_id: id of job
        :return: bool"""
        return self._call_jobs("{}{}{}{}".format(self.url, URL_JOB,
                                                 URL_JOB_START, job_id))

    def remove_job(self, job_id):
        """ Remove one job by ID
        :param job_id: id of job
        :return: bool"""
        return self._call_jobs("{}{}{}{}".format(self.url, URL_JOB,
                                                 URL_JOB_REMOVE, job_id))
