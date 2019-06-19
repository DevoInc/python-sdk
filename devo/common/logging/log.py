# -*- coding: utf-8 -*-
""" Generic function to logging events in Devo SDK """
import os
import logging
from logging.handlers import RotatingFileHandler


def get_log(path_base="./",
            file_name="history.log",
            msg_format="'%(asctime)s %(levelname)s %(message)s'",
            name="log",
            max_size=2097152,
            backup_count=5,
            level=logging.DEBUG):
    """Initialize logger for self process log

    :return: Log object
    """

    full_path = os.path.join(path_base, file_name)
    if not os.path.exists(os.path.dirname(full_path)):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

    logger = logging.getLogger(name)
    logger.addHandler(set_handler(full_path, msg_format, max_size, backup_count))
    logger.setLevel(level)
    return logger


def set_formatter(msg_format):
    """Initialize logger formatter

    :return: Formatter object
    """
    return logging.Formatter(msg_format)


def set_handler(path, msg_format, max_size, backup_count):
    """Initialize handler for logger

    :return: RotatingFileHandler object
    """
    handler = RotatingFileHandler(path, maxBytes=max_size,
                                  backupCount=backup_count)
    handler.setFormatter(set_formatter(msg_format))
    return handler
