# -*- coding: utf-8 -*-
"""Defaults proccessors of API data."""
import json


def proc_default(data):
    """
    Return json object, verify if is a multiline resp or not
    :param data: line from Serrea APi
    :return: json object
    """
    return json.loads(data) if data else None


def proc_json(data):
    """
    Return json object, verify if is a multiline resp or not
    :param data: data from Serrea APi
    :return: map object in python 3, list in python 2
    """
    return map(lambda x: (json.loads(x) if x else None),
               data.split("\r\n"))
