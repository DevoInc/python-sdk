# -*- coding: utf-8 -*-
""" Generic function to logging events in Devo SDK """
import logging
import os
from logging.handlers import RotatingFileHandler


def get_log(path_base="./",
            file_name="history.log",
            msg_format="'%(asctime)s %(levelname)s %(message)s'"):
    """Initialize logger for self process log

    :return: Log object
    """
    logger = logging.getLogger('log')
    logger.addHandler(set_handler(os.path.join(path_base, file_name), msg_format))
    logger.setLevel(logging.DEBUG)
    return logger


def set_formatter(msg_format):
    """Initialize logger formatter

    :return: Formatter object
    """
    return logging.Formatter(msg_format)


def set_handler(path, msg_format):
    """Initialize handler for logger

    :return: RotatingFileHandler object
    """
    handler = RotatingFileHandler(path, maxBytes=2097152, backupCount=5)
    handler.setFormatter(set_formatter(msg_format))
    return handler
