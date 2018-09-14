""" Custom memoize function, not too much useful now """
import collections
import functools


class Memoize(object):
    """
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args, **kwargs):
        if not isinstance(args, collections.Hashable):
            return self.func(*args, **kwargs)
        k = tuple(kwargs.items())
        if (args, k) in self.cache:
            return self.cache[args, k]

        value = self.func(*args, **kwargs)
        self.cache[args, k] = value
        return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)
