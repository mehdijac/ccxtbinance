# binance-trading-bot-mastery

You need to export public key and private key in the terminal 
Install if needed ccxt 

In config file you can add the list of crypto pairs 
and the initial balance 

ACTIVE_TRADING_PAIRS=[{'symbol':'BTC/BUSD'}]

WALLET=100.0

If you need to run a single job use main.py 

for multi-workers run workers.py 

-> In workers main body you can add as many workers as you need, these workers will share the initial balance and perform over the same crypto pair with the same strategy 'Intrends' but diffrent historical data (limit)

-> You can create workers based on other params like crypto pair, hyperparams... 


RUN in the terminal python workers.py 

The script will display a the end the gain & losses of each worker

