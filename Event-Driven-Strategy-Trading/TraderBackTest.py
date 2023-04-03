from __future__ import print_function

import datetime
import pprint
from utils import get_local_timestamp
try:
    import Queue as queue
except ImportError:
    import queue
import time


class TraderBackTest(object):
    """
    Enscapsulates the settings and components for carrying out
    an event-driven backtest.
    """

    def __init__(
        self, symbol_list, initial_capital,start_date,
        heartbeat, data_handler, 
        execution_handler, portfolio, strategy
    ):
        """
        Initialises the backtest.
        Parameters:

        symbol_list - The list of symbol strings.
        intial_capital - The starting capital for the portfolio.
        start_date - The start datetime of the strategy.
        heartbeat - Backtest "heartbeat" in seconds.

        data_handler - (Class) Handles the market data feed.
        execution_handler - (Class) Handles the orders/fills for trades.
        portfolio - (Class) Keeps track of portfolio current and prior positions.
        strategy - (Class) Generates signals based on market data.
        """
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.start_date=start_date
        self.heartbeat = heartbeat

        self.data_handler_cls = data_handler
        self.execution_handler_cls = execution_handler
        self.portfolio_cls = portfolio
        self.strategy_cls = strategy

        self.events = queue.Queue()
        
        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1
       
        self._generate_trading_instances()

    def _generate_trading_instances(self):
        """
        Generates the trading instance objects from 
        their class types.
        """
        print(
            "Configuring the bot : Creating DataHandler, Strategy, Portfolio and ExecutionHandler"
        )
        self.data_handler = self.data_handler_cls(self.events,self.symbol_list,self.start_date)

        self.strategy = self.strategy_cls(self.data_handler, self.events)
        self.portfolio = self.portfolio_cls(self.data_handler, self.events, 
                                            self.initial_capital)
        self.execution_handler = self.execution_handler_cls(self.events) # to add an interface to binance market (e.g data handler)

    def _run_Trader(self):
        """
        Start Trading.
        """
        print("\N{feather}"+' Bot starts trading.......')
        
        current_pnl=0
       
        while self.portfolio.pnl==[] or current_pnl<0.001:
            

            self.data_handler.update_bars()

            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    
                    if event is not None:
                        if event.type=='QUIT':
                            break
                        if event.type == 'MARKET':
                            self.strategy.calculate_signals(event)

                        elif event.type == 'SIGNAL':
                            self.signals += 1                            
                            self.portfolio.update_signal(event)

                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.execution_handler.execute_order(event)

                        elif event.type == 'FILL':
                            self.fills += 1
                            self.portfolio.update_fill(event)
                            current_pnl=self.portfolio.pnl[-1]

            time.sleep(self.heartbeat)

    def _output_performance(self):
        """
        Outputs the strategy performance from the backtest.
        """

        self.portfolio.create_equity_curve_dataframe()

        print("Signals: %s" % self.signals)
        print("Orders: %s" % self.orders)
        print("Fills: %s" % self.fills)

        if (self.signals+1)%2==0:
            print("A Buy order is still open .....")

    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolio performance.
        """
        self._run_Trader()
        self._output_performance()
