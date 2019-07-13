''' 
buyhold algo strategy 
'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
from .strategyFetcher import StrategyFetcher

@StrategyFetcher.register
class BuyAndHoldInitial(bt.Strategy):
    ''' Baseline benchmarck strategy '''
 
    def __init__(self):
        self.val_start = 0.0
        self.roi = 0.0
        self.order = None

    def start(self):
        self.val_start = self.broker.get_cash()
        print('valstart', self.val_start)

    def next(self):
        size = int(self.broker.get_cash() / self.data[0])
        
        if not self.position:
            print('cash', self.broker.get_cash())
            print('size', size)
            print('price', self.data[0])
            self.order = self.buy()

    def stop(self):
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('Buy-Hold')
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))
