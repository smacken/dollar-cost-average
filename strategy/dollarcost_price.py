from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
#import datetime
import backtrader as bt

class DollarCostPrice(bt.Strategy):
    '''
    Dollar cost average over price strategy
    '''
    params = (
        ('usepp1', True),
    )

    def __init__(self):
        if self.p.usepp1:
            self.pp = bt.indicators.PivotPoint(self.data[-1])
        else:
            self.pp = bt.indicators.PivotPoint(self.data1)

    def next(self):
        txt = ','.join(
            ['%04d' % len(self),
             '%04d' % len(self.data0),
             '%04d' % len(self.data1),
             self.data.datetime.date(0).isoformat(),
             '%.2f' % self.pp[0]])

        print(txt)

    def stop(self):
        self.close(size=self.position.size)
        #self.log('Invested: ' + str(self.invested))

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
