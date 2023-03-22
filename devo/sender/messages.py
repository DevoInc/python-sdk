from enum import Enum


class ERROR_MSGS(str, Enum):
    def __str__(self):
        return str(self.value)

    WRONG_FILE_TYPE = "'%s' is not a valid type to be opened as a file",
    ADDRESS_TUPLE = "Devo-SenderConfigSSL| address must be a tuple (\"hostname\", int(port))'",
    WRONG_SSL_CONFIG = "Devo-SenderConfigSSL|Can't create SSL config: %s",
    CONFIG_FILE_NOT_FOUND = "Error in the configuration, %s is not a file or the path does not" \
                            " exist",
    CANT_READ_CONFIG_FILE = "Error in the configuration %s can't be read\noriginal error: %s",
    CONFIG_FILE_PROBLEM = "Error in the configuration, %s problem related to: %s",
    KEY_NOT_COMPATIBLE_WITH_CERT = "Error in the configuration, the key: %s is not compatible" \
                                   " with the cert: %s\noriginal error: %s",
    CHAIN_NOT_COMPATIBLE_WITH_CERT = "Error in config, the chain: %s is not compatible with the" \
                                     " certificate: %s\noriginal error: %s",
    TIMEOUT_RELATED_TO_AN_INCORRECT_ADDRESS_PORT = "Possible error in config, a timeout could be" \
                                                   " related to an incorrect address/port: %s\n" \
                                                   "original error: %s",
    INCORRECT_ADDRESS_PORT = "Error in config, incorrect address/port: %s\noriginal error: %s",
    CERTIFICATE_IN_ADDRESS_IS_NOT_COMPATIBLE = "Error in config, the certificate in the address:" \
                                               " %s is not compatible with: %s",
    ADDRESS_MUST_BE_A_TUPLE = "Devo-SenderConfigSSL| address must be a tuple '(\"hostname\"," \
                              " int(port))'",
    CANT_CREATE_TCP_CONFIG = "DevoSenderConfigTCP|Can't create TCP config: %s",
    PROBLEMS_WITH_SENDER_ARGS = "Problems with args passed to Sender",
    TCP_CONN_ESTABLISHMENT_SOCKET = "TCP conn establishment socket error: %s",
    SSL_CONN_ESTABLISHMENT_SOCKET = "SSL conn establishment socket error: %s",
    PFX_CERTIFICATE_READ_FAILED = "PFX Certificate read failed: %s",
    SEND_ERROR = "Send error",
    SOCKET_ERROR = "Socket error: %s",
    SOCKET_CANT_CONNECT_UNKNOWN_ERROR = "Socket cant connect: unknown error",
    NO_ADDRESS = "No address",
    MULTILINE_SENDING_ERROR = "Error sending multiline event: %s",
    RAW_SENDING_ERROR = "Error sending raw event: %s",
    CLOSING_ERROR = "Error closing connection"
    FLUSHING_BUFFER_ERROR = "Error flushing buffer"
