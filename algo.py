from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import argparse                        
import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
import datetime
import os
import sys
import pandas as pd
from pandas import Series, DataFrame
import random
from copy import deepcopy
import warnings
warnings.filterwarnings('ignore')
from strategy.ma import MA
from strategy.dollarcost import DollarCost

def parse_args():
    """ main args """
    parser = argparse.ArgumentParser(
        description='algorithim trading strategy')

    parser.add_argument('--noheaders', action='store_true', default=True,
                        required=False,
                        help='Do not use header rows')

    parser.add_argument('--noprint', action='store_true', default=True,
                        help='Print the dataframe')

    parser.add_argument('--symbol', default=None,
                        required=False,
                        help='limit to the given symbol')

    parser.add_argument('--atrdist', required=False, action='store',
                        type=float, default=3.0,
                        help=('ATR Factor for stop price calculation'))

    parser.add_argument('--atrperiod', required=False, action='store',
                        type=int, default=14,
                        help=('ATR Period To Consider'))

    parser.add_argument('--smaperiod', required=False, action='store',
                        type=int, default=30,
                        help=('Period for the moving average'))

    parser.add_argument('--dirperiod', required=False, action='store',
                        type=int, default=10,
                        help=('Period for SMA direction calculation'))
    parser.add_argument('--amount', required=False, action='store',
                        type=int, default=1000,
                        help=('Amount of account topup every period'))

    return parser.parse_args()

def getStockList():
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    symbolDates = os.listdir('data\\2013-2016')
    for i, symbolDate in enumerate(symbolDates):
        datapath = os.path.join(modpath, 'data\\2013-2016', symbolDate)
        print(datapath)

def get_data(args):
    ''' get the price data for a given symbol '''
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    symbol_dates = os.listdir('data\\2013-2016')
    symbol_buffer = modpath + "\\data\\" + args.symbol + ".csv"

    # load the dataframe from preload or parse out
    dataframe = pd.DataFrame()
    if os.path.exists(symbol_buffer):
        skiprows = 1 if args.noheaders else 0
        header = 0
        df = pd.read_csv(symbol_buffer,
                        skiprows=skiprows,
                        header=header,
                        parse_dates=True,
                        index_col=0,
                        names=['date', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
        dataframe = df
    else:    
        for i, symbol_date in enumerate(symbol_dates):
            datapath = os.path.join(modpath, 'data\\2013-2016', symbol_date)
            skiprows = 1 if args.noheaders else 0
            header = None if args.noheaders else 0
            df = pd.read_csv(datapath,
                            skiprows=skiprows,
                            header=header,
                            parse_dates=True,
                            index_col=1,
                            names=['symbol', 'date', 'open', 'high', 'low', 'close', 'volume'])
            df = df[df['symbol'] == args.symbol]
            if dataframe.empty: 
                dataframe = df
            else:
                dataframe = pd.concat([dataframe,df])
    
    # save out the dataframe for fast rerun
    if not os.path.exists(symbol_buffer):
        dataframe.to_csv(modpath + "\\data\\" + args.symbol + ".csv",
                         columns=[ 'symbol', 'open', 'high', 'low', 'close', 'volume'],
                         header = False if args.noheaders else True)
    dataframe = dataframe.drop('symbol', axis=1)
    if not args.noprint:
        print('--------------------------------------------------')
        print(dataframe)
        print('--------------------------------------------------')
    data = btfeeds.PandasData(dataname=dataframe)
    return data

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

def execute_strategy():
    """ execute trading strategies """
    args = parse_args()
    startcash = 10000
    cerebro = bt.Cerebro()
    cerebro.broker.addcommissioninfo(FixedCommisionScheme())
    
    data = get_data(args)
    cerebro.adddata(data)
    cerebro.broker.set_cash(startcash)

    cerebro.addanalyzer(bt.analyzers.SQN)
    cerebro.addanalyzer(bt.analyzers.AnnualReturn)
    cerebro.addanalyzer(bt.analyzers.PeriodStats)
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

    cerebro.addstrategy(DollarCost, amount=args.amount, atrdist=args.atrdist)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=10)

    results = cerebro.run()
    st0 = results[0]
    for alyzer in st0.analyzers:
        alyzer.print()

    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash
    print('Final Portfolio Value: ${}'.format(portvalue))
    print('P/L: ${}'.format(pnl))
    cerebro.plot() # style='candlestick'

if __name__ == '__main__':
    execute_strategy()
