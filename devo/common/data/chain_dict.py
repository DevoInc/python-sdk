"""Utility for create customs Dicts with chain dict assignment."""


class ChainDict(dict):
    """ Custom Dict """
    def set_key(self, key_list, value):
        """
        Set key chain like dict[key1][key2][key3] = value

        :param key_list: Array with key names
        :param value: Value to assing
        :return: The dict with the new value assigned
        """
        if not isinstance(key_list, list):
            key_list = [key_list]
        self.set_key_chain(self, key_list, value)
        return

    @staticmethod
    def set_key_chain(cdict, key_list, value):
        """
        Recursive internal method for fill dictionary

        :param cdict: Dict object
        :param key_list: Array with key names
        :param value: Value to assing
        :return: The dict with the new value assigned
        """
        if len(key_list) == 1:
            cdict[key_list[0]] = value
        else:
            cdict[key_list[0]] = ChainDict.set_key_chain(dict(),
                                                           key_list[1:],
                                                           value)
        return cdict
