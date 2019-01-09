# -*- coding: utf-8 -*-
"""Simple Buffer generic class for use of some package functions."""
from threading import Thread

try:
    import Queue
except ImportError:
    import queue as Queue


class DevoBufferException(Exception):
    """ Default Devo Client Exception """
    pass


class Buffer(object):
    """ Simple Buffer class """
    def __init__(self, buffer_max_size=1000, api_response="json/compact"):
        self.queue = Queue.Queue(maxsize=buffer_max_size)
        self.thread = None
        self.temp = ""
        self.temp_event = ""
        self.octet = 0
        self.error = None
        self.close = False
        self.timeout = None
        self.response_split = "\n" if api_response is "csv" else "\r\n"

    def is_alive(self):
        return self.thread.isAlive()

    def set_timeout(self, timeout):
        self.timeout = timeout

    def is_empty(self):
        return False if self.size() > 0 else True

    def create_thread(self, target, kwargs):
        """ Function for create one separate thread for Queue"""
        self.thread = Thread(target=target, kwargs=kwargs)
        self.thread.setDaemon(True)

    def start(self):
        """ Function for call the threat start """
        self.thread.start()

    def get(self, processor=None, block=True, timeout=None):
        """ Get one processed item from the queue """
        if timeout is None:
            timeout = self.timeout

        if not self.error:
            try:
                return processor(self.queue.get(block=block, timeout=timeout)) \
                    if processor is not None \
                    else self.queue.get(block=block, timeout=timeout)
            except Queue.Empty:
                self.close = True
        else:
            raise DevoBufferException("Devo-Buffer|%s" % str(self.error))

    def process_first_line(self, data):
        """ process first line of the Query call (For delete headers) """
        if not isinstance(data, str):
            data = data.decode('utf8')

        if "200 OK" in data.split("\r\n\r\n")[0]:
            return self.decode(data[data.find("\r\n\r\n")+4:]), None

        self.error = data
        return False, data

    def decode(self, data):
        if not isinstance(data, str):
            data = data.decode('utf8')
        return self.buffering(data)

    def buffering(self, data):
        if not self.octet:
            pointer = data.find("\r\n") + 2
            size = int(data[:pointer], 16)
            data = self.temp_event + data[pointer:]
            self.octet = len(self.temp_event) + size
            self.temp_event = ""

        if len(self.temp + data) < self.octet or \
                (not self.octet and not data.find("\r\n")):
            self.temp += data
            return not self.close

        data = self.temp + data
        self.temp = data[self.octet + 2:]
        return self.process_recv(data[:self.octet])

    def size(self):
        """ Verify queue size """
        return self.queue.qsize()

    def process_recv(self, data):
        """ process received data """
        data_list = data.strip().split(self.response_split)
        if data[-(len(self.response_split)):] != self.response_split:
            self.temp_event = data_list.pop()

        for aux in range(0, len(data_list)):
            self.queue.put(data_list[aux].strip(), block=True)

        self.octet = 0
        if len(self.temp.strip()):
            data = self.temp
            self.temp = ""
            if data.find("\r\n") == 0:
                data = data[2:]
            return self.buffering(data)
        return not self.close

    def close(self):
        self.close = True
