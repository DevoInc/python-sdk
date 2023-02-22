import hashlib
import hmac
import time
from enum import Enum

from devo.api.exception import DevoClientException
from devo.api.messages import ERROR_MSGS


def sign_request_with_key(key, secret, data, tstamp=None):
    """
    Creates sign value for authenticating API requests based on key and secret
    :param key: key value
    :param secret: secret value
    :param data: content of the request
    :param tstamp: timestamp of the request
    :return: sign value as HEX string
    """
    tstamp = str(int(time.time()) * 1000) if tstamp is None else tstamp
    sign = hmac.new(secret.encode("utf-8"),
                    (key + data + tstamp).encode("utf-8"),
                    hashlib.sha256)
    return sign.hexdigest()


class AuthenticationMode(Enum):
    """Authentication mechanisms supported by Devo APIs"""

    KEY = 1
    """API key and secret based"""

    TOKEN = 2
    """Token based"""

    JWT = 3
    """JWT based"""


def get_request_headers(mode: AuthenticationMode, data, key: str = None,
                        secret: str = None, token: str = None, jwt: str = None,
                        tstamp=None):
    """
    Create headers for API call
    :param mode: Authentication method: Key/Secret, Token or JWT
    :param data: Content of the request
    :param key: Key for Key/Secret based authentication
    :param secret: Secret for Key/Secret based authentication
    :param token: Token for Token based authentication
    :param jwt: Key for JWT based authentication
    :param tstamp: timestamp of the request
    :return: Return the formed http headers
    """
    tstamp = str(int(time.time()) * 1000) if tstamp is None else tstamp
    if mode == AuthenticationMode.KEY and key is not None and secret is not None:
        sign = sign_request_with_key(key, secret, data, tstamp)
        return {
            'Content-Type': 'application/json',
            'x-logtrust-apikey': key,
            'x-logtrust-timestamp': tstamp,
            'x-logtrust-sign': sign
        }

    if mode == AuthenticationMode.TOKEN and token is not None:
        return {
            'Content-Type': 'application/json',
            'x-logtrust-timestamp': tstamp,
            'Authorization': "Bearer %s" % token
        }

    if mode == AuthenticationMode.JWT and jwt is not None:
        return {
            'Content-Type': 'application/json',
            'x-logtrust-timestamp': tstamp,
            'Authorization': "jwt %s" % jwt
        }

    raise DevoClientException((ERROR_MSGS['no_auth']))
