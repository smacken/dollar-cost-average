from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import datetime

class DollarCost(bt.Strategy):
    '''
    Dollar cost average over time strategy
    '''
    params = dict(
        amount=1000
    )

    def __init__(self):
        # indicators for market trend
        self.ma50 = bt.indicators.SMA(self.data, period=50)
        self.ma200 = bt.indicators.SMA(self.data, period=200)
        self.crup = bt.indicators.CrossUp(self.data, self.ma50, self.ma200)
        self.order = None
        self.month = None
        self.remainder = 0

    def is_first_of_month(self):
        todayDate = self.data.datetime.date()
        if todayDate.day > 25:
            todayDate += datetime.timedelta(7)
        first = todayDate.replace(day=1)

        # the markets might not be open on the first of the month
        month = self.data.datetime.date().month
        return self.data.datetime.date() == first or self.month is None or month > self.month

    def next(self):
        # buy stock if it's the first of the month
        if self.is_first_of_month():
            bank = self.broker.get_cash()
            print('current accnt: ', bank)
            self.broker.add_cash(self.p.amount)
            
            num_buy = int(round(((self.p.amount + self.remainder) / self.data.open[0])))
            print(self.data.open[0], num_buy)
            print('buy', self.data.datetime.date(), (self.p.amount - (num_buy * self.data.open[0])))
            #print(self.ma50, self.ma50(-3))
            if self.ma50 >= self.ma200:
                self.remainder = (self.p.amount - (num_buy * self.data.open[0]))
                print('remainder', self.remainder)
                self.o = self.buy(size=num_buy)

        self.month = self.data.datetime.date().month
        if self.remainder < 0:
            self.remainder = 0
