"""
Parsing .env file content and adding each value into os.environ
For testing purposes
"""
import os
import ast


def load_env_file(path=None):
    """
    Reads a .env file into os.environ.
    """
    if path and os.path.exists(path):
        pass
    else:
        if not os.path.exists('.env'):
            return False
        path = os.path.join('.env')

    for key, value in _proc_env(path):
        os.environ.setdefault(key, str(value))
    return True


def _proc_env(path):
    """
    Gets each line from the file and parse it.
    """
    with open(path) as file:
        for line in file:
            line = line.strip()
            if line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip().upper()
            value = value.strip()

            if not (key and value):
                continue

            try:
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                pass

            yield (key, value)
