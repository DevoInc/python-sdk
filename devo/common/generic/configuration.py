# -*- coding: utf-8 -*-
""" Util for load generic config file in devo standars"""
import json
import sys
import os


class ConfigurationException(Exception):
    """ Default Configuration Exception """


class Configuration(dict):
    """
    Main class for load config files, and extract config objects
    """
    def __init__(self, path=None, section=None):
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
                    json.dump(self, file)
                if path.endswith('.yaml') or path.endswith('.yml'):
                    try:
                        import yaml
                    except ImportError as import_error:
                        print(str(import_error),
                              "- Use 'pip install pyyaml' or install this "
                              "package with [click] option")
                    yaml.dump(self, file, default_flow_style=False)
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

    @staticmethod
    def clean_cfg(cfg):
        """
        Clean self keys with None (CLI default values fix)
        """
        keys = list(cfg.keys())
        for key in keys:
            if cfg[key] is None:
                cfg.pop(key)

        return cfg

    def mix(self, cfg, aux=None):
        """Mix configuration (override vars values)

        :param cfg: Configuration to mix
        :param aux: aux dict for recursive use
        """
        if aux is None:
            aux = self

        cfg = self.clean_cfg(cfg)
        for key, value in cfg.items():
            aux_key = aux.get(key)
            if isinstance(aux_key, dict) and isinstance(value, dict):
                self.mix(value, aux_key)
            else:
                aux[key] = value

    def secure_mix(self, cfg, aux=None):
        """Mix configuration only if value is None or if not exist

        :param cfg: Configuration to mix
        :param aux: aux dict for recursive use
        """
        if aux is None:
            aux = self

        cfg = self.clean_cfg(cfg)
        for key, value in cfg.items():
            aux_key = aux.get(key, None)
            if isinstance(aux_key, dict) and isinstance(value, dict):
                self.mix(value, aux_key)
            elif aux_key is not None and aux_key not in aux.keys():
                aux[key] = value

    def get(self, key=None, default=None, aux_dict=None):
        """Get the configuration as dict

        :return: Return the configuration dict
        """
        if aux_dict is None:
            aux_dict = self

        if key is None:
            return aux_dict

        if not isinstance(key, (list, tuple)):
            key = [key]

        if key[0] in aux_dict.keys():
            if len(key) > 1:
                return self.get(key=key[1:], default=default,
                                aux_dict=aux_dict[key[0]])
            return aux_dict[key[0]]

        return default

    def set(self, key=None, value=None):
        """ Set value of dict
         :param key: Key when save value, can be list to create depth key
         :param value: Value to save
        """
        if key:
            if not isinstance(key, (list, tuple)):
                self[key] = value
            else:
                self.mix(self.create_dict_chain(key, value))

    def create_dict_chain(self, key_list, value):
        if len(key_list) == 1:
            return {key_list[0]: value}

        return {key_list[0]: self.create_dict_chain(key_list[1:], value)}
