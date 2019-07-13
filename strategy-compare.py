from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from commision import FixedCommisionScheme
from strategy.strategyFetcher import StrategyFetcher
from strategy.buyhold import BuyAndHoldInitial
from strategy.buyholddollar import BuyAndHoldDollarCost
from strategy.dollarcost import DollarCost
import argparse                        
import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
import datetime
import os
import json
import sys
import pandas as pd
from pandas import Series, DataFrame
import random
from copy import deepcopy
import warnings
warnings.filterwarnings('ignore')


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

def get_data(args):
    ''' get the price data for a given symbol '''
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    symbol_dates = os.listdir('data\\2013-2016')
    symbol_buffer = modpath + "\\data\\" + args.symbol + ".pkl"

    # load the dataframe from preload or parse out
    dataframe = pd.DataFrame()
    if os.path.exists(symbol_buffer):
        skiprows = 1 if args.noheaders else 0
        header = 0
        frame = pd.read_pickle(symbol_buffer)
        dataframe = frame
    else:
        for i, symbol_date in enumerate(symbol_dates):
            datapath = os.path.join(modpath, 'data\\2013-2016', symbol_date)
            skiprows = 1 if args.noheaders else 0
            header = None if args.noheaders else 0
            frame = pd.read_csv(datapath,
                            skiprows=skiprows,
                            header=header,
                            parse_dates=True,
                            index_col=1,
                            names=['symbol', 'date', 'open', 'high', 'low', 'close', 'volume'])
            frame = frame[frame['symbol'] == args.symbol]
            if dataframe.empty:
                dataframe = frame
            else:
                dataframe = pd.concat([dataframe, frame])

    # save out the dataframe for fast rerun
    if not os.path.exists(symbol_buffer):
        dataframe.to_pickle(modpath + "\\data\\" + args.symbol + ".pkl")
    dataframe = dataframe.drop('symbol', axis=1)
    if not args.noprint:
        print('--------------------------------------------------')
        print(dataframe)
        print('--------------------------------------------------')
    data = btfeeds.PandasData(dataname=dataframe)
    return data

def execute_strategy():
    """ execute trading strategies """
    args = parse_args()
    startcash = 10000
    cerebro = bt.Cerebro()
    
    data = get_data(args)
    cerebro.adddata(data)
    cerebro.broker.set_cash(startcash)
    cerebro.broker.addcommissioninfo(FixedCommisionScheme())

    cerebro.addanalyzer(bt.analyzers.SQN)
    cerebro.addobserver(bt.observers.DrawDown) 
    cerebro.addanalyzer(bt.analyzers.Returns)

    cerebro.optstrategy(StrategyFetcher, idx=StrategyFetcher.StrategyCount())
    results = cerebro.run(maxcpus=args.maxcpus, optreturn=args.optreturn)

    strats = [x[0] for x in results]
    for i, strat in enumerate(strats):
        rets = strat.analyzers.returns.get_analysis()
        print('Strat {} Name {}:\n  - analyzer: {}\n'.format(
            i, strat.strategycls, json.dumps(rets, indent=4)))

    # portvalue = cerebro.broker.getvalue()
    # pnl = portvalue - startcash
    # print('Final Portfolio Value: ${}'.format(portvalue))
    # print('P/L: ${}'.format(pnl))
    # cerebro.plot() # style='candlestick'

if __name__ == '__main__':
    execute_strategy()
