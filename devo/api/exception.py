import json
import time


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
