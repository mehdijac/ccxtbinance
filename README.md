# binance-trading-bot-mastery

* You need to export public key and private key in the terminal 

* Install requirements if needed

* In config file you can add the list of crypto pairs 
and the initial balance 

ACTIVE_TRADING_PAIRS=[{'symbol':'BTC/BUSD'}]

WALLET=100.0

* For a single Trade use main.py 

* For multi-trades run workers.py 

In workers main body you can add as many workers as you need, these workers will share the initial balance and perform over the same crypto pair with the same strategy 'Intrends' but diffrent historical data (limit)

You can create workers based on other params like crypto pair, hyperparams... 


* The script will display at the end the gain & loss of each worker

