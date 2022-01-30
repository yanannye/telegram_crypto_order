import configparser
import pandas as pd
from binance.client import Client


class API_Binance():
    def __init__(self):
        self.api = self._login()
        self.default_stable_coin = 'USDT'

    def _login(self):
        config = configparser.ConfigParser()
        config.read('login_info.ini')
        binance_key = config['Binance']['key']
        binance_secret = config['Binance']['secret']

        client = Client(api_key=binance_key, api_secret=binance_secret)
        return client

    def get_AIP(self):
        return self.api

    def set_default_stable_coin(self, token):
        self.default_stable_coin = token

    def getAccountInfo(self):
        lastPriceList = self.api.get_symbol_ticker()

        def getLastPriceOfSymbol(symbol, lastPriceList):
            df_lastPrice = pd.DataFrame(lastPriceList)
            if len(df_lastPrice[df_lastPrice['symbol'] == symbol]) == 0:
                return -999
            else:
                return float(df_lastPrice[df_lastPrice['symbol'] == symbol]['price'].iloc[0])
        ret = []
        for i in self.api.get_account()['balances']:
            if (float(i['free']) != 0) | (float(i['locked']) != 0):
                symbol = i['asset'] + self.default_stable_coin

                free = float(i['free'])
                locked = float(i['locked'])

                if i['asset'] == default_stable_coin:
                    free_in_stableCoin = free
                    locked_in_stableCoin = locked
                else:
                    LastPrice = getLastPriceOfSymbol(symbol, lastPriceList)
                    if LastPrice == -999:
                        continue
                    else:
                        free_in_stableCoin = LastPrice * float(i['free'])
                        locked_in_stableCoin = LastPrice * float(i['locked'])

                ret.append({
                    'symbol': i['asset'],
                    'free': free,
                    'free_in_stableCoin': free_in_stableCoin,
                    'locked': locked,
                    'locked_in_stableCoin': locked_in_stableCoin,
                })
        return ret