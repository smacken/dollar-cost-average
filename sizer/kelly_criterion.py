import backtrader as bt
# 
# www.seertrading.com/kelly-bet-sizing-money-management-position-sizing-strategy/

class KellyCriterion(bt.Sizer):
    params = (('stake', 1),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        return self.params.stake
