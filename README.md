# binance-auto-trading-bot
v1.0

using:

if __name__ == "__main__":

    APIKey   = ""
    
    Secret   = ""
    
    coin1    = "BNB"
    
    coin2    = "USDT"
    
    BNBUSDT  = Binance(APIKey, Secret, coin1, coin2)
    
    while True:
    
    try:
    
        BNBUSDT.exchange_coin2(SELLING_PRICE = 9.80)
    
        BNBUSDT.exchange_coin1(BUYING_PRICE = 9.73)
    
    except ValueError:
    
        time.sleep(5)
