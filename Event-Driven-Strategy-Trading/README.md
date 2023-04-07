## High level architecture for the event driven strategy 

![alt text](https://github.com/mehdijac/ccxtbinance/blob/main/Event-Driven-Strategy-Trading/HighLevelArchitecture.png?raw=true)

 Run Python Uptrend.py in terminal

* I have added a notebook under the name ML signal : The purpose is to produce a signal ML-based approch. These trained model will act as an indicators. A strategy class can import them to produce signals in calculate_signals' body

* Next steps : Create a pipeline to prepare data for modeling, by testing different models and decide if it's important to ensemble them


```bash

Event Driven Strategy Trading

│   ├── event.py 
│   ├── strategy.py
│   ├── data.py
│   ├── Trader.py
│   ├── TraderBackTest.py
│   ├── portfolio.py
│   ├── execution.py
│   ├── indicators.py
│   ├── utils.py
│   ├── performance.py
│   ├── mac.py
│   ├── MLsignal.ipynb
```


