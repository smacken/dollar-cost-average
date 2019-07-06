'''
    Asx based data retrieval
'''
import datetime
import os
import sys
import pandas as pd
import backtrader.feeds as btfeeds

def getStockList():
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    symbolDates = os.listdir('data\\2013-2016')
    for i, symbolDate in enumerate(symbolDates):
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