""" strategy fetcher"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

class StrategyFetcher(object):
    """ manage a list of different strategies to be run"""
    _STRATS = []

    @classmethod
    def register(cls, target):
        """ register a strategy with the fetcher """
        cls._STRATS.append(target)

    @classmethod
    def StrategyCount(cls):
        """ the number of strategies currently in the fetcher"""
        return range(len(cls._STRATS))

    def __new__(cls, *args, **kwargs):
        idx = kwargs.pop('idx')
        obj = cls._STRATS[idx](*args, **kwargs)
        return obj
