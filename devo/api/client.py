# -*- coding: utf-8 -*-
"""Main class for pull data from Devo API (Client)."""
import hmac
import hashlib
import time
import json
import requests
from devo.common import default_from, default_to
from .processors import processors, proc_json, proc_default, \
    json_compact_simple_names, proc_json_compact_simple_to_jobj

CLIENT_DEFAULT_APP_NAME = 'python-sdk-app'
CLIENT_DEFAULT_USER = 'python-sdk-user'
URL_AWS_EU = 'https://apiv2-eu.devo.com'
URL_QUERY_COMPLEMENT = 'search/query'
URL_JOB = '/search/job/'

DEFAULT = "default"
TO_STR = "bytes_to_str"
TO_BYTES = "str_to_bytes"
JSON = "json"
JSON_SIMPLE = "json_simple"
COMPACT_TO_ARRAY = "jsoncompact_to_array"
SIMPLECOMPACT_TO_OBJ = "jsoncompactsimple_to_obj"
SIMPLECOMPACT_TO_ARRAY = "jsoncompactsimple_to_array"

ERROR_MSGS = {
    "no_query": "Error: Not query provided.",
    "no_auth": "Client dont have key&secret or auth token/jwt",
    "no_endpoint": "Endpoint 'url' not found"
}


class DevoClientException(Exception):
    """ Default Devo Client Exception """


def raise_exception(error):
    try:
        if isinstance(error, str):
            raise DevoClientException(proc_json()(error))
        elif isinstance(error, DevoClientException):
            raise DevoClientException(error.args[0])
        elif isinstance(error, dict):
            raise DevoClientException(error)
        else:
            response_text = proc_json()(error.text)
            raise DevoClientException(response_text)
    except json.decoder.JSONDecodeError:
        raise DevoClientException(_format_error(error))


def _format_error(error):
    return '{"msg": "Error Launching Query", "status": 500, ' \
           '"object": "%s"}' % str(error).replace("\"", "\\\"")


