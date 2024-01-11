# -*- coding: utf-8 -*-
""" File to group all the classes and functions related to the connection
and sending of data to Devo """
import errno
import logging
import select
import socket
import ssl
import sys
import time
import zlib
from enum import Enum
from pathlib import Path
from ssl import SSLWantReadError, SSLWantWriteError

import pem
from _socket import SHUT_WR
from OpenSSL import SSL, crypto

from devo.common import Configuration, get_log, get_stream_handler

from .transformsyslog import (COMPOSE, COMPOSE_BYTES, FACILITY_USER, FORMAT_MY,
                              FORMAT_MY_BYTES, SEVERITY_INFO, priority_map)

PYPY = hasattr(sys, "pypy_version_info")


class ERROR_MSGS(str, Enum):
    def __str__(self):
        return str(self.value)

    WRONG_FILE_TYPE = ("'%s' is not a valid type to be opened as a file",)
    ADDRESS_TUPLE = ('Devo-SenderConfigSSL| address must be a tuple ("hostname", int(port))\'',)
    WRONG_SSL_CONFIG = ("Devo-SenderConfigSSL|Can't create SSL config: %s",)
    CONFIG_FILE_NOT_FOUND = (
        "Error in the configuration, %s is not a file or the path does not exist",
    )
    CANT_READ_CONFIG_FILE = ("Error in the configuration %s can't be read\noriginal error: %s",)
    CONFIG_FILE_PROBLEM = ("Error in the configuration, %s problem related to: %s",)
    KEY_NOT_COMPATIBLE_WITH_CERT = (
        "Error in the configuration, the key: %s is not compatible"
        " with the cert: %s\noriginal error: %s",
    )
    CHAIN_NOT_COMPATIBLE_WITH_CERT = (
        "Error in config, the chain: %s is not compatible with the"
        " certificate: %s\noriginal error: %s",
    )
    TIMEOUT_RELATED_TO_AN_INCORRECT_ADDRESS_PORT = (
        "Possible error in config, a timeout could be"
        " related to an incorrect address/port: %s\n"
        "original error: %s",
    )
    INCORRECT_ADDRESS_PORT = ("Error in config, incorrect address/port: %s\noriginal error: %s",)
    CERTIFICATE_IN_ADDRESS_IS_NOT_COMPATIBLE = (
        "Error in config, the certificate in the address: %s is not compatible with: %s",
    )
    ADDRESS_MUST_BE_A_TUPLE = (
        'Devo-SenderConfigSSL| address must be a tuple \'("hostname",' " int(port))'",
    )
    CANT_CREATE_TCP_CONFIG = ("DevoSenderConfigTCP|Can't create TCP config: %s",)
    PROBLEMS_WITH_SENDER_ARGS = ("Problems with args passed to Sender",)
    TCP_CONN_ESTABLISHMENT_SOCKET = ("TCP conn establishment socket error: %s",)
    SSL_CONN_ESTABLISHMENT_SOCKET = ("SSL conn establishment socket error: %s",)
    PFX_CERTIFICATE_READ_FAILED = ("PFX Certificate read failed: %s",)
    SEND_ERROR = ("Send error",)
    SOCKET_ERROR = ("Socket error: %s",)
    SOCKET_CANT_CONNECT_UNKNOWN_ERROR = ("Socket cant connect: unknown error",)
    NO_ADDRESS = ("No address",)
    MULTILINE_SENDING_ERROR = ("Error sending multiline event: %s",)
    RAW_SENDING_ERROR = ("Error sending raw event: %s",)
    CLOSING_ERROR = "Error closing connection"
    FLUSHING_BUFFER_ERROR = "Error flushing buffer"


class DevoSenderException(Exception):
    """Default Devo Sender Exception for functionalities related to sending
    events to the platform"""

    def __init__(self, message: str):
        """
        Creates an exception related to event sending tasks

        :param message: Message describing the exception. It will be also
         used as `args` attribute in `Exception` class
        """
        self.message: str = message
        """Message describing exception"""
        super().__init__(self.message)


