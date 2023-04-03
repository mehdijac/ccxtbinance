from __future__ import print_function

import datetime
from math import floor
try:
    import Queue as queue
except ImportError:
    import queue

import numpy as np
import pandas as pd

from event import FillEvent, OrderEvent
from performance import create_sharpe_ratio, create_drawdowns,profit_loss


class Portfolio(object):
    """
    The Portfolio class handles the positions and market
    value. 
    The holdings DataFrame stores the cash and total market
    holdings value of each symbol for a particular 
    time-index.
    """

    def __init__(self, bars, events, initial_capital):
        """
        Initialises the portfolio with bars and an event queue. 

        Parameters:
        bars - The DataHandler object with current market data.
        events - The Event Queue object.
        initial_capital - The starting capital in USD.
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.initial_capital = initial_capital

        self.all_holdings = []
        self.pnl= []
        self.curve=pd.DataFrame()

    def update_holdings_from_fill(self, fill):
        """
        Takes a Fill object and updates the holdings.
        Parameters:
        fill - The Fill object to update the holdings with.
        """
        
        latest_datetime = self.bars.get_latest_bar_datetime(self.symbol_list[0])
        

        dh = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list] )
        dh['datetime'] = latest_datetime

        for s in self.symbol_list:
            market_value = self.bars.get_latest_bar_value(s, "close",'1s')
            dh[s]=market_value
        
        #Updating holdings  
        self.all_holdings.append(dh)
        #Updating the pnl 
        self.curve = pd.DataFrame(self.all_holdings)
        self.curve.set_index('datetime', inplace=True)
        final_pnl=list(map(lambda s: profit_loss(self.curve[s], self.initial_capital),self.symbol_list))
        
        self.pnl.append(final_pnl[0])


    def update_fill(self, event):
        """
        Updates the portfolio current holdings 
        from a FillEvent.
        """
        if event.type == 'FILL':
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal):
        """
        Simply files an Order object.

        Parameters:
        signal - Containing Signal information.
        """
        order = None

        symbol = signal.symbol
        direction = signal.signal_type

        mkt_quantity = 1
        order_type = 'MKT'

        if direction == 'LONG' :
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')

        if direction == 'EXIT':
            order = OrderEvent(symbol, order_type,mkt_quantity, 'SELL')

        return order

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders 
        based on the portfolio logic.
        """
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    # ========================
    # POST-TRADING STATISTICS
    # ========================

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        self.curve['pnl']=self.pnl
        print(self.curve)

        print(f" Returns : ",self.pnl[-1])
        

    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio.
        """
        #to be implmented
        pass 