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

from strategy import StrategyFetcher
from strategy.rsi import RSI
from strategy.macd import MACD
from strategy.ma import MA
from strategy.bollinger import Bollinger
from strategy.bollingerCounter import BollingerCounter

def parse_args():
    """ main args """
    parser = argparse.ArgumentParser(
        description='algorithim trading strategy')

    parser.add_argument('--noheaders', action='store_true', default=False,
                        required=False,
                        help='Do not use header rows')

    parser.add_argument('--noprint', action='store_true', default=False,
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

    parser.add_argument('--maxcpus', required=False, action='store',
                        default=1, type=int,
                        help='Limit the numer of CPUs to use')

    parser.add_argument('--optreturn', required=False, action='store_true',
                        help='Return reduced/mocked strategy object')

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
    # cerebro.addstrategy(MACD, atrdist=args.atrdist)
    cerebro.addstrategy(Bollinger, atrdist=args.atrdist)

    data = getData(args)
    cerebro.adddata(data)
    cerebro.broker.set_cash(startcash)

    # cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    cerebro.addanalyzer(bt.analyzers.SQN)
    cerebro.addobserver(bt.observers.DrawDown) 

    # results = cerebro.run()
    # st0 = results[0]
    # for alyzer in st0.analyzers:
    #     alyzer.print()
    # strat = results[0]
    # pyfoliozer = strat.analyzers.getbyname('pyfolio')
    # pyfoliozer.adddata(data)
    # returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()

    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.optstrategy(StrategyFetcher, idx=StrategyFetcher.StrategyCount())
    results = cerebro.run(maxcpus=args.maxcpus, optreturn=args.optreturn)

    strats = [x[0] for x in results]  # flatten the result
    for i, strat in enumerate(strats):
        rets = strat.analyzers.returns.get_analysis()
        print('Strat {} Name {}:\n  - analyzer: {}\n'.format(
            i, strat.__class__.__name__, rets))

    # portvalue = cerebro.broker.getvalue()
    # pnl = portvalue - startcash
    # print('Final Portfolio Value: ${}'.format(portvalue))
    # print('P/L: ${}'.format(pnl))
    # cerebro.plot() # style='candlestick'

    # pf.create_full_tear_sheet(
    #     returns,
    #     positions=positions,
    #     transactions=transactions,
    #     # gross_lev=gross_lev,
    #     live_start_date='2013-01-01',
    #     round_trips=True)

if __name__ == '__main__':
    # args = parse_args()
    # getData(args)
    executeStrategy()
