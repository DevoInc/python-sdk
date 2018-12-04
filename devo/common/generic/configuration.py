# -*- coding: utf-8 -*-
""" Util for load generic config file in devo standars"""
import json
import sys

class ConfigurationException(Exception):
    """ Default Configuration Exception """
    pass

class Configuration(object):
    """
    Main class for load config files, and extract config objects
    """
    def __init__(self):
        self.cfg = dict()

    def __load_cfg(self, cfg, section=None):
        """Load Configuration

        :param section: Section of the file if it have one
        :return: Returns a reference to the instance object
        """
        if section is not None:
            if section in cfg.keys():
                self.mix(cfg[section])
        else:
            self.mix(cfg)
        return self

    def load_json(self, path, section=None):
        """Load Json Configuration

        :param path: Path to the json file
        :param section: Section of the file if it have one
        :return: Returns a reference to the instance object
        """
        with open(path, 'r') as file_content:
            cfg = json.load(file_content)

        return self.__load_cfg(cfg, section)

    def load_yaml(self, path, section=None):
        """Load Yaml Configuration

        :param path: Path to the json file
        :param section: Section of the file if it have one
        :return: Returns a reference to the instance object
        """
        try:
            import yaml
        except ImportError as import_error:
            print(str(import_error), "- Use 'pip install pyyaml' or install this "
                                     "package with [click] option")
            sys.exit(1)
        with open(path, 'r') as stream:
            cfg = yaml.load(stream, Loader=yaml.Loader)

        return self.__load_cfg(cfg, section)

    def load_config(self, path, section=None):
        """Load Configuration

        :param path: Path to the json file
        :param section: Section of the file if it have one
        :return: Returns a reference to the instance object
        """
        if path.endswith('.json'):
            return self.load_json(path, section)
        elif path.endswith('.yaml') or path.endswith('.yml'):
            return self.load_yaml(path, section)

        raise ConfigurationException("Configuration file type unknown or not supportted: %s" %path)

    def load_default_config(self, ext="yml", section=None):
        if ext is "yml" or ext is "yaml":
            return self.load_yaml("~/.devo.%s" % ext, section)
        elif ext is "json":
            return self.load_json("~/.devo.json", section)

    #Deprecated in future
    def load_default_json(self, section=None):
        """Load Json Configuration in ~/.devo.json

        :param section: Section of the file if it have one
        :return: Returns a reference to the instance object
        """
        return self.load_json("~/.devo.json", section)

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