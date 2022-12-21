# -*- coding: utf-8 -*-
"""Main class for pull data from Devo API (Client)."""
import hmac
import hashlib
import logging
import os
import re
import time
import json
import requests
from devo.common import default_from, default_to
from .processors import processors, proc_json, \
    json_compact_simple_names, proc_json_compact_simple_to_jobj
import calendar
from datetime import datetime, timedelta
import pytz


CLIENT_DEFAULT_APP_NAME = 'python-sdk-app'
CLIENT_DEFAULT_USER = 'python-sdk-user'
ADDRESS_AWS_EU = 'https://apiv2-eu.devo.com'
ADDRESS_QUERY_COMPLEMENT = 'search/query'
ADDRESS_JOB = '/search/job/'

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
    "no_auth": "Client don't have key&secret or auth token/jwt",
    "no_endpoint": "Endpoint 'address' not found",
    "to_but_no_from": "If you use end dates for the query 'to' it is "
                      "necessary to use start date 'from'",
    "binary_format_requires_output": "Binary format like `msgpack` and `xls` requires output parameter",
    "wrong_processor": "processor must be lambda/function or one of the defaults API processors.",
    "default_keepalive_only": "Mode '%s' always uses default KeepAlive Token",
    "keepalive_not_supported": "Mode '%s' does not support KeepAlive Token",
    "stream_mode_not_supported": "Mode '%s' does not support stream mode",
    "future_queries_not_supported": "Modes 'xls' and 'msgpack' does not support future queries because KeepAlive"
                                    " tokens are not available for those resonses type",
    "missing_api_key": "You need a API Key and API secret to make this",
    "data_query_error": "Error while receiving query data: %s "
}

DEFAULT_KEEPALIVE_TOKEN = '\n'
EMPTY_EVENT_KEEPALIVE_TOKEN = ''
NO_KEEPALIVE_TOKEN = None