class Client:
    """
    The Devo SERach REst Api main class
    """
    def __init__(self, address=None, auth=None, retries=3, timeout=30):
        """
        Initialize the API with this params, all optionals
        :param key: Key string
        :param secret: Secret string
        :param token: Auth Token
        :param url: URL for the service
        :param buffer: Buffer object, if want another diferent queue
        """
        self.auth = auth

        if not address:
            raise raise_exception(
                _format_error(ERROR_MSGS['no_endpoint'])
            )

        self.address = self.__get_address_parts(address)

        self.pragmas = {"user": CLIENT_DEFAULT_USER,
                        "app_name": CLIENT_DEFAULT_APP_NAME}

        self.processor = proc_default()
        self.proc = DEFAULT

        self.retries = retries
        self.timeout = timeout

    def set_user(self, user=CLIENT_DEFAULT_USER):
        self.pragmas['user'] = user
        return True

    def set_app_name(self, app_name=CLIENT_DEFAULT_APP_NAME):
        self.pragmas['app_name'] = app_name
        return True

    @staticmethod
    def from_dict(config):
        """
        Create Client object from config file values
        :param config: lt-common config standar
        """
        return Client(**config)

    def __get_address_parts(self, address):
        """
        Split the two parts of the api url
        :param url: Url of the api
        """
        return \
            self.__verify_address_complement(
                address.split("//")[-1].split("/", maxsplit=1))

    @staticmethod
    def __verify_address_complement(address_list):
        """
        Verify if only has main domain or full url
        :param url_list: One or two part of the url
        """
        return address_list if len(address_list) == 2 \
            else [address_list[0], URL_QUERY_COMPLEMENT]

    @staticmethod
    def _generate_dates(dates):
        """
        Generate and merge dates object
        :param dates: object with options for query, see doc
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
        response = kwargs.get('response', "json/simple/compact")

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
        try:
            first = next(response)
        except StopIteration:
            first = None
        except TypeError:
            raise_exception(response)

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
                response = requests.post("https://{}"
                                         .format("/".join(self.address)),
                                         data=payload,
                                         headers=self._get_headers(payload),
                                         verify=verify, timeout=self.timeout,
                                         stream=stream)
                if response.status_code != 200:
                    raise DevoClientException(response)

                if stream:
                    return response.iter_lines()
                return response
            except requests.exceptions.ConnectionError as error:
                tries += 1
                if tries >= self.retries:
                    return raise_exception(_format_error(error))
                time.sleep(self.timeout)
            except DevoClientException as error:
                if isinstance(error, DevoClientException):
                    raise_exception(error.args[0])
                else:
                    raise_exception(error)
            except Exception as error:
                return raise_exception(_format_error(error))

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
                   "to": int(default_to(dates['to']) / 1000) if dates['to']
                         is not None
                         else None,
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
        if self.auth.get("key", False) and self.auth.get("secret", False):
            sign = self._get_sign(data, tstamp)
            return {
                'Content-Type': 'application/json',
                'x-logtrust-apikey': self.auth.get("key"),
                'x-logtrust-timestamp': tstamp,
                'x-logtrust-sign': sign
            }

        if self.auth.get("token", False):
            return {
                'Content-Type': 'application/json',
                'x-logtrust-timestamp': tstamp,
                'Authorization': "Bearer %s" % self.auth.get("token")
            }

        if self.auth.get("jwt", False):
            return {
                'Content-Type': 'application/json',
                'x-logtrust-timestamp': tstamp,
                'Authorization': "jwt %s" % self.auth.get("jwt")
            }

        raise DevoClientException(_format_error(ERROR_MSGS['no_auth']))

    def _get_sign(self, data, tstamp):
        """
        Generate the sign for the request
        :param data: returned value from _get_payload()
        :param tstamp: Epoch timestamp
        :return: The sign in hex response
        """
        if not self.auth.get("key", False) or self.auth.get("secret", False):
            raise DevoClientException(_format_error("You need a API Key and "
                                                    "API secret to make this"))
        sign = hmac.new(self.auth.get("secret").encode("utf-8"),
                        (self.auth.get("key") + data + tstamp).encode("utf-8"),
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
            .format(self.pragmas['app_name'], self.pragmas['user'])

        if comment:
            return str_pragmas + ' pragma comment.free:"{}"'.format(comment)

        return str_pragmas

    def get_jobs(self, job_type=None, name=None):
        """Get list of jobs by type and name, default All
        :param job_type: category of jobs
        :param name: name of jobs
        :return: json"""
        plus = "" if not job_type \
            else "/{}".format(job_type if not name
                              else "{}/{}".format(job_type, name))

        return self._call_jobs("{}{}{}".format(self.address[0],
                                               '/search/jobs', plus))

    def get_job(self, job_id):
        """Get all info of job
        :param job_id: job id
        :return: json"""
        return self._call_jobs("{}{}{}".format(self.address[0],
                                               URL_JOB, job_id))

    def stop_job(self, job_id):
        """ Stop one job by ID
        :param job_id: id of job
        :return: bool"""
        return self._call_jobs("{}{}{}{}".format(self.address[0], URL_JOB,
                                                 'stop/', job_id))

    def start_job(self, job_id):
        """ Start one job by ID
        :param job_id: id of job
        :return: bool"""
        return self._call_jobs("{}{}{}{}".format(self.address[0], URL_JOB,
                                                 'start/', job_id))

    def remove_job(self, job_id):
        """ Remove one job by ID
        :param job_id: id of job
        :return: bool"""
        return self._call_jobs("{}{}{}{}".format(self.address[0], URL_JOB,
                                                 'remove/', job_id))

    def _call_jobs(self, url):
        """
        Make the call
        :param url: endpoint
        :return: Response from API
        """
        tries = 0
        while tries < self.retries:
            response = None
            try:
                response = requests.get("https://{}".format(url),
                                        headers=self._get_jobs_headers(),
                                        verify=True, timeout=self.timeout)
            except ConnectionError as error:
                raise_exception({"status": 404, "msg": error})

            if response:
                if response.status_code != 200 or\
                        "error" in response.text[0:15].lower():
                    raise_exception(response.text)
                    return None
                try:
                    return json.loads(response.text)
                except json.decoder.JSONDecodeError:
                    return response.text
            tries += 1
            time.sleep(self.timeout)
        return {}

    def _get_jobs_headers(self):
        tstamp = str(int(time.time()) * 1000)
        return {'x-logtrust-timestamp': tstamp,
                'x-logtrust-apikey': self.auth.get("key"),
                'x-logtrust-sign': self._get_sign("", tstamp)
                }
