# -*- coding: utf-8 -*-
"""Defaults proccessors of API data."""
import json


def proc_default():
    """
    Default processor: return data in str/bytes, after strip
    :return: data
    """
    return lambda data: data.strip()


def proc_bytes_to_str():
    return lambda data: data.strip() if isinstance(data, str) \
        else data.strip().decode("utf-8")


def proc_str_to_bytes():
    return lambda data: data.strip() if isinstance(data, bytes) \
        else data.strip().encode("utf-8")


def proc_json():
    """
    Return json object processor
    :return: json object
    """
    return lambda data: json.loads(data if isinstance(data, str)
                                   else data.decode("utf-8"))\
        if data else None


def proc_json_simple():
    """
    :return: json object
    """
    return proc_json()


def proc_json_compact_to_array():
    """
    :return: json object
    """
    return lambda data: proc_json()(data)['object']['d'] if data else None


def json_compact_simple_names(data):
    return [item for item in sorted(data, key=lambda x: data[x]['index'])]


def proc_json_compact_simple_to_jobj(names=None):
    return proc_json_compact_simple_to_array() if not names else \
        lambda data: dict(zip(names,
                              proc_json_compact_simple_to_array()(data))) \
            if data else {}


def proc_json_compact_simple_to_array():
    return lambda data: proc_json()(data)['d'] if data else []


def processors():
    """Return object with all functions availables"""
    return {
        "default": proc_default,
        "bytes_to_str": proc_bytes_to_str,
        "str_to_bytes": proc_str_to_bytes,
        "json": proc_json,
        "json_simple": proc_json_simple,
        "jsoncompact_to_array": proc_json_compact_to_array,
        "jsoncompactsimple_to_obj": proc_json_compact_simple_to_jobj,
        "jsoncompactsimple_to_array": proc_json_compact_simple_to_array,
        "json_compact_simple_names": json_compact_simple_names
    }
