# -*- coding: utf-8 -*-
"""Main class for pull data from Devo API (Client)."""
import hmac
import hashlib
import time
import json
import requests
from devo.common import default_from, default_to
from .processors import processors, proc_json, \
    json_compact_simple_names, proc_json_compact_simple_to_jobj

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
    "no_auth": "Client dont have key&secret or auth token/jwt",
    "no_endpoint": "Endpoint 'address' not found"
}


class DevoClientException(Exception):
    """ Default Devo Client Exception """


def raise_exception(error):
    """Util function for raise exceptions"""
    try:
        if isinstance(error, str):
            raise DevoClientException(proc_json()(error))
        if isinstance(error, DevoClientException):
            if isinstance(error.args[0], str):
                raise DevoClientException(proc_json()(error.args[0]))
            raise DevoClientException(error.args[0])
        if isinstance(error, dict):
            raise DevoClientException(error)
        response_text = proc_json()(error.text)
        raise DevoClientException(response_text)
    except json.decoder.JSONDecodeError:
        raise DevoClientException(_format_error(error))


def _format_error(error):
    return '{"msg": "Error Launching Query", "status": 500, ' \
           '"object": "%s"}' % str(error).replace("\"", "\\\"")


class ClientConfig:
    """
    Main class for configuration of Client class. With diferent configurations
    """
    def __init__(self, processor=DEFAULT, response="json/simple/compact",
                 destination=None, stream=True, pragmas=None):
        """
        Initialize the API with this params, all optionals
        :param processor: processor for response, default is None
        :param response: format of response
        :param destination: Destination options, see Documentation for more info
        :param stream: Stream queries or not
        :param pragmas: pragmas por query: user, app_name and comment
        """
        self.stream = stream
        self.response = response
        self.destination = destination
        self.proc = None
        self.processor = None
        self.set_processor(processor)

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
                raise_exception("Processor not found")
        elif isinstance(processor, (type(lambda x: 0))):
            self.proc = "CUSTOM"
            self.processor = processor
        else:
            raise_exception("processor must be lambda/function or one of"
                            "the defaults API processors.")
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


class Client:
    """
    The Devo seach rest api main class
    """
    def __init__(self, address=None, auth=None, config=None,
                 retries=None, timeout=None, verify=None):
        """
        Initialize the API with this params, all optionals
        :param address: endpoint
        :param auth: object with auth params (key, secret, token, jwt)
        :param retries: number of retries for a query
        :param timeout: timeout of socket
        """
        if config is None:
            self.config = ClientConfig()
        elif isinstance(config, ClientConfig):
            self.config = config
        else:
            address = address if address else config.get("address", None)
            auth = auth if auth else config.get("auth",
                                                {"key": config.get("key", None),
                                                 "secret": config.get("secret",
                                                                      None),
                                                 "jwt": config.get("jwt", None),
                                                 "token": config.get("token",
                                                                     None)})

            verify = verify if verify is not None \
                else config.get("verify", True)
            retries = retries if retries is not None \
                else config.get("retries", 3)
            timeout = timeout if timeout is not None \
                else config.get("timeout", 30)
            self.config = self._from_dict(config)

        self.auth = auth
        if not address:
            raise raise_exception(
                _format_error(ERROR_MSGS['no_endpoint'])
            )

        self.address = self.__get_address_parts(address)

        self.retries = int(retries) if retries else 3
        self.timeout = int(timeout) if timeout else 30
        self.verify = verify if verify is not None else True

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
                            stream=config.get("stream", True))

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

    def configurate(self, processor=None, response=None,
                    destination=None, stream=True):
        """
        Method for fill Configuration options more easy
        :param processor: processor for response, default is None
        :param response: format of response
        :param destination: Destination options, see Doc for more info
        :param stream: Stream queries or not
        """
        self.config.set_processor(processor)
        if response:
            self.config.response = response

        if stream:
            self.config.stream = stream

        if destination:
            self.config.destination = destination

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
                      'destination': self.config.destination
                      }

        if not self.stream_available(self.config.response) \
                or not self.config.stream:
            if not dates['to']:
                dates['to'] = "now()"
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
            return self._return_stream(payload)
        response = self._make_request(payload)

        if isinstance(response, str):
            return proc_json()(response)
        return self.config.processor(response.text)

    def _return_stream(self, payload):
        """If its a stream call, return yield lines
        :param payload: item with headers for request
        :return line: yield-generator item
        """
        response = self._make_request(payload)
        try:
            first = next(response)
        except StopIteration:
            first = None
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
                yield self.config.processor(line)
        else:
            yield proc_json()(first)

    def _make_request(self, payload):
        """
        Make the request and control the logic about retries if not internet
        :param payload: item with headers for request
        :return: response
        """
        tries = 0
        while tries < self.retries:
            try:
                response = requests.post("https://{}"
                                         .format("/".join(self.address)),
                                         data=payload,
                                         headers=self._get_headers(payload),
                                         verify=self.verify,
                                         timeout=self.timeout,
                                         stream=self.config.stream)
                if response.status_code != 200:
                    raise DevoClientException(response)

                if self.config.stream:
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
        if not self.auth.get("key", False) \
                or not self.auth.get("secret", False):
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
        while tries < self.retries:
            response = None
            try:
                response = requests.get("https://{}".format(address),
                                        headers=self._get_headers(""),
                                        verify=self.verify,
                                        timeout=self.timeout)
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
