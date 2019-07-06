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

# import pyfolio as pf
import warnings
warnings.filterwarnings('ignore')

# from strategy.strategyFetcher import StrategyFetcher

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
        # if i > 10:
        #      break
        datapath = os.path.join(modpath, 'data\\2013-2016', symbolDate)
        print(datapath)

def getData(args):
    ''' get the symbol data '''
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    symbolDates = os.listdir('data\\2013-2016')
    symbolBuffer = modpath + "\\data\\" + args.symbol + ".csv"
    dataframe = pd.DataFrame()
    if os.path.exists(symbolBuffer):
        skiprows = 1 if args.noheaders else 0
        header = 0
        df = pd.read_csv(symbolBuffer,
                        skiprows=skiprows,
                        header=header,
                        parse_dates=True,
                        index_col=0,
                        names=['date', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
        dataframe = df
    else:    
        for i, symbolDate in enumerate(symbolDates):
            datapath = os.path.join(modpath, 'data\\2013-2016', symbolDate)
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

    if not os.path.exists(symbolBuffer):
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

def executeStrategy():
    """ execute trading strategies """
    args = parse_args()
    startcash = 100000
    cerebro = bt.Cerebro()
    cerebro.broker.setcommission(commission=0.001)
    
    data = getData(args)
    cerebro.adddata(data)
    cerebro.broker.set_cash(startcash)
    
    #cerebro.addobserver(bt.analyzers.TradeAnalyzer)
    cerebro.addanalyzer(bt.analyzers.SQN)
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

    # strategy selection
    #cerebro.addstrategy(SMAC)
    # macdIdx = cerebro.addstrategy(MACD, atrdist=args.atrdist)
    # cerebro.addsizer_byidx(macdIdx, bt.sizers.PercentSizer, percents=10)
    
    cerebro.addstrategy(DollarCost, amount=args.amount)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=10)

    results = cerebro.run()
    st0 = results[0]
    for alyzer in st0.analyzers:
        alyzer.print()

    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash
    print('Final Portfolio Value: ${}'.format(portvalue))
    print('P/L: ${}'.format(pnl))
    cerebro.plot(style='candlestick') # style='candlestick'

    # pf.create_full_tear_sheet(
    #     returns,
    #     positions=positions,
    #     transactions=transactions,
    #     # gross_lev=gross_lev,
    #     live_start_date='2013-01-01',
    #     round_trips=True)

if __name__ == '__main__':
    executeStrategy()
