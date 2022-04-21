import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from binance import Client

client = Client('API-KEY', 'SECRET-KEY')
print (client)

def getdata(symbol):
    #Get the data of the fear and greed index using the API 
    r = requests.get('https://api.alternative.me/fng/?limit=0')

    # Format the data in un dataframe, set the index to a modified timestamp 
    df = pd.DataFrame(r.json()['data'])
    df.value = df.value.astype(int)
    df.timestamp = pd.to_datetime(df.timestamp,unit='s')
    df.set_index('timestamp',inplace=True)
    df = df[::-1]
   
   # Get the data of the cryptocurreny from yahoo finance and put it in another data frame and 
   # set the index to timestamp 
    df1 = yf.download(symbol)[['Close']]

    df1.index.name = 'timestamp'

    # Merge de two dataframes 
    tog = df.merge(df1,on='timestamp')

    tog['change'] = tog.Close.pct_change()
  
    tog['position'] = np.where(tog.value <= 20,1,0)
   
    return tog


# strategytest defined the BUY/SELL strategy. Basically if the FearandGreed index is less < 20 we buy and hold 
# until the index is more than 50. Then we sell 

def strategytest(symbol,qty,entried):
    df = getdata(symbol)
    buy_condition = 20
    sell_condition = 50
    if not entried:
        if buy_condition >= df.value[-1]:
            order = client.create_order(symbol=symbol,side='BUY',type='MARKET',quantity=qty)
            print(order)
            entried = True
        else:
            print("No trade has been executed")
    if entried:
        while True:
            df = getdata(symbol)
            sincebuy = df.loc[df.index > pd.to_datetime(order['transactTime'],unit='ms')]
            if len(sincebuy) > 0:
                sincebuyret = df.value[-1]
                if sincebuyret > 50:
                    order = client.create_order(symbol=symbol,side='SELL',type='MARKET',quantity=qty)
                    print(order)
                    break

# calling the Bot using BTC 
strategytest('BTC-USD',1,False)
