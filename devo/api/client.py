# -*- coding: utf-8 -*-
"""Main class for pull data from Devo API (Client)."""
import hmac
import hashlib
import time
import json
import requests
from devo.common import default_from, default_to
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
        if stream
        :param kwargs: stream -> if stream or full response
        :param kwargs: response -> response format
        :return: Result of the query (dict) or Buffer object
        """

        query = kwargs.get('query', None)
        query_id = kwargs.get('query_id', None)
        dates = self._generate_dates(kwargs.get('dates', None))
        stream = kwargs.get('stream', True)
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
            stream = False

        return self._call(
            self._get_payload(query, query_id, dates, opts),
            stream
        )

    def _make_request(self, payload, stream):
        """
        Make the request and control the logic about retries if not internet
        :param payload: item with headers for request
        :param stream: boolean, indicate if one call is a streaming call
        :return: response
        """
        tries = 0
        while tries < self.retries:
            try:
                response = requests.post(
                                "https://{}/{}".format(self.url,
                                                       self.query_url),
                                data=payload,
                                headers=self._get_headers(payload),
                                verify=True, timeout=self.timeout,
                                stream=stream)
                if stream:
                    return response.iter_lines()
                return response
            except Exception as error:
                if isinstance(error, requests.exceptions.ConnectionError):
                    tries += 1
                    if tries >= self.retries:
                        return self._format_error(error)
                    time.sleep(self.sleep)
                else:
                    return self._format_error(error)

    def _return_stream(self, payload, stream):
        """If its a stream call, return yield lines
        :param payload: item with headers for request
        :param stream: boolean, indicate if one call is a streaming call
        :return line: yield-generator item
        """
        response = self._make_request(payload, stream)

        if isinstance(response, str):
            yield json.loads(response)
        else:
            first = next(response)
            if self._is_correct_response(first):
                yield first.strip()
                for line in response:
                    yield line.strip()
            else:
                if isinstance(first, bytes):
                    first = first.decode("utf-8")
                yield json.loads(first)

    def _call(self, payload, stream):
        """
        Make the call, select correct item to return
        :param payload: item with headers for request
        :param stream: boolean, indicate if one call is a streaming call
        :return: Response from API
        """
        if stream:
            return self._return_stream(payload, stream)
        else:
            response = self._make_request(payload, stream)
            if isinstance(response, str):
                return json.loads(response)
            return response.text

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

    def _get_headers(self, data):
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
        :param url: endpoint
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

        return {'x-logtrust-timestamp': tstamp,
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
