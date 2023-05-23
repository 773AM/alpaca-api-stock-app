import sqlite3, datetime, config
from datetime import timedelta
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):

    stock = request.query_params.get('add_stock', False)

    connection = sqlite3.connect('app.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if type(stock) == str:
        cursor.execute("""
            SELECT id, symbol, name FROM stock WHERE symbol LIKE ?
        """, (stock,))
    else:
        cursor.execute("""
            SELECT id, symbol, name FROM stock ORDER BY symbol
        """)

    rows = cursor.fetchall()

    current_date = datetime.date.today()
    previous_date = (current_date - timedelta(days = 1)).isoformat() ## We run this in the morning so we don't have the current date's close and we cannot calculate it's RSI, SMA's

    cursor.execute("""
        SELECT symbol, rsi_14, sma_20, sma_50, close
        FROM stock join stock_price on stock_price.stock_id = stock.id
        WHERE date = ?
    """,(previous_date,))
    

    indicator_rows = cursor.fetchall()
    indicator_values = {}
    for row in indicator_rows:
        indicator_values[row['symbol']] = row


    return templates.TemplateResponse("index.html", {"request":request, "stocks":rows, "indicator_values":indicator_values})


@app.get("/stock/{symbol}")
def stock_detail(request: Request, symbol):
    connection = sqlite3.connect('app.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM watch_list
    """)

    WatchList = cursor.fetchall()

    cursor.execute("""
        SELECT id, symbol, name FROM stock WHERE symbol = ?
    """, (symbol,))

    row = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM stock_price WHERE stock_id= ? ORDER BY date DESC
    """, (row['id'],))

    prices = cursor.fetchall()

    return templates.TemplateResponse("stock_detail.html", {"request":request, "stock":row, "bars": prices, "WatchList": WatchList})

@app.post("/add_WatchList")
def add_watchlist(stock_id: int = Form(...)):
    connection = sqlite3.connect('app.db')
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO watch_list (stock_id) VALUES (?)
    """, (stock_id,))

    connection.commit()
    
    return RedirectResponse(url=f"/myWatchList", status_code=303)

@app.get("/myWatchList")
def myWatchList(request: Request):
    connection = sqlite3.connect('app.db')
    connection.row_factory = sqlite3.Row
    
    cursor = connection.cursor()

    cursor.execute("""
        SELECT symbol, name FROM stock 
        JOIN watch_list ON watch_list.stock_id = stock.id
    """)

    stocks = cursor.fetchall()

    return templates.TemplateResponse("watch_list.html", {"request": request, "stocks": stocks})

@app.get("/orders")
def orders(request: Request):
    trading_client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)

    request_params = GetOrdersRequest(
        status='all'
    )
    account_orders = trading_client.get_orders(request_params)
    print(account_orders)

    return templates.TemplateResponse("orders.html", {"request": request, "Orders": account_orders})