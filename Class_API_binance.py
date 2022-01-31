import configparser
import pandas as pd
from binance.client import Client
from binance.enums import *


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
        '''
        Return: (DataFrame)
        '''
        lastPriceList = self.api.get_symbol_ticker()

        def getLastPriceOfSymbol(symbol, lastPriceList):
            df_lastPrice = pd.DataFrame(lastPriceList)
            if len(df_lastPrice[df_lastPrice['symbol'] == symbol]) == 0:
                return -999
            else:
                return float(df_lastPrice[df_lastPrice['symbol'] == symbol]['price'].iloc[0])

        ret = []
        default_stable_coin = "USDT"

        for i in self.api.get_account()['balances']:
            if (float(i['free']) != 0) | (float(i['locked']) != 0):
                symbol = i['asset'] + default_stable_coin

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
        return pd.DataFrame(ret)

    def get_order_all(self):
        '''
        Return: (DataFrame)
        '''
        return pd.DataFrame(self.api.get_open_orders())

    def get_order_symbol(self, symbol):
        '''
        Return: (DataFrame)
        '''
        df = pd.DataFrame(self.api.get_open_orders())
        if len(df) != 0:
            return df[df['symbol'] == symbol]
        else:
            return pd.DataFrame()

    def cancel_order_symbol(self, symbol):
        orders = self.get_order_symbol(symbol)
        if len(orders['symbol']) != 0:
            for index in orders.index:
                symbol = orders['symbol'][index]
                orderId = orders['orderId'][index]
                self.api.cancel_order(symbol=symbol, orderId=orderId)

    def cancel_order_all(self):
        orders = self.get_order_all()
        if (len(orders) != 0):
            for index in orders.index:
                symbol = orders['symbol'][index]
                orderId = orders['orderId'][index]
                self.api.cancel_order(symbol=symbol, orderId=orderId)

    def execute_order(self, orderSignal, lot, mode):
        '''
        :param orderSignal:
        :param lot:
        :param mode: 'MARKET' / 'LIMIT' / "TEST"
        :return:
        '''
        symbol = orderSignal['Symbol']
        side = orderSignal['Side']
        price = orderSignal["Price"]
        order_func = self.api.create_order if mode == 'MARKET' or mode == 'LIMIT' else self.api.create_test_order
        try:
            args = dict(
                side=side,
                type=ORDER_TYPE_MARKET,
                symbol=symbol,
                quantity=abs(lot))

            if mode == 'LIMIT':
                args['price'] = price
                args['type'] = ORDER_TYPE_LIMIT
                args['timeInForce'] = 'GTC'

            order_func(**args)
            order_result = 'success'
            print('|', mode, symbol, side, abs(lot), order_result)
        except Exception as e:
            print('| FAIL', symbol, symbol, side, abs(lot), str(e))
            order_result = 'FAIL: ' + str(e)

