# -*- coding: utf-8 -*-
"""Main class for pull data from Devo API (Client)."""
import time
import sys

PY3 = sys.version_info[0] > 2
CLIENT_DEFAULT_APP_NAME = 'python-sdk-app'
CLIENT_DEFAULT_USER = 'python-sdk-user'
URL_AWS_EU = 'https://api-eu.logtrust.com'
URL_VDC = 'https://spainapi.logtrust.com'
URL_AWS_USA = 'https://api-us.logtrust.com'
URL_QUERY_COMPLEMENT = 'search/query'
URL_JOB = '/search/job/'
URL_JOBS = '/search/jobs'
URL_JOB_START = 'start/'
URL_JOB_STOP = 'stop/'
URL_JOB_REMOVE = 'remove/'


class DevoClientException(Exception):
    """ Default Devo Client Exception """


if not PY3:
    class ConnectionError(OSError):
        """ Connection error. """
        def __init__(self, *args, **kwargs):  # real signature unknown
            pass


class Base:
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

        self.url, self.query_url = self.__set_url_query()
        self.retries = 3
        self.timeout = 30
        self.sleep = 5

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
    def _stream_available(resp):
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


    @staticmethod
    def _format_error(error):
        return '{"msg": "Error Launching Query", "status": 500, ' \
               '"object": "%s"}' % error
