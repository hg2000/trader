## A Trading Engine for backtesting and live trading

not ready for production yet !!
Works only with IG Markets.


### Installation
pip3 install -r requirements.txt

cp .env_example .env
fill in credentials

Add Market price Data in .csv format to Folder resources/prices
Add strategy under engine/Strategy
Define strategy parameters under setup/strategies

Parameter optimization:
python3.6 optimize.py

Backtest:
python3.6 backtest.py

Live Trading (Don't do it on a Live Account !)
python3.6 run.py

