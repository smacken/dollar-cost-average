from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime
import backtrader as bt
from .strategyFetcher import StrategyFetcher

@StrategyFetcher.register
class DollarCost(bt.Strategy):
    '''
    Dollar cost average over time strategy
    '''
    params = (
        ('amount', 1000),
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 3.0),   # % ATR distance for stop price
    )

    def __init__(self):
        # indicators for market trend
        self.ma50 = bt.indicators.SMA(self.data, period=50)
        self.ma200 = bt.indicators.SMA(self.data, period=200)
        self.crup = bt.indicators.CrossUp(self.data, self.ma50, self.ma200)
        self.crdown = bt.indicators.CrossDown(self.data, self.ma50, self.ma200)
        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)
        self.pstop = 0
        self.order = None
        self.month = None
        self.remainder = 0
        self.bearish = False
        self.invested = 0
        self.stopped = False

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
            self.stopped = False
            bank = self.broker.get_cash()
            self.broker.add_cash(self.p.amount)
            self.invested += self.p.amount
            
            num_buy = int(round(((self.p.amount + self.remainder) / self.data.open[0])))
            #print(self.data.open[0], num_buy)
            print('buy', self.data.datetime.date(), (self.p.amount - (num_buy * self.data.open[0])))
            
            if self.ma50 >= self.ma200 and self.data.high[0] > self.ma50:
                self.bearish = False
                self.remainder = (self.p.amount - (num_buy * self.data.open[0]))
                print('remainder', self.remainder)
                self.order = self.buy(size=num_buy)
            else:
                # engage stop loss
                self.bearish = True
                pdist = self.atr[0] * self.p.atrdist
                self.pstop = self.data.close[0] - pdist

        self.month = self.data.datetime.date().month
        if self.remainder < 0:
            self.remainder = 0

        # stop loss
        if self.position and self.bearish and not self.stopped:
            pclose = self.data.close[0]
            pstop = self.pstop

            if pclose < pstop:
                print('sell position: ', self.position.size)
                close_position = int(round(self.position.size/2))
                self.close(size=close_position)
                self.stopped = True
            else:
                pdist = self.atr[0] * self.p.atrdist
                self.pstop = max(pstop, pclose - pdist)

    def stop(self):
        self.close(size=self.position.size)
        self.log('Invested: ' + str(self.invested))

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