class SenderConfigSSL:
    """
    Configuration SSL class.

    :param address: (tuple) (Server address, port)
    :param key: (str) key src file
    :param cert:  (str) cert src file
    :param chain:  (str) chain src file
    :param pkcs:  (dict) (path: pfx src file, password: of cert)
    :param sec_level: (int) default None. If certs are too weak you can change
    this param to work with it
    :param verify_mode:  (bool) Verification for the configuration

    >>>sender_config = SenderConfigSSL(address=(SERVER, int(PORT)), key=KEY,
    ...                                cert=CERT, chain=CHAIN, sec_level=None,
    ...                                check_hostname=True,
    ...                                verify_mode=None,
    ...                                verify_config=False)

    See Also:
        Sender

    """

    def __init__(
        self,
        address=None,
        key=None,
        cert=None,
        chain=None,
        pkcs=None,
        sec_level=None,
        check_hostname=True,
        verify_mode=None,
        verify_config=False,
    ):
        if not isinstance(address, tuple):
            raise DevoSenderException(ERROR_MSGS.ADDRESS_TUPLE)
        try:
            self.address = address
            self.key = key
            self.cert = cert
            self.chain = chain
            self.pkcs = pkcs
            self.hostname = socket.gethostname()
            self.sec_level = sec_level
            self.check_hostname = check_hostname
            self.verify_config = verify_config
            self.verify_mode = verify_mode
        except Exception as error:
            raise DevoSenderException(ERROR_MSGS.WRONG_SSL_CONFIG % str(error)) from error

        if self.verify_config:
            self.check_config_files_path()
            self.check_config_certificate_key()
            self.check_config_certificate_chain()
            self.check_config_certificate_address()

    def check_config_files_path(self):
        """
        Check if the certificate files
        in the configurations are path correct.

        :return: Boolean true or raises an exception
        """
        certificates = [self.key, self.chain, self.cert]
        for file in certificates:
            try:
                if not (file.is_file() if isinstance(file, Path) else Path(file).is_file()):
                    raise DevoSenderException(ERROR_MSGS.CONFIG_FILE_NOT_FOUND % file)
            except IOError as error:
                if error.errno == errno.EACCES:
                    raise DevoSenderException(
                        ERROR_MSGS.CANT_READ_CONFIG_FILE % (file, str(error))
                    ) from error
                else:
                    raise DevoSenderException(
                        ERROR_MSGS.CONFIG_FILE_PROBLEM % (file, str(error))
                    ) from error
        return True

    def check_config_certificate_key(self):
        """
        Check if both the certificate and the key
        in the configuration are compatible with each other.

        :return: Boolean true or raises an exception
        """

        with open_file(self.cert, mode="rb") as certificate_file, open_file(
            self.key, mode="rb"
        ) as key_file:
            certificate_raw = certificate_file.read()
            key_raw = key_file.read()
            certificate_obj = crypto.load_certificate(crypto.FILETYPE_PEM, certificate_raw)
            private_key_obj = crypto.load_privatekey(crypto.FILETYPE_PEM, key_raw)
            context = SSL.Context(SSL.TLS_CLIENT_METHOD)
            context.use_privatekey(private_key_obj)
            context.use_certificate(certificate_obj)
        try:
            context.check_privatekey()
        except SSL.Error as error:
            raise DevoSenderException(
                ERROR_MSGS.KEY_NOT_COMPATIBLE_WITH_CERT % (self.key, self.cert, str(error))
            ) from error
        return True

    def check_config_certificate_chain(self):
        """
        Check if both the certificate and the chain
        in the configuration are compatible with each other.

        :return: Boolean true or raises an exception
        """
        with open_file(self.cert, mode="rb") as certificate_file, open_file(
            self.chain, mode="rb"
        ) as chain_file:
            certificate_raw = certificate_file.read()
            chain_raw = chain_file.read()
            certificate_obj = crypto.load_certificate(crypto.FILETYPE_PEM, certificate_raw)
            certificates_chain = crypto.X509Store()
            for certificate in pem.parse(chain_raw):
                certificates_chain.add_cert(
                    crypto.load_certificate(crypto.FILETYPE_PEM, str(certificate))
                )
            store_ctx = crypto.X509StoreContext(certificates_chain, certificate_obj)
        try:
            store_ctx.verify_certificate()
        except crypto.X509StoreContextError as error:
            raise DevoSenderException(
                ERROR_MSGS.CHAIN_NOT_COMPATIBLE_WITH_CERT % (self.chain, self.cert, str(error))
            ) from error
        return True

    def check_config_certificate_address(self):
        """
        Check if the certificate is compatible with the
        address, also check if the address and port are
        valid.

        :return: Boolean true or raises an exception
        """
        sock = socket.socket()
        context = SSL.Context(SSL.TLS_CLIENT_METHOD)
        sock.settimeout(10)

        # Restrict insecure protocols
        context.set_options(SSL.OP_NO_SSLv2)
        context.set_options(SSL.OP_NO_SSLv3)
        context.set_options(SSL.OP_NO_TLSv1)
        context.set_options(SSL.OP_NO_TLSv1_1)

        connection = SSL.Connection(context, sock)
        try:
            connection.connect(self.address)
        except socket.timeout as error:
            raise DevoSenderException(
                ERROR_MSGS.TIMEOUT_RELATED_TO_AN_INCORRECT_ADDRESS_PORT
                % (str(self.address), str(error))
            ) from error
        except ConnectionRefusedError as error:
            raise DevoSenderException(
                ERROR_MSGS.INCORRECT_ADDRESS_PORT % (str(self.address), str(error))
            ) from error
        sock.setblocking(True)
        connection.do_handshake()
        server_chain = connection.get_peer_cert_chain()
        connection.close()

        with open_file(self.chain, mode="rb") as chain_file:
            chain = chain_file.read()
            chain_certs = []
            for _ca in pem.parse(chain):
                chain_certs.append(crypto.load_certificate(crypto.FILETYPE_PEM, str(_ca)))

        server_common_names = self.get_common_names(server_chain, "get_subject")
        client_common_names = self.get_common_names(chain_certs, "get_issuer")

        if server_common_names & client_common_names:
            return True

        raise DevoSenderException(
            ERROR_MSGS.CERTIFICATE_IN_ADDRESS_IS_NOT_COMPATIBLE % (self.address[0], self.chain)
        )

    @staticmethod
    def get_common_names(cert_chain, components_type):
        result = set()
        for temp_cert in cert_chain:
            for key, value in getattr(temp_cert, components_type)().get_components():
                if key.decode("utf-8") == "CN":
                    result.add(value)
        return result

    @staticmethod
    def fake_get_peer_cert_chain(chain):
        with open_file(chain, mode="rb") as chain_file:
            chain_certs = []
            for _ca in pem.parse(chain_file.read()):
                chain_certs.append(crypto.load_certificate(crypto.FILETYPE_PEM, str(_ca)))
            return chain_certs


