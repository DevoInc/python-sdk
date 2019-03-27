# -*- coding: utf-8 -*-
"""Main class for pull data from Devo API (Client)."""
import hmac
import hashlib
import time
import json
import sys
import requests
from devo.common import default_from, default_to
from .processors import processors, proc_json, proc_default, \
    json_compact_simple_names, proc_json_compact_simple_to_jobj

PY3 = sys.version_info[0] > 2
CLIENT_DEFAULT_APP_NAME = 'python-sdk-app'
CLIENT_DEFAULT_USER = 'python-sdk-user'
URL_AWS_EU = 'https://api-eu.devo.com'
URL_VDC = 'https://api-es.devo.com'
URL_AWS_USA = 'https://api-us.devo.com'
URL_QUERY_COMPLEMENT = 'search/query'
URL_JOB = '/search/job/'
URL_JOBS = '/search/jobs'
URL_JOB_START = 'start/'
URL_JOB_STOP = 'stop/'
URL_JOB_REMOVE = 'remove/'

DEFAULT = "default"
TO_STR = "bytes_to_str"
TO_BYTES = "str_to_bytes"
JSON = "json"
JSON_SIMPLE = "json_simple"
COMPACT_TO_ARRAY = "jsoncompact_to_array"
SIMPLECOMPACT_TO_OBJ = "jsoncompactsimple_to_obj"
SIMPLECOMPACT_TO_ARRAY = "jsoncompactsimple_to_array"


class DevoClientException(Exception):
    """ Default Devo Client Exception """


if not PY3:
    class ConnectionError(OSError):
        """ Connection error. """
        def __init__(self, *args, **kwargs):  # real signature unknown
            pass


