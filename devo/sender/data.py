# -*- coding: utf-8 -*-
""" File to group all the classes and functions related to the connection
and sending of data to Devo """
import logging
import socket
import ssl
import sys
import time
import zlib

from .transformsyslog import FORMAT_MY, FORMAT_MY_BYTES, \
    FACILITY_USER, SEVERITY_INFO, COMPOSE, \
    COMPOSE_BYTES, priority_map

PY3 = sys.version_info[0] > 2
PY33 = sys.version_info[0] == 3 and sys.version_info[1] == 3
PY34 = sys.version_info[0] == 3 and sys.version_info[1] == 4
PYPY = hasattr(sys, 'pypy_version_info')


class DevoSenderException(Exception):
    """ Default Devo Sender Exception """
    pass


class SenderConfigSSL:
    """
    Configuration SSL class.

    :param address: (str) Server address
    :param port: (int) Server port
    :param key: (str) key src file
    :param cert:  (str) cert src file
    :param chain:  (str) chain src file
    :param timeout: (int) Time in seconds to restart connection
    :param cert_reqs: (bool) Use certs in SSL connection

    >>>sender_config = SenderConfigSSL(address=SERVER, port=PORT,
    ...                                cert_reqs=True, key=KEY,
    ...                                cert=CERT, chain=CHAIN)

    See Also:
        Sender

    """

    def __init__(self, address=None, port=None, key=None, debug=False,
                 cert=None, chain=None, timeout=300, cert_reqs=True,
                 **kwargs):
        try:
            self.timeout = timeout * 1000
            self.address = (address, int(port))
            self.cert_reqs = cert_reqs
            self.debug = debug
            if cert_reqs:
                self.key = key
                self.cert = cert
                self.chain = chain
            self.hostname = socket.gethostname()
            self.type = 'SSL'
        except Exception as error:
            raise DevoSenderException(
                "Devo-SenderConfigSSL|Can't create SSL config: "
                "%s" % str(error))


class SenderConfigTCP:
    """
    Configuration TCP class.

    :param address:(str) Server address
    :param port: (int) Server port
    :param timeout: (int) Time in seconds to restart connection

    >>>sender_config = SenderConfigTCP(address=SERVER, port=PORT)

    See Also:
        Sender

    """

    def __init__(self, address=None, port=None, debug=False, timeout=300,
                 **kwargs):

        try:
            self.timeout = timeout * 1000
            self.address = (address, int(port))
            self.hostname = socket.gethostname()
            self.type = 'TCP'
            self.debug = debug
        except Exception as error:
            raise DevoSenderException(
                "DevoSenderConfigTCP|Can't create TCP config: "
                "%s" % str(error))


