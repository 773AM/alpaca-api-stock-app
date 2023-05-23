import sqlite3 , config
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.requests import AssetClass

connection = sqlite3.connect('app.db')
connection.row_factory = sqlite3.Row #for cleaner code

cursor = connection.cursor()

cursor.execute(""" 
    SELECT symbol, name FROM stock
""")

rows = cursor.fetchall()
symbols = [row['symbol'] for row in rows] # big list of every symbol in the data base to compare when updating

trading_client = TradingClient(config.API_KEY,config.SECRET_KEY)

#US equities 
search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)
assets = trading_client.get_all_assets(search_params)

for asset in assets: 
    try:
        if asset.status == 'active' and asset.tradable and asset.symbol not in symbols:
            print(f"Added a new stock {asset.symbol} {asset.name}")
            cursor.execute("INSERT INTO stock (symbol, name, exchange) VALUES (? ,? ,? )", (asset.symbol, asset.name, asset.exchange))
    except Exception as error: 
        print(asset.symbol)
        print(error)

connection.commit()