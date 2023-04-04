from __future__ import print_function

import datetime

import numpy as np
import pandas as pd
import statsmodels.api as sm

from strategy import Strategy
from event import SignalEvent
from Trader import Trader
from TraderBackTest import TraderBackTest
from data import BinanceDataHandler,BinanceDataHandlerBacktest
from execution import SimulatedExecutionHandler
from portfolio import Portfolio
from indicators import In_trend 



class Intrend(Strategy):
    """
    Carries out an Intrend strategy with a
    short/long simple weighted moving average.
    """ 

    def __init__(
        self, bars, events, weight_ma_margion=1, window=5,limit=81):
        """
        Initialises the Intrend Strategy.
        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        weight_ma_margion - The strenght of the upper/lower bands (see indicators).
        window - The moving average lookback.
        limit - The number of candelsticks.
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.weight_ma_margion = weight_ma_margion
        self.window = window
        self.limit=limit

        # Set to True if a symbol is in the market
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to 'OUT'.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'
        return bought

    def calculate_signals(self, event):
        """
        Generates a new set of signals based on the INTREND
        strategy with the upper/lower bands crossing the last close.    
        Parameters
        event - A MarketEvent object. 
        """
        if event.type == 'MARKET':
            for s in self.symbol_list:
                
                print("\N{package}"+f"  Fetching new bars {s} from Market")

                bars = self.bars.get_latest_bars(s, N=self.limit).copy()
               
                df=In_trend(bars,self.window,self.weight_ma_margion)
                
                bar_date=self.bars.get_latest_bar_datetime(s,'1s')
                bar_date=np.datetime_as_string(bar_date)[0:19]
                
                if bars is not None and bars.size>0:#bars != []:
                    
                    last_index=len(df)-1
                    is_buy_signal=(not df['in_uptrend'].iloc[last_index-1] and df['in_uptrend'].iloc[last_index])
                    is_sell_signal = (df['in_uptrend'].iloc[last_index-1] and not df['in_uptrend'].iloc[last_index]) 
                    
                    symbol = s
                    dt = datetime.datetime.utcnow()
                    
                    sig_dir = ""

                    if is_buy_signal and self.bought[s] == "OUT":
                        print("\N{blossom}"+ f"  Signal to buy  {symbol} emitted at :{bar_date}")
                        sig_dir = 'LONG'
                        signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'LONG'
                        
                    elif is_sell_signal and self.bought[s] == "LONG":
                        print("\N{rose}"+ f"  Signal to sell {symbol} emitted at :{bar_date}")
                        sig_dir = 'EXIT'
                        signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'OUT'



if __name__ == "__main__":

    symbol_list = ['BTC/USDT']

    initial_capital = 100.0

    heartbeat = 0.0

    # T = Trader(symbol_list, initial_capital, heartbeat,
    #         BinanceDataHandler, SimulatedExecutionHandler, 
    #         Portfolio, Intrend)

    start_date='2023-04-01 00:00:00'

    T = TraderBackTest(symbol_list, initial_capital, start_date,heartbeat,
                BinanceDataHandlerBacktest, SimulatedExecutionHandler, 
                Portfolio, Intrend)
    

    T.simulate_trading()