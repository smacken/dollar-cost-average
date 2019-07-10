'''
    Backtrader commision schemes
'''
import backtrader as bt

class FixedCommisionScheme(bt.CommInfoBase):
    '''
    This is a simple fixed commission scheme
    i.e. $10 per trade
    '''
    params = (
        ('commission', 10),
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_FIXED),
        )

    def _getcommission(self, size, price, pseudoexec):
        return self.p.commission

class FixedStagedCommisionScheme(bt.CommInfoBase):
    '''
    This is a simple fixed commission scheme
    i.e. $10 per trade
    '''
    params = (
        ('commission', 10),
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_FIXED),
        )

    def _getcommission(self, size, price, pseudoexec):
        return self.p.commission if size * price <= 1000 else 2*self.p.commission
