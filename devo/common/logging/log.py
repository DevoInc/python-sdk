# -*- coding: utf-8 -*-
""" Generic function to logging events in Devo SDK """
import os
import sys
import logging
from logging.handlers import RotatingFileHandler


def get_log(name="log", level=None, handler=None):
    """Initialize logger for self process
    :TODO v4.0.0: In version 4.0 delete level option for get_log
    :return: Log object
    """
    logger = logging.getLogger(name)
    if handler is None:
        handler = get_rotating_file_handler(level=None if level is None
                                            else level)
        logger.addHandler(handler)
    elif isinstance(handler, list):
        for simple_handler in handler:
            if level is not None:
                simple_handler.setLevel(level)
            logger.addHandler(simple_handler)
    else:
        logger.addHandler(handler)

    if level is not None:
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
                              backup_count=5,
                              level=logging.INFO):
    """Initialize rotating file handler for logger

    :return: RotatingFileHandler object
    """
    full_path = os.path.join(path, file_name)
    if not os.path.exists(os.path.dirname(full_path)):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

    handler = RotatingFileHandler(full_path, maxBytes=max_size,
                                  backupCount=backup_count)
    handler.setFormatter(set_formatter(msg_format))
    if level is not None:
        handler.setLevel(level)
    return handler


def get_stream_handler(dest=sys.stdout,
                       msg_format='%(asctime)s|%(levelname)s|%(message)s',
                       level=logging.INFO):
    """Initialize stream handlerhandler for logger
    :return: StreamHandler object
    """
    handler = logging.StreamHandler(dest)
    handler.setFormatter(set_formatter(msg_format))
    if level is not None:
        handler.setLevel(level)
    return handler
