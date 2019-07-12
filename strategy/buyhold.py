from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
from .strategyFetcher import StrategyFetcher

@StrategyFetcher.register
class BuyAndHoldInitial(bt.Strategy):
    def __init__(self):
        self.val_start = 0.0
        self.roi = 0.0

    def start(self):
        self.val_start = self.broker.get_cash()

    def next(self):
        size = int(self.broker.get_cash() / self.data)
        self.buy(size=size)

    def stop(self):
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('Buy-Hold')
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))

@StrategyFetcher.register
class BuyAndHoldDollarCost(bt.Strategy):
    params = dict(
        monthly_cash=1000.0,
        start_cash=10000.0
    )

    def start(self):
        self.broker.set_fundmode(fundmode=True, fundstartval=self.p.start_cash)

        self.cash_start = self.broker.get_cash()
        self.val_start = self.p.start_cash

        # Add a timer which will be called on the 1st trading day of the month
        self.add_timer(
            bt.timer.SESSION_END,
            monthdays=[1],
            monthcarry=True,
        )

    def notify_timer(self, timer, when, *args, **kwargs):
        self.broker.add_cash(self.p.monthly_cash)
        target_value = self.broker.get_value() + self.p.monthly_cash
        self.order_target_value(target=target_value)

    def stop(self):
        self.roi = (self.broker.get_value() - self.cash_start) - 1.0
        self.froi = self.broker.get_fundvalue() - self.val_start
        print('Buy-hold Dollarcost')
        print('ROI:        {:.2f}%'.format(self.roi))
        print('Fund Value: {:.2f}%'.format(self.froi))
