import sqlite3, config, datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.requests import StockBarsRequest, StockLatestBarRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame





connection = sqlite3.connect('app.db')

connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT symbol, name FROM stock
    JOIN watch_list on watch_list.stock_id = stock.id
    WHERE watch_list.stock_id = stock.id
""")

stocks = cursor.fetchall()

symbols = [stock['symbol'] for stock in stocks]


api = StockHistoricalDataClient(config.API_KEY, config.SECRET_KEY)
trading_client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)

current_date_start = datetime.datetime.today().strftime("%Y-%m-%d") + ' 13:30:00'
current_date_end = datetime.datetime.today().strftime("%Y-%m-%d") + ' 13:45:00'
for symbol in symbols:
    try:
        request_params = StockBarsRequest(
        symbol_or_symbols= symbol,
        timeframe= TimeFrame.Minute,
        start= current_date_start,
        end= current_date_end,
        )        
    
        minute_bars = api.get_stock_bars(request_params).df

        request_params_live = StockLatestBarRequest (
            symbol_or_symbols=symbol,
        )

        after_bars = api.get_stock_latest_bar(request_params_live)

        high_range = max(minute_bars['high'])
        low_range = min(minute_bars['low'])
        latest_bar = after_bars[symbol].close
        
        opening_range = float(high_range) - float(low_range)
        print(f"Symbol: {symbol}")
        print(f"15-Min Open Range: {opening_range}")

        if latest_bar > high_range:
            print(f"Placing Bullish Market Order for {symbol}, stop loss is {low_range}, take profit is {high_range*1.01}")
            market_order_data = MarketOrderRequest(
                symbol= symbol,
                qty= 100,
                side=OrderSide.BUY,
                type= 'market',
                time_in_force=TimeInForce.DAY,
                stop_loss={'stop_price': low_range},
                take_profit = {'limit_price': high_range * 1.01}
            )
            market_order = trading_client.submit_order(
                order_data=market_order_data
            )
        
    except Exception as error:
        print('There was an error')
        print(error)