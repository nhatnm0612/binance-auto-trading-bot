##=================================##

import os
import ast
import time
import rule
import numpy

##=================================##

from binance.enums import *
from binance.client import Client

##=================================##

ALL = "ALL"

##=================================##

class Binance:
    ##=================================##
    ##      A U T O T R A D I N G      ##
    ##=================================##

    """
    1. Checking Account Balance
    2. Checking Exchange Rate
    3. Auto Buying
    4. Auto Selling
    5. Cancel Order
    6. Trading Rule
    """
    
    def __init__(self, api_key, secret_key, coin1, coin2):
        self.coin1      = coin1
        self.coin2      = coin2
        self.api_key    = api_key
        self.secret_key = secret_key
        self.symbol     = "{}{}".format(self.coin1, self.coin2)
        self.client     = Client(self.api_key, self.secret_key)


    def price_now(self):
        ## checking coin price
        prices = self.client.get_all_tickers()
        if "{}{}".format(self.coin1, self.coin2) in [price["symbol"] for price in prices]:
            for price in prices:
                if price["symbol"] == "{}".format(self.symbol):
                    print("[*] Ping SERVER, {}/{} Exchange Rate is {:f} now...".format(self.coin1, self.coin2, float(price["price"])))
                    return float(price["price"])
        else:
            raise IOError('There is no such symbol as "{}"'.format(self.symbol))

    def balance_check(self, ticker):
        ## checking account balance
        if self.client.get_asset_balance(asset = ticker) != None:
            return float(self.client.get_asset_balance(asset = ticker)["free"])
        else:
            raise IOError("There is no such asset name as \"{}\"".format(ticker))

    def exchange_coin1(self, BUYING_PRICE, volumn = ALL, check_price_timer = 5, check_order_timer = 300):
        ## buying coin1 by coin2
        complete_order    = False
        coin2_have        = self.balance_check(ticker = "{}".format(self.coin2))
        minimum_amount    = float(self.trading_rule()["minimum amount"])
        if BUYING_PRICE < float(self.trading_rule()["minimum price"]):
            raise ValueError("Your price is too low. Minimum price is {}".format(self.trading_rule()["minimum price"]))
        elif coin2_have < float(self.trading_rule()["minimum order value"]):
            raise ValueError("Your {} balance is not enough. Minimum order value is {} {}".format(self.coin2,
                                                                                                  self.trading_rule()["minimum order value"],
                                                                                                  self.trading_rule()["minimum order value unit"]))
        else:
            vol = (int(numpy.round((coin2_have / BUYING_PRICE) / minimum_amount)) * minimum_amount) if volumn == ALL else volumn
            while complete_order == False:
                price_now = self.price_now()
                if BUYING_PRICE >= price_now:
                    ## bit price_now
                    ## if success: note(something) && break
                    ## else sleep && repeat
                    print("<*> Order BUY {} {} at market price {}".format(vol, self.coin1, price_now))
                    self.client.create_order(symbol = self.symbol,
                                             side = SIDE_BUY,
                                             type = ORDER_TYPE_LIMIT,
                                             timeInForce = TIME_IN_FORCE_GTC,
                                             quantity = vol,
                                             price = "{}".format(price_now)) 
                    complete_order = True
                    print("[*] Complete order, now sleep for {} second(s)".format(check_order_timer))
                    time.sleep(check_order_timer)
                    open_orders    = self.client.get_open_orders(symbol = self.symbol)
                    for open_order in open_orders:
                        print("<*> Cancel order ID: {}".format(open_order["orderId"]))
                        self.client.cancel_order(symbol = self.symbol,
                                                 orderId = "{}".format(open_order["orderId"]))
                elif BUYING_PRICE < price_now:
                    time.sleep(check_price_timer)
            
    def exchange_coin2(self, SELLING_PRICE, volumn = ALL, check_price_timer = 5, check_order_timer = 300):
        ## selling coin1 to coin2
        complete_order    = False
        coin1_have        = self.balance_check(ticker = "{}".format(self.coin1))
        minimum_amount    = float(self.trading_rule()["minimum amount"])
        if SELLING_PRICE < float(self.trading_rule()["minimum price"]):
            raise ValueError("Your price is too low. Minimum price is {}".format(self.trading_rule()["minimum price"]))
        elif (coin1_have * SELLING_PRICE) < float(self.trading_rule()["minimum order value"]):
            raise ValueError("Your {} balance is not enough. Minimum order value is {} {}".format(self.coin1,
                                                                                                  self.trading_rule()["minimum order value"],
                                                                                                  self.trading_rule()["minimum order value unit"]))
        else:
            vol = (int(numpy.round(coin1_have / minimum_amount)) * minimum_amount) if volumn == ALL else volumn
            while complete_order == False:
                price_now = self.price_now()
                if SELLING_PRICE <= price_now:
                    ## bit price_now
                    ## if success: note(something) && break
                    ## else sleep && repeat
                    print("<*> Order SELL {} {} at market price {}".format(vol, self.coin1, price_now))
                    self.client.create_order(symbol = self.symbol,
                                             side = SIDE_SELL,
                                             type = ORDER_TYPE_LIMIT,
                                             timeInForce = TIME_IN_FORCE_GTC,
                                             quantity = vol,
                                             price = "{}".format(price_now)) 
                    complete_order = True
                    print("[*] Complete order, now sleep for {} second(s)".format(check_order_timer))
                    time.sleep(check_order_timer)
                    open_orders    = self.client.get_open_orders(symbol = self.symbol)
                    for open_order in open_orders:
                        print("<*> Cancel order ID: {}".format(open_order["orderId"]))
                        self.client.cancel_order(symbol = self.symbol,
                                                 orderId = "{}".format(open_order["orderId"]))
                elif SELLING_PRICE > price_now:
                    time.sleep(check_price_timer)

    def cancel_order(self, ORDER):
        client.cancel_order(symbol = self.symbol,
                            orderId = ORDER)

    def trading_rule(self):
        for info in rule.BINANCE_RULE:
            if info["symbol"] == self.symbol:
                return info


if __name__ == "__main__":
    APIKey   = ""
    Secret   = ""
    coin1    = "BNB"
    coin2    = "USDT"
    BNBUSDT  = Binance(APIKey, Secret, coin1, coin2)
    while True:
        try:
            BNBUSDT.exchange_coin2(SELLING_PRICE = 9.80)
            BNBUSDT.exchange_coin1(BUYING_PRICE = 9.73)
        except ValueError:
            time.sleep(5)
