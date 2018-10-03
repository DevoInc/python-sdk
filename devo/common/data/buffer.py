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
    def __init__(self, buffer_max_size=1000):
        self.queue = Queue.Queue(maxsize=buffer_max_size)
        self.thread = None
        self.temp = None
        self.error = None

    def is_alive(self):
        return self.thread.isAlive()

    def create_thread(self, target, kwargs):
        """ Function for create one separate thread for Queue"""
        self.thread = Thread(target=target, kwargs=kwargs)
        self.thread.setDaemon(True)

    def start(self):
        """ Function for call the threat start """
        self.thread.start()

    def get(self, proccessor=None, block=True, timeout=None):
        """ Get one proccessed item from the queue """
        if not self.error:
            return proccessor(self.queue.get(block=block, timeout=timeout)) \
                if proccessor is not None \
                else self.queue.get(block=block, timeout=timeout)
        raise DevoBufferException("Devo-Buffer|%s" % str(self.error))

    def proccess_first_line(self, data):
        """ Proccess first line of the Query call (For delete headers) """
        if not isinstance(data, str):
            data = data.decode('utf8')

        if "200 OK" in data.split("\r\n\r\n")[0]:
            self.proccess_recv(data[data.find("\r\n\r\n")+4:])
            return True, None

        self.error = data
        return False, data

    def size(self):
        """ Verify queue size """
        return self.queue.qsize()

    def proccess_recv(self, data):
        """ Proccess received data """
        if not isinstance(data, str):
            data = data.decode('utf8')

        data = data[data.find("\r\n") + 2:].split("\r\n ")

        data_len = len(data)
        if self.temp is not None:
            data[0] = self.temp + data[0]

        if len(data) > 1:
            for aux in range(0, data_len - 1):
                self.queue.put(data[aux].strip(), block=True)

        if data[data_len-1][-4:] == "\r\n\r\n":
            self.queue.put(data[data_len-1][:-4].strip(), block=True)
            self.temp = None
        else:
            self.temp = data[data_len-1][:-2].strip()
