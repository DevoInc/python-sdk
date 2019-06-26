# -*- coding: utf-8 -*-
""" Generic function to logging events in Devo SDK """
import os
import sys
import logging
from logging.handlers import RotatingFileHandler


def get_log(name="log", level=logging.DEBUG, handler=None):
    """Initialize logger for self process log
    :return: Log object
    """
    logger = logging.getLogger(name)
    logger.addHandler(get_rotating_file_handler()
                      if not handler else handler)
    logger.setLevel(level)
    return logger


def set_formatter(msg_format):
    """Initialize logger formatter

    :return: Formatter object
    """
    return logging.Formatter(msg_format)


def get_rotating_file_handler(path="./",
                              file_name="history.log",
                              msg_format='%(asctime)s|%(levelname)s|%(message)s',
                              max_size=2097152,
                              backup_count=5):
    """Initialize rotating file handler for logger

    :return: RotatingFileHandler object
    """
    full_path = os.path.join(path, file_name)
    if not os.path.exists(os.path.dirname(full_path)):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

    handler = RotatingFileHandler(full_path, maxBytes=max_size,
                                  backupCount=backup_count)
    handler.setFormatter(set_formatter(msg_format))
    return handler


def get_stream_handler(dest=sys.stdout,
                       msg_format='%(asctime)s|%(levelname)s|%(message)s'):
    """Initialize stream handlerhandler for logger
    :return: StreamHandler object
    """
    handler = logging.StreamHandler(dest)
    handler.setFormatter(set_formatter(msg_format))
    return handler