class Sender(logging.Handler):
    """
    Class that manages the connection to the data collector

    :param config: Config class, you can send params in kwargs
    :param verbose_level: Logger verbose level. Default level INFO
    :param sockettimeout: Socket timeout in minutes
    :param logger: logger. Default sys.console

    >>>con = Sender(sender_config)

    """
    def __init__(self, config=None, **kwargs):
        if not config:
            config = SenderConfigTCP(**kwargs) if kwargs.get('type') == "TCP" \
                else SenderConfigSSL(**kwargs) if kwargs.get('type') == "SSL" \
                else None

        if not config:
            raise DevoSenderException("Problems with args passed to Sender")

        facility = kwargs.get('facility', FACILITY_USER)
        verbose_level = kwargs.get('verbose_level', "INFO")
        sockettimeout = kwargs.get('sockettimeout', 5)
        logger = kwargs.get('logger', None)
        tag = kwargs.get('tag', None)


        logging.Handler.__init__(self)
        self.logger = self.__set_logger(verbose_level) if logger is None \
            else logger

        self._logger_tag = tag
        self.socket = None
        self._sender_config = config
        self.reconection = 0
        self.sockettimeout = sockettimeout
        self.max_zip_buffer = 19500
        self.compression_level = -1
        self.zip_buffer = b''
        self.composed_msg = b''
        self.facility = facility

        if self._sender_config.type == 'SSL':
            self.__connect_ssl()

        if self._sender_config.type == 'TCP':
            self.__connect_tcpsocket()

    def __connect(self):
        if self._sender_config.type == 'SSL':
            self.__connect_ssl()
        if self._sender_config.type == 'TCP':
            self.__connect_tcpsocket()

    def __connect_tcpsocket(self):
        """
        Connect to TCP socket
        :return:
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.sockettimeout)
        try:
            self.socket.connect(self._sender_config.address)
        except socket.error as error:
            self.close()
            raise DevoSenderException(
                "Devo-Sender|TCP conn establishment socket error: %s" % str(error))

        self.timestart = int(round(time.time() * 1000))

    @staticmethod
    def __set_logger(verbose_level):
        logger = logging.getLogger('DevoSender')
        logger.setLevel(verbose_level.upper())
        if not logger.handlers:
            sender_logger = logging.StreamHandler(sys.stdout)
            sender_logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s|%(levelname)s|%(message)s')
            sender_logger.setFormatter(formatter)
            logger.addHandler(sender_logger)
        return logger

    def __connect_ssl(self):
        """
        Connect to SSL socket.

        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.sockettimeout)

        try:
            try:
                if self._sender_config.cert_reqs:
                    self.socket = ssl.wrap_socket(
                        self.socket,
                        keyfile=self._sender_config.key,
                        certfile=self._sender_config.cert,
                        ca_certs=self._sender_config.chain,
                        cert_reqs=ssl.CERT_REQUIRED)
                else:
                    self.socket = ssl.wrap_socket(self.socket,
                                                  cert_reqs=ssl.CERT_NONE)
            except ssl.SSLError:
                raise ssl.SSLError
            self.socket.connect(self._sender_config.address)
            self.reconection += 1
            self.logger.debug('Devo-Sender|Conected to %s|%s'
                              % (repr(self.socket.getpeername())
                                 , str(self.reconection)))
            self.timestart = int(round(time.time() * 1000))

        except socket.error as error:
            self.close()
            raise DevoSenderException(
                "Devo-Sender|SSL conn establishment socket error: %s" % str(error))


    def info(self, msg):
        """
        When Sender its a logger handler, this function its used to send
        "info" log
        :param msg: the msg to log
        :return:
        """
        self.send(tag=self._logger_tag, msg=msg)

    def __status(self):
        """
        View Socket status, check if it's open
        """
        timeit = int(round(time.time() * 1000)) - self.timestart
        if self.socket is None:
            return False
        if self._sender_config.timeout < timeit:
            self.close()
            return False
        return True

    def close(self):
        """
        Forces socket closure
        """
        if self.zip_buffer:
            self.flush_buffer()

        if self.socket is not None:
            self.socket.close()
            self.socket = None

    @staticmethod
    def __encode_record(record):
        """
        Class for encode the record for correct send
        :param record: the record to encode
        :return: record encoded for PY3 or PY2
        """
        if PY3:
            if not isinstance(record, bytes):
                return record.encode('utf-8')
        else:
            if not isinstance(record, str):
                return bytes(record.encode("utf-8"))

        return record

    def send_raw(self, record, multiline=False, zip=False):
        """
        Send raw messages to the collector

        >>>con.send_raw('<14>Jan  1 00:00:00 MacBook-Pro-de-X.local'
        ...             'my.app.devo_sender.test: txt Prueba')

        """
        try:
            if not self.__status():
                self.__connect()

            if self.socket:
                try:
                    if not multiline and not zip:
                        sent = self.socket.send(self.__encode_record(record))
                    else:
                        if multiline:
                            record = self.__encode_record(record)

                        msg_size = len(record)
                        sent = 0
                        total = int(msg_size / 4096)
                        if msg_size % 4096 > 0:
                            total += 1
                        for iteration in range(0, total):
                            sent += self.socket.send(
                                record[int(iteration * 4096):
                                       int((iteration + 1) * 4096)])

                        if sent == 0:
                            raise DevoSenderException("Devo-Sender|Send error")

                    if self._sender_config.debug:
                        self.logger.debug('sent|%d|size|%d|msg|%s' %
                                          (sent, len(record), record))
                except socket.error:
                    self.close()
                    raise DevoSenderException(
                        "Devo-Sender|Socket error: %s" % str(socket.error))
        except Exception as error:
            raise error

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
        facility = kwargs.get('facility', FACILITY_USER)
        severity = kwargs.get('severity', SEVERITY_INFO)
        if kwargs.get('bytes', False):
            date = kwargs.get('date', b'Jan  1 00:00:00')
            hostname = kwargs.get('hostname', socket.gethostname().encode("utf-8"))
            log_format = kwargs.get('log_format', FORMAT_MY_BYTES)
        else:
            date = kwargs.get('date', 'Jan  1 00:00:00')
            hostname = kwargs.get('hostname', socket.gethostname())
            log_format = kwargs.get('log_format', FORMAT_MY)

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
        :param kwargs: date -> String Date format '%Y-%m-%d %H%M%S'


        >>>con.send(tag='my.app.devo_sender.test', msg='prueba mensaje')
        See Also:
            send_raw
        """
        if isinstance(msg, bytes):
            self.send_bytes(tag, msg, **kwargs)
        else:
            self.send_str(tag, msg, **kwargs)

    def send_str(self, tag, msg, **kwargs):
        """
        Send function when str, sure py 27. Cant be zipped
        """
        if msg[-1:] != "\n":
            msg += "\n"

        msg = COMPOSE % (self.compose_mem(tag, **kwargs), msg)
        self.send_raw(msg, multiline=kwargs.get('multiline', False))

    def send_bytes(self, tag, msg, **kwargs):
        """
        Send function when bytes, sure py3x. Can be zipped
        """
        msg = COMPOSE_BYTES % (self.compose_mem(tag, bytes=True, **kwargs), msg)
        if kwargs.get('zip', False):
            self.fill_buffer(msg)
        else:
            if msg[-1:] != b"\n":
                msg += b"\n"

            self.send_raw(msg, multiline=kwargs.get('multiline', False))

    def fill_buffer(self, msg):
        """
        Internal method for fill buffer for be zipped and sended
        :param msg: bytes
        :return: None
        """
        if msg[-1:] != b"\n":
            msg += b"\n"

        self.zip_buffer += msg
        if len(self.zip_buffer) > self.max_zip_buffer:
            self.flush_buffer()

    def flush_buffer(self):
        """
        Method for flush-send buffer, its zipped and sended now
        :return: None
        """
        if self.zip_buffer:
            compressor = zlib.compressobj(self.compression_level,
                                          zlib.DEFLATED, 31)
            record = compressor.compress(self.zip_buffer) + compressor.flush()
            self.send_raw(record, zip=True)
            self.zip_buffer = b''

    def set_logger_tag(self, tag):
        """
        When Sender its used for logging, you can set the tag for default
        :param tag: table tag
        :return:
        """
        self._logger_tag = tag

    @staticmethod
    def for_logging(config, con_type="SSL", tag="test.drop.free"):
        """ Function for create Sender object from config file to use in
        logging handler
        :param config: config Devo file
        :param con_type: type of connection
        :param tag: tag for the table
        :return: Sender object
        """
        con = Sender.from_config(config, con_type)
        con.set_logger_tag(tag)
        con.set_level = 7
        return con

    @staticmethod
    def from_config(config, con_type=None, logger=None):
        """ Function for create Sender object from config file
        :param config: config Devo file
        :param con_type: type of connection
        :param logger: logger handler, default None
        :return: Sender object
        """
        con_type = config['type'].upper() if "type" in config and con_type is not None else "SSL"
        cert_reqs = config['cert_reqs'] if "cert_reqs" in config else True

        if con_type == "SSL":
            if cert_reqs:
                return Sender(
                    SenderConfigSSL(
                        address=config['address'],
                        port=int(config['port']),
                        cert_reqs=True,
                        key=config['key'],
                        cert=config['cert'],
                        chain=config['chain']
                    ), logger=logger
                )
            return Sender(
                SenderConfigSSL(
                    address=config['address'],
                    port=int(config['port']),
                    cert_reqs=False
                ), logger=logger
            )

        if con_type == "TCP":
            return Sender(
                SenderConfigTCP(
                    address=config['address'],
                    port=int(config['port'])
                ), logger=logger
            )
        raise DevoSenderException("Devo-Sender|Type must be 'SSL' or 'TCP'")

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
            msg += '\000'
            self.send(self._logger_tag, msg, facility=self.facility,
                      severity=priority_map.get(record.levelname, "info"))
        except Exception:
            self.handleError(record)
