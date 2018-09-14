# -*- coding: utf-8 -*-
""" Util for load generic config file in devo standars"""
import json


class Configuration(object):
    """
    Main class for load config files, and extract config objects
    """
    def __init__(self):
        self.cfg = dict()

    def load_json(self, path, section=None):
        """Load Json Configuration

        :param path: Path to the json file
        :param section: Section of the file if it have one
        """
        with open(path, 'r') as file_content:
            cfg = json.load(file_content)

        if section is not None:
            if section in cfg.keys():
                self.mix(cfg[section])
        else:
            self.mix(cfg)
        return self

    def load_default_json(self, section=None):
        """Load Json Configuration in ~/.devo.json

        :param section: Section of the file if it have one
        """
        with open("~/.devo.json", 'r') as file_content:
            cfg = json.load(file_content)

        if section is not None:
            if section in cfg.keys():
                self.secure_mix(cfg[section])
        else:
            self.secure_mix(cfg)
        return self

    @staticmethod
    def clean_cfg(cfg):
        """
        Clean self.cfg keys with None (CLI default values fix)
        """
        keys = list(cfg.keys())
        for key in keys:
            if cfg[key] is None:
                cfg.pop(key)

        return cfg

    def mix(self, cfg):
        """Mix configuration only if not None param (Override vars)

        :param cfg: Configuration to mix
        """
        cfg = self.clean_cfg(cfg)
        for key in cfg:
            self.cfg[key] = cfg[key]

    def secure_mix(self, cfg):
        """Mix configuration only if not None param and if not exist

        :param cfg: Configuration to mix
        """
        self.clean_cfg(cfg)
        for key in cfg:
            if key not in self.cfg.keys():
                self.cfg[key] = cfg[key]

    def get(self):
        """Get the configuration as dict

        :return: Return the configuration dict
        """
        return self.cfg

    def keys(self, prop):
        """Check if exist property and if not then set to None

        :param prop: Property to check
        """
        if prop not in self.cfg:
            return False
        return True

    #DEPRECATE THIS FOR 2.0
    def key_exist(self, prop):
        """Check if exist property and if not then set to None

        :param prop: Property to check
        """
        if prop not in self.cfg:
            return False
        return True

    def set(self, key_list, value):
        """ Set value of dict
         :param key_list: Key when save value, can be list to create depth key
         :param value: Value to save
        """
        if value:
            if not isinstance(key_list, list):
                key_list = [key_list]
            self.set_key_chain(self, key_list, value)

    @staticmethod
    def set_key_chain(aux_dict, key_list, value):
        """
        Auxiliar function to create subdicts into dicts, and save the value
        recursively
         :param aux_dict: aux_dict when you create dicts into dicts
         :param key_list: Actual key list for the loop
         :param value: Value to save
        """
        if len(key_list) == 1:
            aux_dict[key_list[0]] = value
        else:
            aux_dict[key_list[0]] = Configuration.set_key_chain(dict(),
                                                                key_list[1:],
                                                                value)
        return aux_dict
