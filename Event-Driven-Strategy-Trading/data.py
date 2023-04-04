from __future__ import print_function

from abc import ABCMeta, abstractmethod
import datetime
import os, os.path
import ccxt
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', None)

from event import MarketEvent




class LiveDataHandler(object):  
    """
    LiveDataHandler is an abstract base class providing an interface for
    all subsequent (inherited) live data handlers.
    The goal of a (derived) LiveDataHandler object is to output a generated
    set of bars (OHLCV) for each symbol requested. 
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type,TF='1s'):
        """
        Returns one of the Open, High, Low, Close or Volume
        from the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_value()")
    
    @abstractmethod
    def get_latest_bar_values(self, symbol, val_type,TF,N=1):
        """
        Returns N value of the Open, High, Low, Close or Volume
        from the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_values()")

    
    @abstractmethod
    def get_latest_bars_datetime(self, symbol,TF='1s'):
        """
        Returns a Python datetime object for the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_datetime()")

    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bars to the bars_queue for each symbol
        """
        raise NotImplementedError("Should implement update_bars()")
    
    @abstractmethod
    def get_latest_bars(self, symbol, TF='1s', N=1):
        """
        Returns the last N bars updated.
        """
        raise NotImplementedError("Should implement get_latest_bars()")
    
class BinanceDataHandler(LiveDataHandler):

    """
    BinanceDataHandler is designed to connect to the Binance API for
    each symbol to obtain the "latest" bars in a manner identical to a live
    trading interface. 
    """

    def __init__(self, events,symbol_list):
        """
        Initialises the API binance client for the data handler and 
        requesting real time data for each symbol.

        Parameters:
        events - The Event Queue.
        symbol-list - List of pairs symbol.
        """
        self.events = events
        self.symbol_list=symbol_list
        self.binance_spot_api=self._connect_spot_api() # to be updated

    def _connect_spot_api(self):
        """
        This function creates a client to the Binance API
        """ 
        return ccxt.binance({
        "apiKey": os.environ.get('bk'),
        "secret": os.environ.get('bs')
        })
    
    def get_latest_bar_value(self, symbol, val_type,TF='1s'):
        """
        Returns one of the Open, High, Low, Close or Volume
        from the last bar.
        """
        return self.get_latest_bars(symbol,TF, 1)[val_type].values[0]
    
    def get_latest_bars_values(self, symbol, val_type,TF='1s',N=1):
        """
        Returns N value of the Open, High, Low, Close or Volume
        from the last bar.
        """
        return self.get_latest_bars(symbol,TF, N)[val_type]
    
    def get_latest_bar_datetime(self, symbol,TF='1s'):
        """
        Returns a Python datetime object for the last bar.
        """
        return self.get_latest_bars(symbol,TF, 1)['timestamp'].values[0]
    
    def update_bars(self):
        """
        Pushes the latest bars to the bars_queue for each symbol
        """
        self.events.put(MarketEvent())
            
    def get_latest_bars(self, symbol,TF='1s', N=1):
        """
        Returns the last N bars updated.
        """
        if symbol in self.symbol_list :
        
            bars = self.binance_spot_api.fetch_ohlcv(symbol, timeframe=TF, limit=N+1)
            df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            return df
        
class BacktestDataHandler(object):  
    """
    BacktestDataHandler is an abstract base class providing an interface for
    all subsequent (inherited) backtest data handlers.
    The goal of a (derived) BacktestDataHandler object is to output a generated
    set of bars (OHLCV) for each symbol requested. 
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type,TF='1s'):
        """
        Returns one of the Open, High, Low, Close or Volume
        from the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_value()")
    
    @abstractmethod
    def get_latest_bar_values(self, symbol, val_type,TF,N=1):
        """
        Returns N value of the Open, High, Low, Close or Volume
        from the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_values()")
    
    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type,TF,N=1):
        """
        Returns N value of the Open, High, Low, Close or Volume
        from the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bars_values()")

    
    @abstractmethod
    def get_latest_bars_datetime(self, symbol,TF='1s'):
        """
        Returns a Python datetime object for the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_datetime()")

    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bars to the bars_queue for each symbol
        """
        raise NotImplementedError("Should implement update_bars()")
    
    @abstractmethod
    def get_latest_bars(self, symbol, TF='1s', N=1):
        """
        Returns the last N bars updated.
        """
        raise NotImplementedError("Should implement get_latest_bars()")

class BinanceDataHandlerBacktest(BacktestDataHandler):  
    """
    BinanceDataHandlerBacktest is designed to connect to the Binance API for
    each symbol to obtain the "latest" bars since a starting date for a certain period of time. 
    """

    def __init__(self, events,symbol_list,start_date):
        """
        Initialises the API binance client for the data hasndler and 
        requesting real time data for each symbol.

        Parameters:
        events - The Event Queue.
        symbol_list - List of pairs symbol.
        exchange - The Binance API client.
        data_history - The main historical data.
        ...
        """
        self.events = events
        self.symbol_list=symbol_list
        self.start_date=start_date
        self.exchange=self._connect_spot_api()
        self.data_history= {s:self._get_bars(s) for s in self.symbol_list}


        self.current=None 
        self.continue_backtest=True

    def _connect_spot_api(self):
        """
        This function creates a client to the Binance api
        """ 
        return ccxt.binance({
        "apiKey": os.environ.get('bk'),
        "secret": os.environ.get('bs')
        })
    
    def _get_bars(self,symbol,TF='1s',N=50000):
        """
        Fetch the historical data from Binance Exchange, converting
        them into pandas DataFrames.
        """
        from_ts = self.exchange.parse8601(self.start_date)
        sinces=[from_ts]
        # SHould be dividable by 500
        n=(N/500)
        dfs=[]

        while n>0:
            bars=self.exchange.fetch_ohlcv(symbol, timeframe=TF,since=sinces[-1],limit=501)
            sinces.append(sinces[-1]+60000)
            df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            dfs.append(df)
            n=n-1

        df_final=pd.concat(dfs)
        
        return df_final
  

    def _load_bars(self, symbol, TF='1s', N=501):
            """
            Returns the last N bars updated.
            """
            n=int(len(self.data_history[symbol])/N)
            for i in range(n):
                current_data=self.data_history[symbol].iloc[(i*N):(i+1)*N-1]
                yield pd.DataFrame(current_data.values,columns=current_data.columns)

    def get_latest_bars(self, symbol, TF='1s', N=501):
            
            if self.current is None :
                self.generator_data=self._load_bars(symbol, TF='1s', N=N)
                self.current=next(self.generator_data)
            
            return self.current
    
            
    def get_latest_bar_value(self, symbol, val_type,TF='1s'):
        
        return self.current[val_type].values[-1]
        
 
    def get_latest_bar_values(self, symbol, val_type,TF='1s',N=1):
     
        return self.current[val_type]
    
    def get_latest_bars_values(self, symbol, val_type,TF='1s',N=1):
        
        return self.current[val_type]
    


    def get_latest_bar_datetime(self, symbol,TF='1s'):

        return self.current['timestamp'].values[0]


    def update_bars(self):
        if self.current is not None:
            try :
                self.current=next(self.generator_data)
            except StopIteration:
                self.continue_backtest=False
        self.events.put(MarketEvent())


            

