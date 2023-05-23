import config, datetime, sqlite3
from datetime import timedelta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import tulipy, numpy

connection = sqlite3.connect('app.db')

connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    SELECT id, symbol, name FROM stock
""")

rows = cursor.fetchall()

symbols = []
stock_dict = {}

for row in rows:
    symbol = row['symbol']
    symbols.append(symbol)
    stock_dict[symbol] = row['id']


api = StockHistoricalDataClient(config.API_KEY, config.SECRET_KEY)

chunk_size = 200

for i in range(0, len(symbols), chunk_size):
    symbol_chunk = symbols[i:i+chunk_size]

    request_params = StockBarsRequest(
    symbol_or_symbols= symbol_chunk,
    timeframe= TimeFrame.Day,
    start= datetime.datetime(2022, 5, 21),
    end= datetime.datetime.today()
)

    barsets = api.get_stock_bars(request_params)  #BARSETS comes in tuple data={DICTIONARY OF DATA, with KEYS being the stock TICKERS}
    
    for stock in symbol_chunk:
        try:
            stock_data = barsets[stock]
            recent_closes = [bar.close for bar in stock_data]
            
            for bar in stock_data:
                stock_id = stock_dict[stock]
                previous_date = (datetime.date.today()- timedelta(days = 1)).isoformat() ## We run this in the morning so we don't have the current date's close and we cannot calculate it's RSI, SMA's
                if len(recent_closes) >=50 and previous_date == bar.timestamp.strftime("%Y-%m-%d"):
                    sma_20 = tulipy.sma(numpy.array(recent_closes), period=20)[-1]
                    sma_50 = tulipy.sma(numpy.array(recent_closes), period=50)[-1]
                    rsi_14 = tulipy.rsi(numpy.array(recent_closes), period=14)[-1]
                else:
                    sma_20, sma_50, rsi_14 = None, None, None
                cursor.execute("""
                    INSERT INTO stock_price (stock_id, date, open, high, low, close, volume, sma_20, sma_50, rsi_14)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (stock_id, bar.timestamp.strftime("%Y-%m-%d"), bar.open, bar.high, bar.low, bar.close, bar.volume, sma_20, sma_50, rsi_14))
        except Exception as error:
            print(error)

connection.commit()
    
                                   

    
    

    