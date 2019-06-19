# -*- coding: utf-8 -*-
""" Util for load generic config file in devo standars"""
import json
import sys
import os


class ConfigurationException(Exception):
    """ Default Configuration Exception """


class Configuration:
    """
    Main class for load config files, and extract config objects
    """
    def __init__(self, path=None, section=None):
        self.cfg = dict()
        if path is not None:
            self.load_config(path=path, section=section)

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
        return None

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
            print(str(import_error), "- Use 'pip install pyyaml' or "
                                     "install this "
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
        if path.endswith('.yaml') or path.endswith('.yml'):
            return self.load_yaml(path, section)

        raise ConfigurationException("Configuration file type unknown "
                                     "or not supported: %s" % path)

    def save(self, path=None, save_bak=False):
        if path is None:
            return False

        if os.path.isfile(path):
            os.rename(path, "{}.bak".format(path))
        try:
            with open(path, 'w') as file:
                if path.endswith('.json'):
                    json.dump(self.cfg, file)
                if path.endswith('.yaml') or path.endswith('.yml'):
                    try:
                        import yaml
                    except ImportError as import_error:
                        print(str(import_error),
                              "- Use 'pip install pyyaml' or install this "
                              "package with [click] option")
                    yaml.dump(self.cfg, file, default_flow_style=False)
            if os.path.isfile("{}.bak".format(path)) and not save_bak:
                self.delete_file("{}.bak".format(path))
            return True
        except Exception:
            if os.path.isfile(path):
                self.delete_file(path)
            if os.path.isfile("{}.bak".format(path)):
                os.rename("{}.bak".format(path), path)
            return False

    @staticmethod
    def delete_file(file):
        if os.path.isfile(file):
            os.remove(file)

    @staticmethod
    def __search_default_config_file():
        return "json" if os.path.exists(os.path.expanduser("~/.devo.json")) \
            else "yaml" if os.path.exists(os.path.expanduser("~/.devo.yaml")) \
            else "yml" if os.path.exists(os.path.expanduser("~/.devo.yml")) \
            else None

    def load_default_config(self, ext=None, section=None):
        """Function for load default configuration"""
        if not ext:
            ext = self.__search_default_config_file()

        if ext in ("yml", "yaml"):
            return self.load_yaml("~/.devo.%s" % ext, section)
        if ext == "json":
            return self.load_json("~/.devo.json", section)

        raise ConfigurationException("Config file must be yml or json")

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

    def get(self, *args, **kwargs):
        """Get the configuration as dict

        :return: Return the configuration dict
        """
        key = kwargs.get("key", None)
        aux_dict = kwargs.get("aux_dict", None)

        if args:
            if isinstance(args[0], list):
                key = args[0]
            else:
                key = list(args)
        if key:
            if aux_dict is None:
                aux_dict = self.cfg
            if isinstance(key, list):
                if len(key) > 1:
                    return self.get(key=key[1:], aux_dict=aux_dict[key[0]])
                return aux_dict[key[0]]
            return self.cfg[key]

        return self.cfg

    def keys(self, prop=None):
        """Check if exist property and if not then set to None

        :param prop: Property to check
        """
        if not prop:
            return self.cfg.keys()

        if prop not in self.cfg:
            return False
        return True

    def key_exist(self, prop):
        """Check if exist property and if not then set to None

        :param prop: Property to check
        """
        return self.keys(prop)

    def set(self, key_list, value):
        """ Set value of dict
         :param key_list: Key when save value, can be list to create depth key
         :param value: Value to save
        """
        if value:
            if not isinstance(key_list, list):
                key_list = [key_list]
            self.cfg = self.set_key_chain(self.cfg, key_list, value)

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

    def __getitem__(self, key):
        return self.cfg[key]

    def __setitem__(self, key, value):
        self.cfg[key] = value
        return None

    def __str__(self):
        return str(self.cfg)