class Client:
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
        self.time_start = int(round(time.time() * 1000))
        if len(args) == 3:
            self.key = args[0]
            self.secret = args[1]
            self.url = args[2]
        elif not args:
            self.key = kwargs.get("key",
                                  kwargs.get("api_key",
                                             kwargs.get("apiKey", None)))

            self.secret = kwargs.get("secret",
                                     kwargs.get("api_secret",
                                                kwargs.get("apiSecret", None)))

            self.url = kwargs.get("url", None)
        else:
            raise DevoClientException("Devo-Client|Position arguments are "
                                      "deprecated, It is only enabled as "
                                      "compatibility, being able to pass only "
                                      "3 arguments: key, secret and url, "
                                      "in that order. ")

        self.user = kwargs.get('user', CLIENT_DEFAULT_USER)
        self.app_name = kwargs.get('app_name', CLIENT_DEFAULT_APP_NAME)
        self.token = kwargs.get("token",
                                kwargs.get(
                                    "auth_token",
                                    kwargs.get("authToken", None)))

        self.jwt = kwargs.get("jwt", None)
        self.response = "json/simple/compact"
        self.processor = proc_default()
        self.proc = DEFAULT

        self.url, self.query_url = self.__set_url_query()
        self.retries = 3
        self.timeout = 30
        self.sleep = 5

    @staticmethod
    def from_config(config):
        """
        Create Client object from config file values
        :param config: lt-common config standar
        """
        return Client(**config)

    def __set_url_query(self):
        """
        Set URL to ask
        :param url: string, full or only one part
        :return: Complete url for call api
        """
        if self.url is None:
            return URL_AWS_EU, URL_QUERY_COMPLEMENT
        return self.__get_url_parts()

    def __get_url_parts(self):
        """
        Split the two parts of the api url
        :param url: Url of the api
        """
        return self.__verify_url_complement(
            self.url.split("//")[-1].split("/", maxsplit=1) if PY3
            else self.url.split("//")[-1].split("/", 1))

    @staticmethod
    def __verify_url_complement(url_list):
        """
        Verify if only has main domain or full url
        :param url_list: One or two part of the url
        """
        return url_list if len(url_list) == 2 \
            else [url_list[0], URL_QUERY_COMPLEMENT]

    @staticmethod
    def _generate_dates(dates):
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

    @staticmethod
    def stream_available(resp):
        """
        Verify if can stream resp from API by type of resp in opts
        :param resp: str
        :return: bool
        """
        return resp not in ["json", "json/compact"]

    @staticmethod
    def _format_error(error):
        return '{"msg": "Error Launching Query", "status": 500, ' \
               '"object": "%s"}' % str(error).replace("\"", "\\\"")

    @staticmethod
    def _is_correct_response(line):
        try:
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            if "error" in line[:15].lower():
                return False
            return True
        except ValueError:
            return False

    def query(self, **kwargs):
        """
        Query API by a custom query
        :param kwargs: query -> Query to perform
        :param kwargs: query_id -> Query ID to perform the query
        :param kwargs: dates -> Dict with "from" and "to" keys
        if stream
        :param kwargs: stream -> if stream or full response
        :param kwargs: response -> response format
        :param kwargs: verify -> (optional) Either a boolean, in which case
         it controls whether we verify
         the server's TLS certificate, or a string, in which case it must be
         a path to a CA bundle to use. Defaults to ``True``.
        :return: Result of the query (dict) or Buffer object
        """

        query = kwargs.get('query', None)
        query_id = kwargs.get('query_id', None)
        dates = self._generate_dates(kwargs.get('dates', None))
        stream = kwargs.get('stream', True)

        processor = kwargs.get('processor', None)
        response = kwargs.get('response', self.response)

        if not processor or \
                (response == "csv" and processor not in (TO_STR, TO_BYTES)):
            self.proc = DEFAULT
        else:
            self.proc = processor

        self.processor = processors()[self.proc]()

        if query is not None:
            query += self._generate_pragmas(comment=kwargs.get('comment', None))

        opts = {'limit': kwargs.get('limit', None),
                'response': response,
                'offset': kwargs.get('offset', None),
                'destination': kwargs.get('destination', None)
                }

        if not self.stream_available(opts['response']) or not stream:
            if not dates['to']:
                dates['to'] = "now()"
            stream = False

        return self._call(
            self._get_payload(query, query_id, dates, opts),
            stream, kwargs.get('verify', True)
        )

    def _call(self, payload, stream, verify):
        """
        Make the call, select correct item to return
        :param payload: item with headers for request
        :param stream: boolean, indicate if one call is a streaming call
        :return: Response from API
        """
        if stream:
            return self._return_stream(payload, stream, verify)

        response = self._make_request(payload, stream, verify)
        if isinstance(response, str):
            return proc_json()(response)
        return self.processor(response.text)

    def _return_stream(self, payload, stream, verify):
        """If its a stream call, return yield lines
        :param payload: item with headers for request
        :param stream: boolean, indicate if one call is a streaming call
        :return line: yield-generator item
        """
        response = self._make_request(payload, stream, verify)

        if isinstance(response, str):
            yield proc_json()(response)
        else:
            first = next(response)
            if self._is_correct_response(first):
                if self.proc == SIMPLECOMPACT_TO_OBJ:
                    aux = json_compact_simple_names(proc_json()(first)['m'])
                    self.processor = proc_json_compact_simple_to_jobj(aux)
                elif self.proc == SIMPLECOMPACT_TO_ARRAY:
                    pass
                else:
                    yield self.processor(first)
                for line in response:
                    yield self.processor(line)
            else:
                yield proc_json()(first)

    def _make_request(self, payload, stream, verify):
        """
        Make the request and control the logic about retries if not internet
        :param payload: item with headers for request
        :param stream: boolean, indicate if one call is a streaming call
        :return: response
        """
        tries = 0
        while tries < self.retries:
            try:
                response = requests.post("https://{}/{}".format(self.url,
                                                                self.query_url),
                                         data=payload,
                                         headers=self._get_headers(payload),
                                         verify=verify, timeout=self.timeout,
                                         stream=stream)
                if response.status_code != 200:
                    return response

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
