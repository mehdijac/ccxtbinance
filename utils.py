from datetime import datetime 
import pandas as pd

def get_local_timestamp():
    """
    This function returns the actual time
    """

    return int(str(datetime.now().timestamp())[0:10])

def profit_loss(history_orders,initial_balance):
    """
    This function calculates the profit and loss for an initiative balance of a pair
    """
    relative_ratio=1
    for i in range(len(history_orders)):
        if i % 2==0:
            relative_ratio=relative_ratio/history_orders[i]
        else:
            relative_ratio=relative_ratio*history_orders[i]

    return initial_balance*(relative_ratio-1) 


def get_bars(exchange,pair,limit,timeframe):

    bars = exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df


