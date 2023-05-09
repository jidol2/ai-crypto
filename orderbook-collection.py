import time
import requests
import pandas as pd
import datetime as dt

x=dt.datetime.now()

while (1):

    book = {}
    response = requests.get ('https://api.bithumb.com/public/orderbook/BTC_KRW/?count=5')
    book = response.json()


    data = book['data']

    bids = (pd.DataFrame(data['bids'])).apply(pd.to_numeric,errors='ignore')
    bids.sort_values('price', ascending=False, inplace=True)
    bids = bids.reset_index(); del bids['index']
    bids['type'] = 0
    
    asks = (pd.DataFrame(data['asks'])).apply(pd.to_numeric,errors='ignore')
    asks.sort_values('price', ascending=True, inplace=True)
    asks['type'] = 1 

    df = bids._append(asks)
    
    print (df)

    print ("\n")

    time.sleep(0.8)
    #continue;

    df = bids._append(asks)
    
    timestamp = dt.datetime.now()
    req_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    df['quantity'] = df['quantity'].round(decimals=4)
    df['timestamp'] = req_timestamp
    
    
    df.to_csv("/Users/jlee1119/2023-05-06-bithumb-btc-orderbook.csv", index=False, header=False, mode = 'a')

    if timestamp.day!=x.day: break


while (1):

    book = {}
    response = requests.get ('https://api.bithumb.com/public/orderbook/BTC_KRW/?count=5')
    book = response.json()


    data = book['data']

    bids = (pd.DataFrame(data['bids'])).apply(pd.to_numeric,errors='ignore')
    bids.sort_values('price', ascending=False, inplace=True)
    bids = bids.reset_index(); del bids['index']
    bids['type'] = 0
    
    asks = (pd.DataFrame(data['asks'])).apply(pd.to_numeric,errors='ignore')
    asks.sort_values('price', ascending=True, inplace=True)
    asks['type'] = 1 

    df = bids._append(asks)
    
    print (df)

    print ("\n")

    time.sleep(0.8)
    #continue;

    df = bids._append(asks)
    
    timestamp = dt.datetime.now()
    req_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

    df['quantity'] = df['quantity'].round(decimals=4)
    df['timestamp'] = req_timestamp

    
    df.to_csv("/Users/jlee1119/2023-05-07-bithumb-btc-orderbook.csv", index=False, header=False, mode = 'a')

    if timestamp.hour==x.hour and timestamp.minute==x.minute and timestamp.second==x.second: break

    #should_write_header = os.path.exists(fn)
    #if should_write_header == False:
    #    df.to_csv(fn, index=False, header=True, mode = 'a')
    #else:
    #    df.to_csv(fn, index=False, header=False, mode = 'a')

    #time.sleep(4.9)






   
