# alpaca-api-stock-app

1. create an alpaca account and get your api key and secret key
2. install fastapi and the alpaca sdk
3. go to the config.py file and replace my keys
4. create a database called 'app.db'
5. run create_db.py
6. run populate_stocks.py
7. run populate_prices.py
8. on your command line run "python -m uvicorn main:app --reload" to host the WEB UI on your machine
9. run opening_range_breakout on a task scheduler or cronjob on MacOS set to anytime after the stock market open + 15minutes
not financial advice! 