class SenderConfigTCP:
    """
    Configuration TCP class.
    :param address:(tuple) Server address and port

    >>>sender_config = SenderConfigTCP(address=(ADDRESS, PORT))

    See Also:
        Sender
    """

    def __init__(self, address=None):
        if not isinstance(address, tuple):
            raise DevoSenderException(ERROR_MSGS.ADDRESS_MUST_BE_A_TUPLE)
        try:
            self.address = address
            self.hostname = socket.gethostname()
            self.sec_level = None
        except Exception as error:
            raise DevoSenderException(ERROR_MSGS.CANT_CREATE_TCP_CONFIG % str(error)) from error


class SenderBuffer:
    """Micro class for buffer values"""

    def __init__(self):
        self.length = 19500
        self.compression_level = -1
        self.text_buffer = b""
        self.events = 0


class Sender(logging.Handler):
    """
    Class that manages the connection to the data collector

    :param config: SenderConfigSSL, SenderConfigTCP or dict object
    :param con_type: TCP or SSL, default SSL, you can pass it in
    config object too
    :param timeout: timeout for socket
    :param inactivity_timeout: inactivity timeout for Ingestion balancer, so connection is
     restarted before reaching
    :param debug: For more info in console/logger output
    :param logger: logger. Default sys.console
    """

    def __init__(
        self,
        config=None,
        con_type=None,
        inactivity_timeout=30,
        timeout=30,
        debug=False,
        logger=None,
    ):
        if config is None:
            raise DevoSenderException(ERROR_MSGS.PROBLEMS_WITH_SENDER_ARGS)

        self.socket = None
        self.reconnection = 0
        self.debug = debug
        self.socket_timeout = timeout
        self.inactivity_timeout = inactivity_timeout
        self.socket_max_connection = 3600 * 1000
        self.last_message = int(time.time())
        self.buffer = SenderBuffer()
        self.logging = {}

        self.timestart = time.time()
        if isinstance(config, (dict, Configuration)):
            timeout = config.get("timeout", timeout)
            debug = config.get("debug", debug)
            config = self._from_dict(config=config, con_type=con_type)

        logging.Handler.__init__(self)
        self.logger = (
            logger
            if logger
            else get_log(
                handler=get_stream_handler(
                    msg_format="%(asctime)s|%(levelname)s|Devo-Sender|%(message)s"
                )
            )
        )

        self._sender_config = config

        if self._sender_config.sec_level is not None:
            self.logger.warning(
                "Openssl's default security "
                "level has been overwritten to "
                "{}.".format(self._sender_config.sec_level)
            )

        if isinstance(config, SenderConfigSSL):
            self.__connect_ssl()

        if isinstance(config, SenderConfigTCP):
            self.__connect_tcp_socket()

    def __del__(self):
        self.close()

    def __connect(self):
        if isinstance(self._sender_config, SenderConfigSSL):
            self.__connect_ssl()
        if isinstance(self._sender_config, SenderConfigTCP):
            self.__connect_tcp_socket()

    def __connect_tcp_socket(self):
        """
        Connect to TCP socket
        :return:
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.socket_timeout)
        try:
            self.socket.connect(self._sender_config.address)
            self.last_message = int(time.time())
        except socket.error as error:
            self.close()
            raise DevoSenderException(
                ERROR_MSGS.TCP_CONN_ESTABLISHMENT_SOCKET % str(error)
            ) from error

        self.timestart = int(round(time.time() * 1000))
        self.socket.setblocking(False)

    def __connect_ssl(self):
        """
        Connect to SSL socket.

        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.socket_timeout)
        try:
            if self._sender_config.pkcs is not None:
                from .pfx_to_pem import pfx_to_pem

                pkcs = self._sender_config.pkcs
                key, cert, chain = pfx_to_pem(
                    path=pkcs.get("path", None), password=pkcs.get("password", None)
                )

                self._sender_config.key = key.name
                self._sender_config.cert = cert.name
                self._sender_config.chain = chain.name
        except Exception as error:
            self.close()
            raise DevoSenderException(
                ERROR_MSGS.PFX_CERTIFICATE_READ_FAILED % str(error)
            ) from error
        try:
            if (
                self._sender_config.key is not None
                and self._sender_config.chain is not None
                and self._sender_config.cert is not None
            ):
                context = ssl.create_default_context(cafile=self._sender_config.chain)

                if self._sender_config.sec_level is not None:
                    context.set_ciphers(
                        "DEFAULT@SECLEVEL={!s}".format(self._sender_config.sec_level)
                    )

                context.check_hostname = self._sender_config.check_hostname

                if self._sender_config.verify_mode is not None:
                    context.verify_mode = self._sender_config.verify_mode

                context.load_cert_chain(
                    keyfile=self._sender_config.key, certfile=self._sender_config.cert
                )
                self.socket = context.wrap_socket(
                    self.socket, server_hostname=self._sender_config.address[0]
                )
            else:
                self.socket = ssl.wrap_socket(
                    self.socket, ssl_version=ssl.PROTOCOL_TLS, cert_reqs=ssl.CERT_NONE
                )

            self.socket.connect(self._sender_config.address)
            self.last_message = int(time.time())
            self.reconnection += 1
            if self.debug:
                self.logger.debug(
                    "Conected to %s|%s" % (repr(self.socket.getpeername()), str(self.reconnection))
                )
            self.timestart = int(round(time.time() * 1000))
            self.socket.setblocking(False)

        except socket.error as error:
            self.close()
            raise DevoSenderException(
                ERROR_MSGS.SSL_CONN_ESTABLISHMENT_SOCKET % str(error)
            ) from error

    def info(self, msg):
        """
        When Sender its a logger handler, this function its used to send
        "info" log
        :param msg: the msg to log
        :return:
        """
        self.send(tag=self.logging.get("tag"), msg=msg)

    # TODO: Deprecated
    def set_sec_level(self, sec_level=None):
        """
        Set sec_level of SSL Context:

        :param sec_level: sec_level value
        :return
        """
        self._sender_config.sec_level = sec_level

    # TODO: Deprecated
    def set_verify_mode(self, verify_mode=None):
        """
        Set verify_mode of SSL Context:

        ssl.CERT_NONE = 0
        ssl.CERT_OPTIONAL = 1
        ssl.CERT_REQUIRED = 2

        :param verify_mode: verify mode value
        :return
        """
        self._sender_config.verify_mode = verify_mode

    # TODO: Deprecated
    def set_check_hostname(self, check_hostname=True):
        """
        Set check_hostname of SSL Context:

        :param check_hostname: check_hostname value. Default True
        :return
        """
        self._sender_config.check_hostname = check_hostname

    def buffer_size(self, size=19500):
        """
        Set buffer size for Sender:

        :param size: New size of buffer. Default 19500
        :return True or False
        """
        try:
            self.buffer.length = size
            return True
        except Exception:
            return False

    def compression_level(self, cl=-1):
        """
        Set compression level for zipped data

        compression_level is an integer from 0 to 9 or -1
        controlling the level of compression;
        1 (Z_BEST_SPEED) is the fastest and produces the lower compression,
        9 (Z_BEST_COMPRESSION) is the slowest and produces the highest
        compression.
        0 (Z_NO_COMPRESSION) has no compression.
        The default value is -1 (Z_DEFAULT_COMPRESSION).

        Z_DEFAULT_COMPRESSION represents a default compromise between
        speed and compression (currently equivalent to level 6).
        :param cl: (Compression_level). Default -1

        :return True or False
        """
        try:
            self.buffer.compression_level = cl
            return True
        except Exception:
            return False

    def __status(self):
        """
        View Socket status, check if it's open
        """
        timeit = int(round(time.time() * 1000)) - self.timestart
        if self.socket is None:
            return False

        if self.socket_max_connection < timeit:
            self.close()
            return False

        # If there is no activity (connection or message sent) for an amount of time bigger
        # then the inactivity timeout, the balancer may have already close the connection.
        # Close it and reconnect.
        if int(time.time()) - self.last_message > self.inactivity_timeout:
            self.close()
            return False

        # If no data, EOF and channel is closed
        if self.__check_EOF():
            # Restart connection
            self.close()
            return False

        return True

    def close(self):
        """
        Forces socket closure
        """
        if self.socket is not None:
            try:
                self.socket.shutdown(SHUT_WR)
                self.__wait_for_EOF()
            except Exception:  # Try else continue
                logging.warning(ERROR_MSGS.CLOSING_ERROR)
            finally:
                self.socket.close()
                self.socket = None

    @staticmethod
    def __encode_multiline(record):
        try:
            record = Sender.__encode_record(record)
            return b"%d %s" % (len(record), record)
        except Exception as error:
            raise DevoSenderException(ERROR_MSGS.MULTILINE_SENDING_ERROR % str(error)) from error

    @staticmethod
    def __encode_record(record):
        """
        Class for encode the record for correct send
        :param record: the record to encode
        :return: record encoded for PY3
        """
        if not isinstance(record, bytes):
            return record.encode("utf-8")
        return record

    def __send_oc(self, record):
        msg_size = len(record)
        sent = 0
        total = int(msg_size / 4096)
        if msg_size % 4096 > 0:
            total += 1
        for iteration in range(0, total):
            part = record[int(iteration * 4096) : int((iteration + 1) * 4096)]
            self.__sendall(part)
            self.last_message = int(time.time())
            sent += len(part)
        if sent == 0:
            raise DevoSenderException(ERROR_MSGS.SEND_ERROR)
        return sent

    def __sendall(self, content):
        """
        Send content to endpoint dealing with blocking socket and SSL wrapper
        :param content: The content to be sent as event
        :raises DevoSenderException: if data cannot be sent or timeout is reached before sending it
        :return: No expected return
        """
        then = time.time()
        # Is the channel ready for writing?
        if select.select([], [self.socket], [], self.socket_timeout)[1]:
            while True:
                try:
                    # Write it
                    if self.socket.sendall(content) is not None:
                        raise DevoSenderException(str(ERROR_MSGS.SEND_ERROR))
                    else:
                        return
                except BlockingIOError as exc:
                    # This is not blocking socket
                    if exc.errno == errno.ECONNRESET:
                        # A TCP RST implies error in channel
                        raise IOError("Connection reset by endpoint") from exc
                    elif exc.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                        # Any other error but EAGAIN and EWOULDBLOCK here
                        raise IOError("Error while accessing socket") from exc
                    else:
                        # errno.EAGAIN means nothing to get, but socket working
                        pass
                except SSLWantWriteError:
                    # If the data is ready at socket OS level but not at
                    # SSL wrapper level, this exception may raise
                    pass
                # Try while timeout not reached
                if time.time() - self.socket_timeout >= then:
                    raise DevoSenderException(ERROR_MSGS.ERROR_AFTER_TIMEOUT)
        else:
            raise DevoSenderException(ERROR_MSGS.ERROR_AFTER_TIMEOUT)

    def __check_EOF(self):
        """
        Checks for EOF of the downstream channell to check whether endpoint closed connection
        If the channel was closed by the other endpoint (ingestion balancer)
        the reading of the download channel will return EOF. This is
        checked by reading a ready buffer but getting no data, empty bytes
        :return: Whether the EOF is detected in downstream (True) or not (False)
        """
        # Is the channel ready for reading?
        if select.select([self.socket], [], [], 0)[0]:
            while True:
                try:
                    # Read it
                    buf = self.socket.recv(1)
                    # If no data, EOF and channel is closed
                    return buf == b""
                except BlockingIOError as exc:
                    # This is not blocking socket
                    if exc.errno == errno.ECONNRESET:
                        # A TCP RST implies error in channel
                        raise IOError("Connection reset by endpoint") from exc
                    elif exc.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                        # Any other error but EAGAIN and EWOULDBLOCK here
                        raise IOError("Error while accessing socket") from exc
                    else:
                        # errno.EAGAIN means nothing to get, but socket working
                        # Nothing to read, everything is ok
                        return False
                except SSLWantReadError:
                    # If the data is ready at socket OS level but not at
                    # SSL wrapper level, this exception may raise
                    # Nothing to read, everything is ok
                    return False
        else:
            return False

    def __wait_for_EOF(self):
        """
        Wait for the endpoint to close the downstream channel after client closed the upstream one
        The downstream channel is closed by the other endpoint, ingestion balancer,
        by sending EOF. This is checked by reading a ready buffer but getting no data, empty bytes
        :raises DevoSenderException: if timeout is reached before sending it
        :return: Array of bytes with all the data send by endpoint until closing
        """
        then = time.time()
        # Wait for the channel to be ready for reading (with timeout)
        if select.select([self.socket], [], [], self.socket_timeout)[0]:
            bytes = bytearray()
            while True:
                try:
                    # Read it
                    buf = self.socket.recv(1)
                    # If no data, EOF and channel is closed
                    if buf == b"":
                        return bytes
                    else:
                        bytes.extend(buf)
                except BlockingIOError as exc:
                    # This is not blocking socket
                    if exc.errno == errno.ECONNRESET:
                        # A TCP RST implies error in channel
                        raise IOError("Connection reset by endpoint") from exc
                    elif exc.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                        # Any other error but EAGAIN and EWOULDBLOCK here
                        raise IOError("Error while accessing socket") from exc
                    else:
                        # errno.EAGAIN means nothing to get, but socket working
                        pass
                except SSLWantReadError:
                    # If the data is ready at socket OS level but not at
                    # SSL wrapper level, this exception may raise
                    pass
                # Try while timeout not reached
                if time.time() - self.socket_timeout >= then:
                    raise DevoSenderException(ERROR_MSGS.ERROR_AFTER_TIMEOUT)
        else:
            raise DevoSenderException(ERROR_MSGS.ERROR_AFTER_TIMEOUT)

    def send_raw(self, record, multiline=False, zip=False):
        """
        Send raw messages to the collector

        >>>con.send_raw('<14>Jan  1 00:00:00 MacBook-Pro-de-X.local'
        ...             'my.app.devo_sender.test: txt test')

        """
        try:
            if not self.__status():
                self.__connect()

            if self.socket:
                try:
                    if not multiline and not zip:
                        msg = self.__encode_record(record)
                        sent = len(msg)
                        self.__sendall(msg)
                        self.last_message = int(time.time())
                        return 1
                    if multiline:
                        record = self.__encode_multiline(record)

                    sent = self.__send_oc(record)
                    if sent:
                        return 1
                    return 0
                except socket.error as error:
                    self.close()
                    raise DevoSenderException(ERROR_MSGS.SOCKET_ERROR % str(error)) from error
                finally:
                    if self.debug:
                        self.logger.debug("sent|%d|size|%d|msg|%s" % (sent, len(record), record))
            raise DevoSenderException(ERROR_MSGS.SOCKET_CANT_CONNECT_UNKNOWN_ERROR)
        except DevoSenderException:
            raise
        except Exception as error:
            raise DevoSenderException(ERROR_MSGS.RAW_SENDING_ERROR % str(error)) from error

    @staticmethod
    def compose_mem(tag, **kwargs):
        """
        Creates the raw message header. If it is in real time it memorizes
        the header because it will be static.

        :param tag: table name
        :param kwargs: log_format -> Log format to send
        :param kwargs: facility -> facility user
        :param kwargs: severity -> severity info
        :param kwargs: hostname -> set hostname machine
        :param kwargs: date -> String Date format '%Y-%m-%d %H%M%S'
        :return: raw message header

        >>>con.compose_mem(tag='my.app.devo_sender.test')
        >>>'<14>Jan  1 00:00:00 MacBook-Pro-de-XXX-2.local'

        See Also:
            send

        """
        facility = kwargs.get("facility", FACILITY_USER)
        severity = kwargs.get("severity", SEVERITY_INFO)
        if kwargs.get("bytes", False):
            date = kwargs.get("date", b"Jan  1 00:00:00")
            hostname = kwargs.get("hostname", socket.gethostname().encode("utf-8"))
            log_format = kwargs.get("log_format", FORMAT_MY_BYTES)
        else:
            date = kwargs.get("date", "Jan  1 00:00:00")
            hostname = kwargs.get("hostname", socket.gethostname())
            log_format = kwargs.get("log_format", FORMAT_MY)

        return log_format % ((facility * 8) + severity, date, hostname, tag)

    def send(self, tag, msg, **kwargs):
        """
        Creates the raw message and send.

        :param tag: table name
        :param msg: Message to send
        :param kwargs: log_format -> Log format to send
        :param kwargs: facility -> facility user
        :param kwargs: severity -> severity info
        :param kwargs: hostname -> set hostname machine
        :param kwargs: multiline -> send multiline msg
        :param kwargs: zip -> send it zipped
        :param kwargs: date -> String Date format '%Y-%m-%d %H%M%S'


        >>>con.send(tag='my.app.devo_sender.test', msg='test of msg')
        See Also:
            send_raw
        """
        if isinstance(msg, bytes):
            return self.send_bytes(tag, msg, **kwargs)
        return self.send_str(tag, msg, **kwargs)

    def send_str(self, tag, msg, **kwargs):
        """
        Send function when str, sure py 27. Cant be zip
        """
        if msg[-1:] != "\n":
            msg += "\n"

        msg = COMPOSE % (self.compose_mem(tag, **kwargs), msg)
        return self.send_raw(msg, multiline=kwargs.get("multiline", False))

    def send_bytes(self, tag, msg, **kwargs):
        """
        Send function when bytes, sure py3x. Can be zipped
        """
        msg = COMPOSE_BYTES % (self.compose_mem(tag, bytes=True, **kwargs), msg)
        if kwargs.get("zip", False):
            return self.fill_buffer(msg)

        if msg[-1:] != b"\n":
            msg += b"\n"

        return self.send_raw(msg, multiline=kwargs.get("multiline", False))

    def fill_buffer(self, msg):
        """
        Internal method for fill buffer for be zipped and sent
        :param msg: bytes
        :return: None
        """
        if msg[-1:] != b"\n":
            msg += b"\n"

        self.buffer.text_buffer += msg
        self.buffer.events += 1
        if len(self.buffer.text_buffer) > self.buffer.length:
            return self.flush_buffer()
        return 0

    def flush_buffer(self):
        """
        Method for flush-send buffer, its zipped and sent now
        :return: None
        """
        if self.buffer.text_buffer:
            try:
                compressor = zlib.compressobj(self.buffer.compression_level, zlib.DEFLATED, 31)
                record = compressor.compress(self.buffer.text_buffer) + compressor.flush()
                if self.send_raw(record, zip=True):
                    return self.buffer.events
                return 0
            except Exception as error:
                raise DevoSenderException(ERROR_MSGS.FLUSHING_BUFFER_ERROR) from error
            finally:
                self.buffer.text_buffer = b""
                self.buffer.events = 0
        return 0

    @staticmethod
    def for_logging(config=None, con_type=None, tag=None, level=None):
        """Function for create Sender object from config file to use in
        logging handler
        :param config: config Devo file
        :param con_type: type of connection
        :param tag: tag for the table
        :param level: level of logger
        :param formatter: log formatter
        :return: Sender object
        """
        con = Sender(config=config, con_type=con_type)
        if tag:
            con.logging["tag"] = tag
        elif isinstance(config, dict):
            con.logging["tag"] = config.get("tag", "my.app.log")
        else:
            con.logging["tag"] = "my.app.log"

        if level:
            con.logging["level"] = level
        elif isinstance(config, dict):
            con.logging["level"] = config.get("verbose_level", 10)
        else:
            con.logging["level"] = logging.INFO

        con.logger.setLevel(con.logging.get("level"))

        return con

    @staticmethod
    def _from_dict(config=None, con_type=None):
        """Function for create Sender config object from dict file
        :param config: config Devo file
        :param con_type: type of connection
        :param logger: logger handler, default None
        :return: Sender object
        """
        if con_type:
            connection_type = con_type
        elif "type" in config.keys():
            connection_type = config["type"]
        else:
            connection_type = "SSL"

        address = config.get("address", None)

        if not address:
            raise DevoSenderException(ERROR_MSGS.NO_ADDRESS)

        if not isinstance(address, tuple):
            address = (address, int(config.get("port", 443)))

        if connection_type == "SSL":
            return SenderConfigSSL(
                address=address,
                key=config.get("key", None),
                cert=config.get("cert", None),
                chain=config.get("chain", None),
                pkcs=config.get("pkcs", None),
                sec_level=config.get("sec_level", None),
                verify_mode=config.get("verify_mode", None),
                verify_config=config.get("verify_config", False),
                check_hostname=config.get("check_hostname", True),
            )

        return SenderConfigTCP(address=address)

    def emit(self, record):
        """
        If used as an handler it will redirect the logs to the send function.

        In order to be a proper logger handler it required to override the
        emit function.
        :param record -> String that contains the message to be send and it's
        characteristics such as severity etc.
        :return: raw message header

        See Also:
            send
        """
        try:
            msg = self.format(record)
            msg += "\000"
            try:
                severity = priority_map.get(record.levelname, record.levelno)
            except AttributeError:
                severity = priority_map.get("INFO")
            self.send(
                tag=self.logging.get("tag", "test.keep.free"),
                msg=msg,
                facility=self.logging.get("level", FACILITY_USER),
                severity=severity,
            )
        except Exception:
            self.handleError(record)


def open_file(file, mode="r", encoding="utf-8"):
    """
    Helper class to open file whenever is provided as `Path` or `str` type
    :param file File to open
    :param mode Opening mode
    :param encoding Encoding of content
    """
    if isinstance(file, Path):
        return file.open(mode=mode, encoding=encoding if not mode.endswith("b") else None)
    elif isinstance(file, str):
        return open(file, mode=mode, encoding=encoding if not mode.endswith("b") else None)
    else:
        raise DevoSenderException(ERROR_MSGS.WRONG_FILE_TYPE % str(type(file)))
