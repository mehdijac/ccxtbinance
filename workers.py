from config import *
from utils import *
from indicators import In_trend
from credentials import BINANCE_API_KEY,BINANCE_SECRET_KEY

import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.max_rows', None)
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')

import ccxt
import schedule


global binance_spot_api
global pnls

class worker:

    def __init__(self,exchange,name,balance,pair,timeframe,limit,weight_ma_margion,m_average_period):
        
        self.exchange=exchange
        self.name=name
        self.balance=balance
        self.pair=pair
        self.timeframe=timeframe
        self.limit=limit
        self.weight_ma_margion=weight_ma_margion
        self.m_average_period=m_average_period
        self.in_position=False
        self.pnl=[]
        self.orders=[]

    def is_buy_signal(self,df):
        """
        This function identity the period when it is suitable to buy
        """
        last_index=len(df)-1
        signal=(not df['in_uptrend'][last_index-1] and df['in_uptrend'][last_index])

        return signal   
    
    def is_sell_signal(self,df):
        """
        This function identity the period when it is suitable to sell
        """  
        last_index=len(df)-1
        signal=(df['in_uptrend'][last_index-1] and not df['in_uptrend'][last_index])

        return signal
    
    def buy_sell_orders(self,df):
        """
        This function creates buy and sell orders if there is any signal and if there is no active order
        """
        global pnls
        last_index=len(df)-1
    
        if self.is_buy_signal(df):

            print(self.name + "\N{blossom}"+" changed to uptrend, buy")
            if not self.in_position:
                #order = exchange.create_market_buy_order
                self.orders.append(df["close"][last_index])
                self.in_position = True
            else:
                 print(self.name + "already in position, nothing to do")
            
    
        if self.is_sell_signal(df) :

            print(self.name + "\N{rose}"+" changed to downtrend, sell")
            if self.in_position and df["close"][last_index]>self.orders[-1]:
                self.orders.append(df["close"][last_index])
                self.pnl.append(profit_loss(self.orders,self.balance))

                pnls[f'{self.name}']=self.pnl

                #order = exchange.create_market_sell_order
                print(self.name + "\N{money with wings}"+"\N{money with wings}"+"\N{money with wings}"+f' profit and loss : {self.pnl[-1]}')
                self.in_position = False
            else:
                print(self.name + "You aren't in position, nothing to sell")  

    def run_bot(self):

        print(self.name +  "\N{spouting whale}"+f"  Fetching new bars for {datetime.now().isoformat()}")

        bars = binance_spot_api.fetch_ohlcv(self.pair, timeframe=self.timeframe, limit=self.limit)

        df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        Intrend_data = In_trend(df,self.m_average_period,self.weight_ma_margion)
    
        self.buy_sell_orders(Intrend_data)

def init_bot():
    """
    This function create a client to the Binance api
    """
    global binance_spot_api 
    binance_spot_api=ccxt.binance({
    "apiKey": BINANCE_API_KEY,
    "secret": BINANCE_SECRET_KEY
     })
    
    print("\N{seedling}"+' Initiating bot.......')



if __name__=='__main__':

    pair=ACTIVE_TRADING_PAIRS[0]['symbol']
    timeframe='1s'
    limit=[80,90]
    last_period=5
    weight_ma_margion=0.5
    #since=

    init_bot()

    pnls={}

    NBworker=len(limit)

    job=schedule.Scheduler()

    Workers=[]
    start_time= get_local_timestamp()
    print("\N{alarm clock}"+f' start time  : {start_time}')

    for i in range(NBworker):
        Workers.append(worker(binance_spot_api,f'WORKER -> { limit[i]}',WALLET/NBworker,pair,timeframe,limit[i],weight_ma_margion,last_period))
        #job.every(1).seconds.do(lambda : Workers[-1].run_bot())
        pnls[f'WORKER -> { limit[i]}']=[]
    job.every(1).seconds.do(lambda : Workers[-2].run_bot())
    job.every(1).seconds.do(lambda : Workers[-1].run_bot())
    while (get_local_timestamp()-start_time)<400:

        job.run_pending()
        time.sleep(1)

    plt.plot(pnls[Workers[-2].name])
    plt.show()
    plt.plot(pnls[Workers[-1].name])
    plt.show()

    print("\N{alarm clock}"+ f' end time  : {get_local_timestamp()}')







