import talib as ta
import pandas as pd
from numpy import array
import ccxt
import time

exchange = ccxt.binance({
    'enableRateLimit': True,
    'apiKey': '7Fd8RySvCmgttHqr3IPAjAoNiT0KWE6rsf6gYvfVPEInA3G0fMJgeesvlzHfHshd',
    'secret': 'h2aHWcdWeDah3Pq8LT6u7K4fIW9eelDBcA4KKddzIfmZBl10lKJ7QLGU784FBbS2',
})

coins = ['ETH/BTC', 'LTC/BTC', 'XMR/BTC', 'XRP/BTC']


def getClose(coin):
    try:
        d = exchange.fetch_ohlcv(coin, '5m')
        timestamps = pd.to_datetime([el[0] for el in d], unit='ms')
        close_prices = [el[4] for el in d]
        df = pd.DataFrame(list(zip(timestamps, close_prices)), columns=['time', 'close'])
        time.sleep(1)
        return df
    except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
        print('Got an error', type(error).__name__, error.args, ', retrying in 30 seconds...')
        time.sleep(30)
        getClose(coin)


def getLast(arr, name):
    return arr[name][arr[name].index[-1]]


if __name__ == '__main__':

    print('Starting Chande Multi Momentum Strategy')

    while True:
        for coin in coins:
            df = getClose(coin)
            cmo = ta.CMO(array(df.close), 9)

            if cmo[-1] < -96:
                print('we are long at {}'.format(df.close[-1]))
            elif cmo[-1] > 96:
                print('we are short at {}'.format(df.close[-1]))
            else:
                print('-------------------------------')
                print(getLast(df, 'time'))
                print('{}:  '
                      'close:  {}  '
                      'cmo:  {}'.format(coin, getLast(df, 'close'), cmo[-1]))



