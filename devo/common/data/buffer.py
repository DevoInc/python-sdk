# -*- coding: utf-8 -*-
"""Simple Buffer generic class for use of some package functions."""
from threading import Thread
from sys import version_info


try:
    import Queue
except ImportError:
    import queue as Queue


class DevoBufferException(Exception):
    """ Default Devo Client Exception """


def clrf():
    """clrf character in"""
    return b"\r\n" if version_info[0] > 2 else "\r\n"


def get_response_split(api_response):
    """Get split for each event, if csv or other, and in bytes or str"""
    if version_info[0] > 2:
        return b"\n" if api_response == "csv" else b"\r\n"
    return "\n" if api_response == "csv" else "\r\n"


def empty():
    """Empty string in bytes or str if py2 or py3"""
    return bytes() if version_info[0] > 2 else str()


class Buffer:
    """ Simple Buffer class """
    def __init__(self, buffer_max_size=1000, api_response="json/compact"):
        self.queue = Queue.Queue(maxsize=buffer_max_size)
        self.thread = None
        self.temp = empty()
        self.temp_event = empty()
        self.response_split = get_response_split(api_response)
        self.clrf = clrf()
        self.octet = 0
        self.error = None
        self.close = False
        self.timeout = None
        self.api_response = api_response

    def is_alive(self):
        """Revise is buffer is alive"""
        return self.thread.isAlive()

    def set_timeout(self, timeout):
        """Set timeout for socket call"""
        self.timeout = timeout

    def is_empty(self):
        """Revise is buffer queue is empty"""
        return True if self.size() else False

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

        if version_info[0] > 2:
            response_ok = b"200 OK"
        else:
            response_ok = "200 OK"

        if response_ok in data.split(self.clrf+self.clrf)[0]:
            return self.buffering(data[data.find(self.clrf+self.clrf)+4:]), None

        self.error = data
        return False, data

    def buffering(self, data):
        """Saving temp date from system IO, waiting for all octet response"""
        if not self.octet:
            pointer = data.find(self.clrf) + 2
            size = int(data[:pointer], 16)
            data = self.temp_event + data[pointer:]
            self.octet = len(self.temp_event) + size
            self.temp_event = empty()

        if len(self.temp + data) < self.octet or \
                (not self.octet and not data.find(self.clrf)):
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

        for item in data_list:
            self.queue.put(item.strip(), block=True)

        self.octet = 0
        if len(self.temp.strip()):
            data = self.temp
            self.temp = empty()
            if data.find(self.clrf) == 0:
                data = data[2:]
            return self.buffering(data)
        return not self.close