class DevoClientException(Exception):
    """ Default Devo Client Exception """

    def __init__(self, message, status=None, code=None, cause=None):
        if isinstance(message, dict):
            self.status = message.get('status', status)
            self.cause = message.get('cause', cause)
            self.message = message.get('msg',
                                       message if isinstance(message, str)
                                       else json.dumps(message))
            self.cid = message.get('cid', None)
            self.code = message.get('code', code)
            self.timestamp = message.get('timestamp',
                                         time.time_ns() // 1000000)
        else:
            self.message = message
            self.status = status
            self.cause = cause
            self.cid = None
            self.code = code
            self.timestamp = time.time_ns() // 1000000
        super().__init__(message)

    def __str__(self):
        return self.message + ((": " + self.cause) if self.cause else '')


def raise_exception(error_data, status=None):
    if isinstance(error_data, requests.models.Response):
        raise DevoClientException(
            _format_error(error_data.json(), status=error_data.status_code))

    elif isinstance(error_data, str):
        if not status:
            raise DevoClientException(
                _format_error({"object": error_data}, status=None))
        raise DevoClientException(
            _format_error({"object": error_data}, status=status))
    elif isinstance(error_data, BaseException):
        raise DevoClientException(_format_error(error_data, status=None))\
            from error_data
    else:
        raise DevoClientException(_format_error(error_data, status=None))


def _format_error(error, status):
    if isinstance(error, dict):
        response = {
            "msg": error.get("msg", "Error Launching Query"),
            "cause": error.get("object") or error.get("context") or error
        }
        # 'object' may be a list
        if isinstance(response["cause"], list):
            response["cause"] = ": ".join(response["cause"])
        if status:
            response['status'] = status
        elif 'status' in error:
            response['status'] = error['status']
        for item in ['code', 'cid', 'timestamp']:
            if item in error:
                response[item] = error[item]
        return response
    else:
        return {
            "msg": str(error),
            "cause": str(error)
        }


class ClientConfig:
    """
    Main class for configuration of Client class. With diferent configurations
    """

    def __init__(self, processor=DEFAULT, response="json/simple/compact",
                 destination=None, stream=True, pragmas=None,
                 keepAliveToken=DEFAULT_KEEPALIVE_TOKEN):
        """
        Initialize the API with this params, all optionals
        :param processor: processor for response, default is None
        :param response: format of response
        :param destination: Destination options, see Documentation
        :param stream: Stream queries or not
        :param pragmas: pragmas por query: user, app_name and comment
        :param keepAliveToken: KeepAlive token for long responses queries
        """
        self.stream = stream
        self.response = response
        self.destination = destination
        self.proc = None
        self.processor = None
        self.set_processor(processor)
        self.keepAliveToken = None
        self.set_keepalive_token(keepAliveToken)

        if pragmas:
            self.pragmas = pragmas
            if "user" not in self.pragmas.keys():
                self.pragmas['user'] = CLIENT_DEFAULT_USER
            if "app_name" not in self.pragmas.keys():
                self.pragmas['app_name'] = CLIENT_DEFAULT_APP_NAME
        else:
            self.pragmas = {"user": CLIENT_DEFAULT_USER,
                            "app_name": CLIENT_DEFAULT_APP_NAME}

    def set_processor(self, processor=None):
        """
        Set processor of response
        :param processor: lambda function
        :return:
        """
        if isinstance(processor, (str, bytes)):
            self.proc = processor
            try:
                self.processor = processors()[self.proc]()
            except KeyError:
                raise_exception(f"Processor {self.proc} not found")
        elif isinstance(processor, (type(lambda x: 0))):
            self.proc = "CUSTOM"
            self.processor = processor
        else:
            raise_exception(ERROR_MSGS["wrong_processor"])
        return True

    def set_user(self, user=CLIENT_DEFAULT_USER):
        """
        Set user to put in pragma when make the query
        :param user: username string
        :return:
        """
        self.pragmas['user'] = user
        return True

    def set_app_name(self, app_name=CLIENT_DEFAULT_APP_NAME):
        """
        Set app_name to put in pragma when make the query
        :param app_name: app_name string
        :return:
        """
        self.pragmas['app_name'] = app_name
        return True

    def set_keepalive_token(self, keepAliveToken=DEFAULT_KEEPALIVE_TOKEN):
        """
        Set whether KeepAlive token is used and which token is used
        :param keepAliveToken: KeepAlive token for long responses queries
        :return:
        """
        # The KeepAlive token does not apply to any format other than 'csv',
        # 'tsv'. All json* responses always use default b'    ' token for
        # keepalive (cannot be modified), but implementation uses
        # NO_KEEP_ALIVE value as it does not change the query msgpack and
        # xls does not support keepalive
        if self.response in ['json', 'json/compact', 'json/simple',
                             'json/simple/compact']:
            self.keepAliveToken = NO_KEEPALIVE_TOKEN
            if keepAliveToken not in [NO_KEEPALIVE_TOKEN,
                                      DEFAULT_KEEPALIVE_TOKEN]:
                logging.warning(
                    ERROR_MSGS["default_keepalive_only"] % self.response)
        # In the cases 'csv', 'tsv' you can use any value passed in
        # 'keepAliveToken'.
        elif self.response in ['csv', 'tsv']:
            self.keepAliveToken = keepAliveToken
        else:
            if keepAliveToken not in [NO_KEEPALIVE_TOKEN,
                                      DEFAULT_KEEPALIVE_TOKEN]:
                logging.warning(
                    ERROR_MSGS["keepalive_not_supported"] % self.response)
            self.keepAliveToken = NO_KEEPALIVE_TOKEN
        return True


class Client:
    """
    The Devo search rest api main class
    """

    def __init__(self, address=None, auth=None, config=None,
                 retries=None, timeout=None, verify=None, retry_delay=None):
        """
        Initialize the API with this params, all optionals
        :param address: endpoint
        :param auth: object with auth params (key, secret, token, jwt)
        :param retries: number of retries for a query
        :param timeout: timeout of socket. Default: None (blocking queries)
        :param retry_delay: delay to wait between retry attemps, exponential
         backoff algorithm applied with rate reduction of 2. Default: 5 seconds
        :param verify: Whether enable or disable the TLS authentication of
         endpoint
        """
        if config is None:
            self.config = ClientConfig()
        elif isinstance(config, ClientConfig):
            self.config = config
        else:
            address = address if address else config.get("address", None)
            auth = auth if auth else \
                config.get("auth",
                           {"key": config.get("key", None),
                            "secret": config.get("secret", None),
                            "jwt": config.get("jwt", None),
                            "token": config.get("token", None)})

            verify = verify if verify is not None \
                else config.get("verify", True)
            retries = retries if retries is not None \
                else config.get("retries", 0)
            timeout = timeout if timeout is not None \
                else config.get("timeout", 300)
            retry_delay = retry_delay if retry_delay is not None \
                else config.get("retry_delay", 5)
            self.config = self._from_dict(config)

        self.auth = auth
        if not address:
            raise raise_exception(ERROR_MSGS['no_endpoint'])

        self.address = self.__get_address_parts(address)

        self.retries = int(retries) if retries else 0
        self.timeout = int(timeout) if timeout else 300
        self.retry_delay = int(retry_delay) if retry_delay else 5
        self.verify = verify if verify is not None else True

        # For internal testing purposes, Devo will never expose a REST service
        # in an unsecure manner
        self.unsecure_http = True if \
            os.getenv("UNSECURE_HTTP", "False").upper() == "TRUE" else False

    @staticmethod
    def _from_dict(config):
        """
        Create Client object from config file values
        :param config: lt-common config standar
        """
        return ClientConfig(processor=config.get("processor", DEFAULT),
                            response=config.get("response",
                                                "json/simple/compact"),
                            destination=config.get("destination", None),
                            stream=config.get("stream", True),
                            keepAliveToken=config.get("keepAliveToken",
                                                      DEFAULT_KEEPALIVE_TOKEN))

    def verify_certificates(self, option=True):
        """
        Set if verify or not the TSL certificates in https calls
        :param option: (bool) True or False
        """
        self.verify = option

    def __get_address_parts(self, address):
        """
        Split the two parts of the api address
        :param address: address of the api
        """
        return \
            self.__verify_address_complement(
                address.split("//")[-1].split("/", maxsplit=1))

    @staticmethod
    def __verify_address_complement(address_list):
        """
        Verify if only has main domain or full address
        :param address_list: One or two part of the address
        """
        return address_list if len(address_list) == 2 \
            else [address_list[0], ADDRESS_QUERY_COMPLEMENT]

    @staticmethod
    def _generate_dates(dates):
        """
        Generate and merge dates object
        :param dates: object with options for query, see doc
        :return: updated opts
        """
        default = {'from': '1h', 'to': None}
        if not dates:
            return default

        default.update(dates)
        return default

    @staticmethod
    def stream_available(resp):
        """
        Verify whether stream response supports stream mode
        :param resp: str
        :return: bool
        """
        return resp not in ["json", "json/compact", "msgpack", "xls"]

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

    def configurate(self, processor=None, response=None,
                    destination=None, stream=True,
                    keepAliveToken=DEFAULT_KEEPALIVE_TOKEN):
        """
        Method for fill Configuration options easier
        :param processor: processor for response, default is None
        :param response: format of response
        :param destination: Destination options, see Doc for more info
        :param stream: Stream queries or not
        :param keepAliveToken: KeepAlive token for long responses queries
        """
        self.config.set_processor(processor)
        if response:
            self.config.response = response

        if stream:
            self.config.stream = stream

        if destination:
            self.config.destination = destination
        self.config.set_keepalive_token(keepAliveToken)

    def query(self, query=None, query_id=None, dates=None,
              limit=None, offset=None, comment=None):
        """
        Query API by a custom query
        :param query: Query to perform
        :param query_id: Query ID to perform the query
        :param dates: Dict with "from" and "to" keys
        :param limit: Max number of rows
        :param offset: start of needle for query
        :param comment: comment for query
        :return: Result of the query (dict) or Iterator object
        """
        dates = self._generate_dates(dates)

        if query is not None:
            query += self._generate_pragmas(comment=comment)

        query_opts = {'limit': limit,
                      'response': self.config.response,
                      'offset': offset,
                      'destination': self.config.destination,
                      'keepAliveToken': self.config.keepAliveToken
                      }

        if not self.stream_available(self.config.response) \
                or not self.config.stream:
            if not dates['to']:
                dates['to'] = "now()"
            if self.config.stream:
                logging.warning(ERROR_MSGS["stream_mode_not_supported"] % self.config.response)
            # If is a future query and response type is 'xls' or 'msgpack'
            # return warning because is not available.
            if self._future_queries_available(self.config.response):
                self.config.stream = False
            else:

                fromDate = self._fromDate_parser(default_to(dates['from']))
                toDate = self._toDate_parser(fromDate, default_to(dates['to']))

                if toDate > default_to("now()"):
                    raise raise_exception(ERROR_MSGS["future_queries_not_supported"])

            self.config.stream = False

        return self._call(
            self._get_payload(query, query_id, dates, query_opts)
        )

    def _call(self, payload):
        """
        Make the call, select correct item to return
        :param payload: item with headers for request
        :return: Response from API
        """
        if self.config.stream:
            return self._return_string_stream(payload)
        # We access to the whole server response value
        (wholeResponse, _, _) = self._make_request(payload)

        if isinstance(wholeResponse, str):
            # Analyse the response data to check if there are any error
            # messages within the response.
            self._error_handler(wholeResponse)
            return proc_json()(wholeResponse)
        if self.config.response in ["msgpack", "xls"]:
            # Analyse the response data to check if there are any error
            # messages within the response.
            self._error_handler(wholeResponse.content)
            return self.config.processor(wholeResponse.content)
        else:
            # Analyse the response data to check if there are any error
            # messages within the response.
            self._error_handler(wholeResponse.text)
            return self.config.processor(
                self._keepalive_content_sanitize(wholeResponse.text))

    def _return_string_stream(self, payload):
        """If it's a stream call, return yield lines
        :param payload: item with headers for request
        :return line: yield-generator item
        """
        # We access to the iterLines response from the server.
        (_, iterStringResponse, _) = self._make_request(payload)

        response = filter(lambda l: self._empty_lines_sanitize(l),
                          map(lambda l: self._keepalive_stream_sanitize(l),
                              map(lambda l: l.decode('utf-8'),
                                  iterStringResponse)))
        try:
            first = next(response)
        except StopIteration:
            return None  # The query did not return any result
        except TypeError:
            raise_exception(response)

        if self._is_correct_response(first):
            if self.config.proc == SIMPLECOMPACT_TO_OBJ:
                aux = json_compact_simple_names(proc_json()(first)['m'])
                self.config.processor = proc_json_compact_simple_to_jobj(aux)
            elif self.config.proc == SIMPLECOMPACT_TO_ARRAY:
                pass
            else:
                yield self.config.processor(first)
            for line in response:
                # Analyse the response data to check if there are any error
                # messages within the response.
                self._error_handler(line)

                yield self.config.processor(line)
        else:
            yield proc_json()(first)

    @staticmethod
    def _empty_lines_sanitize(line):
        return line.strip()

    def _keepalive_content_sanitize(self, response):
        if self.config.keepAliveToken == NO_KEEPALIVE_TOKEN or \
                self.config.keepAliveToken is None:
            return response
        elif self.config.keepAliveToken == DEFAULT_KEEPALIVE_TOKEN:
            if self.config.response.startswith("json"):
                return response
            elif self.config.response in ["csv", "tsv"]:
                return re.sub(rf'{DEFAULT_KEEPALIVE_TOKEN}{{2,}}',
                              f'{DEFAULT_KEEPALIVE_TOKEN}', response)
            else:
                return response
        elif self.config.keepAliveToken == EMPTY_EVENT_KEEPALIVE_TOKEN:
            if self.config.response == 'csv':
                return re.sub(r'(,+$)|(,+\n)', '', response)
            elif self.config.response == 'tsv':
                return re.sub(r'(\t+$)|(\t+\n)', '', response)
            else:
                return response
        else:
            return response.replace(f'{self.config.keepAliveToken}', '')

    def _keepalive_stream_sanitize(self, line):
        if self.config.keepAliveToken == NO_KEEPALIVE_TOKEN or \
                self.config.keepAliveToken is None:
            return line
        elif self.config.keepAliveToken == DEFAULT_KEEPALIVE_TOKEN:
            if self.config.response.startswith("json"):
                return line
            elif self.config.response in ["csv", "tsv"]:
                return re.sub(DEFAULT_KEEPALIVE_TOKEN, '', line)
            else:
                return line
        elif self.config.keepAliveToken == EMPTY_EVENT_KEEPALIVE_TOKEN:
            if self.config.response == 'csv':
                return re.sub(r'(,+$)|(,+\n)', '', line)
            elif self.config.response == 'tsv':
                return re.sub(r'(\t+$)|(\t+\n)', '', line)
            else:
                return line
        else:
            return line.replace(f'{self.config.keepAliveToken}', '')

    def _make_request(self, payload):
        """
        Make the request and control the logic about retries if not internet
        :param payload: item with headers for request
        :return: response
        """
        tries = 0
        while tries <= self.retries:
            try:
                response = self.__request(payload)
                if response.status_code != 200:
                    raise DevoClientException(response)

                if self.config.stream:
                    if (self.config.response in ["msgpack", "xls"]):
                        return (None, None, response.iter_content())
                    return (None, response.iter_lines(), None)
                # In case of NOT stream mode we return the whole server
                # response.
                return (response, None, None)
            except requests.exceptions.ConnectionError as error:
                tries += 1
                if tries > self.retries:
                    return raise_exception(error)
                time.sleep(self.retry_delay * (2 ** (tries-1)))
            except DevoClientException as error:
                if isinstance(error, DevoClientException):
                    raise_exception(error.args[0])
                else:
                    raise_exception(error)
            except Exception as error:
                return raise_exception(error)

    def __request(self, payload):
        """
        POST request method extracted for mocking purposes
        """
        return requests.post("{}://{}".format(
            "http" if self.unsecure_http else "https",
            "/".join(self.address)),
            data=payload,
            headers=self._get_headers(payload),
            verify=self.verify,
            timeout=self.timeout,
            stream=self.config.stream)

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
        date_from = default_from(dates['from'])
        date_to = default_to(dates['to']) if dates['to'] is not None else None

        payload = {
            "from":
                int(date_from / 1000) if isinstance(date_from, (int, float))
                else date_from,
            "to":
                int(date_to / 1000) if isinstance(date_to, (int, float))
                else date_to,
            "mode": {"type": opts['response']}}

        if dates.get("timeZone"):
            payload['timeZone'] = dates.get("timeZone")

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

        if opts["keepAliveToken"] is not None and \
                opts["keepAliveToken"] != NO_KEEPALIVE_TOKEN:
            if opts["keepAliveToken"] == EMPTY_EVENT_KEEPALIVE_TOKEN:
                payload['keepAlive'] = {'type': 'empty'}
            elif opts["keepAliveToken"] == DEFAULT_KEEPALIVE_TOKEN:
                payload['keepAlive'] = {'type': 'token'}
            else:
                payload['keepAlive'] = {'type': 'token',
                                        'token': opts["keepAliveToken"]}

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

        raise DevoClientException((ERROR_MSGS['no_auth']))

    def _get_sign(self, data, tstamp):
        """
        Generate the sign for the request
        :param data: returned value from _get_payload()
        :param tstamp: Epoch timestamp
        :return: The sign in hex response
        """
        if not self.auth.get("key", False) \
                or not self.auth.get("secret", False):
            raise DevoClientException(ERROR_MSGS["missing_api_key"])
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
                      'pragma comment.user:"{}"' \
            .format(self.config.pragmas['app_name'],
                    self.config.pragmas['user'])

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
                                               ADDRESS_JOB, job_id))

    def stop_job(self, job_id):
        """ Stop one job by ID
        :param job_id: id of job
        :return: bool"""
        return self._call_jobs("{}{}{}{}".format(self.address[0], ADDRESS_JOB,
                                                 'stop/', job_id))

    def start_job(self, job_id):
        """ Start one job by ID
        :param job_id: id of job
        :return: bool"""
        return self._call_jobs("{}{}{}{}".format(self.address[0], ADDRESS_JOB,
                                                 'start/', job_id))

    def remove_job(self, job_id):
        """ Remove one job by ID
        :param job_id: id of job
        :return: bool"""
        return self._call_jobs("{}{}{}{}".format(self.address[0], ADDRESS_JOB,
                                                 'remove/', job_id))

    def _call_jobs(self, address):
        """
        Make the call
        :param address: endpoint
        :return: Response from API
        """
        tries = 0
        while tries <= self.retries:
            response = None
            try:
                response = requests.get("https://{}".format(address),
                                        headers=self._get_headers(""),
                                        verify=self.verify,
                                        timeout=self.timeout)
            except ConnectionError as error:
                raise_exception({"status": 404, "msg": error})

            if response:
                if response.status_code != 200 or \
                        "error" in response.text[0:15].lower():
                    raise_exception(response.text)
                    return None
                try:
                    return json.loads(response.text)
                except json.decoder.JSONDecodeError:
                    return response.text
            tries += 1
            time.sleep(self.retry_delay * (2 ** (tries-1)))
        return {}

    @staticmethod
    def _future_queries_available(resp):
        """
        Verify whether future queries are supported for the response type
        selected
        :param resp: str
        :return: bool
        """
        return resp not in ["msgpack", "xls"]

    @staticmethod
    def _fromDate_parser(fromDate, now=datetime.now()):

        if isinstance(fromDate, (float, int)):
            return fromDate
        now = now.astimezone(pytz.UTC)
        now_milliseconds = now.timestamp() * 1000
        adate = datetime.strptime(str(now.date()), '%Y-%m-%d').replace(
            tzinfo=pytz.utc)

        if re.match('^[1-9]+(d|ad|h|ah|m|am|s|as)', fromDate):
            date = re.split('(d|ad|h|ah|m|am|s|as)', fromDate)
            num = int(date[0])
            unit = date[1]

            if unit == "d":
                return now_milliseconds - (8.64e+7 * num)
            elif unit == "ad":
                return adate.timestamp() * 1000 - (8.64e+7 * num)
            elif unit == "h":
                return now_milliseconds - (3.6e+6 * num)
            elif unit == "ah":
                return adate.timestamp() * 1000 - (3.6e+6 * num)
            elif unit == "m":
                return now_milliseconds - (60000 * num)
            elif unit == "am":
                return adate.timestamp() * 1000 - (60000 * num)
            elif unit == "s":
                return now_milliseconds - (1000 * num)
            elif unit == "as":
                return adate.timestamp() * 1000 - (1000 * num)

        elif fromDate == "today":
            return adate.timestamp() * 1000
        elif fromDate == "endday":
            return (adate + timedelta(hours=23, minutes=59,
                                      seconds=59)).timestamp() * 1000
        elif fromDate == "endmonth":
            return (adate.replace(
                day=calendar.monthrange(adate.year, adate.month)[
                    1]) + timedelta(hours=23, minutes=59,
                                    seconds=59)).timestamp() * 1000
        elif fromDate == "now":
            return now.timestamp() * 1000

    @staticmethod
    def _toDate_parser(fromDateMillisec, toDate, now=datetime.now()):

        if isinstance(toDate, (float, int)):
            return toDate

        now = now.astimezone(pytz.UTC)
        fromDate = datetime.fromtimestamp(fromDateMillisec / 1000).replace(
            tzinfo=pytz.utc)
        aFromdate = datetime.strptime(str(fromDate.date()),
                                      '%Y-%m-%d').replace(tzinfo=pytz.utc)
        aNowdate = datetime.strptime(str(now.date()), '%Y-%m-%d').replace(
            tzinfo=pytz.utc)

        if re.match('^[1-9]+(d|ad|h|ah|m|am|s|as)', toDate):
            date = re.split('(d|ad|h|ah|m|am|s|as)', toDate)
            num = int(date[0])
            unit = date[1]

            if unit == "d":
                return fromDateMillisec + (8.64e+7 * num)
            elif unit == "ad":
                return aFromdate.timestamp() * 1000 + (8.64e+7 * num)
            elif unit == "h":
                return fromDateMillisec + (3.6e+6 * num)
            elif unit == "ah":
                return aFromdate.timestamp() * 1000 + (3.6e+6 * num)
            elif unit == "m":
                return fromDateMillisec + (60000 * num)
            elif unit == "am":
                return aFromdate.timestamp() * 1000 + (60000 * num)
            elif unit == "s":
                return fromDateMillisec + (1000 * num)
            elif unit == "as":
                return aFromdate.timestamp() * 1000 + (1000 * num)

        elif toDate == "today":
            return aNowdate.timestamp() * 1000
        elif toDate == "endday":
            return (aFromdate + timedelta(hours=23, minutes=59,
                                          seconds=59)).timestamp() * 1000
        elif toDate == "endmonth":
            return (aFromdate.replace(
                day=calendar.monthrange(aFromdate.year, aFromdate.month)[
                    1]) + timedelta(hours=23, minutes=59,
                                    seconds=59)).timestamp() * 1000
        elif toDate == "now":
            return now.timestamp() * 1000

    def _error_handler(self, content):
        """
        Function to manage possible errors returned from malote queries that
        Serrea is sending as part of the http response
        Depending on the response output format the error will be handled
        by different ways
        """
        if self.config.response in ["xls", "msgpack"]:
            return content
        else:
            pattern = DATA_ERROR_PATTERNS[self.config.response]
            match = re.search(pattern, content)
            if match:
                error = match.group(0)
                code = int(match.group(1))
                message = match.group(2).strip()
                raise DevoClientException(
                    ERROR_MSGS["data_query_error"]
                    % message, code=code, cause=error)
            else:
                return content


DATA_ERROR_PATTERNS = {
    "json/simple/compact": r'{"e":\[(\d+),"([^"]+)"]}',
    "json/simple": r'\["error",(\d+),"([^"]+)"\]',
    "json": r'"error":\s\[(\d+),"([^"]+)"\]',
    "json/compact": r'"e":\s\[(\d+),"([^"]+)"\]',
    "csv": r'devo\.api\.error,(\d+),([^,\n]+)',
    'tsv': r'devo\.api\.error(?:\t|\s+)(\d+)(?:\t|\s+)([^\t\n]+)'
}
