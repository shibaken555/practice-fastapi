from typing import Annotated
from fastapi import APIRouter, FastAPI, Query
import yfinance as yf

app = FastAPI()
router = APIRouter()


# 企業を検索した時に表示させる概要ページを表示するAPI
@router.get("/fetch_stocks/overview/{ticker_symbol}")
async def fetch_stocks(ticker_symbol):
    input_ticker_symbol = yf.Ticker(ticker_symbol)
    company_info = input_ticker_symbol.info
    if company_info.get("trailingPegRatio") is None:
        return {
            "ticker_symbol": ticker_symbol,
            "message": "存在しないティッカーシンボルです",
        }
    else:
        # 企業名、株価、時価総額を取得し返却する
        company_name = company_info.get("longName")
        stock_price = company_info.get("currentPrice")
        market_cap = company_info.get("marketCap")
        return {
            "ticker_symbol": ticker_symbol,
            "company_name": company_name,
            "stock_price": stock_price,
            "market_cap": market_cap,
            "message": "OK"
        }


# 入力したティッカーシンボルに合致する企業情報を返却するAPI
@router.get("/fetch_stocks/info/{ticker_symbol}")
async def fetch_stocks(ticker_symbol):
    input_ticker_symbol = yf.Ticker(ticker_symbol)
    company = input_ticker_symbol.info
    if company.get("trailingPegRatio") is None:
        return {
            {"ticker_symbol": ticker_symbol},
            {"company_info": "存在しないティッカーシンボルです"},
        }
    else:
        company_info = company.get("longBusinessSummary")
        return {"ticker_symbol": ticker_symbol, "company_info": company_info}


# 入力したティッカーシンボルに合致する企業の株価を返却するAPI
@router.get("/fetch_price/{ticker_symbol}/period/{period}")
async def fetch_price(ticker_symbol: str, period: str):
    ticker = yf.Ticker(ticker_symbol)
    price_history = ticker.history(period=period)
    if price_history.empty:
        return {
            "ticker_symbol": ticker_symbol,
            "price_data": "正しい期間を入力してください",
        }
    else:
        # price_data.Dateが時刻までを取得しているが、仕様上、年月日までで充分なので調整して返却する
        # price_historyの型がDataFrameでありそのままだとフロントにreturn出来ないので辞書型にしている
        price_data = price_history.reset_index().to_dict(orient="records")
        for d in price_data:
            d["Date"] = d["Date"].strftime("%Y-%m-%d")
        return {"ticker_symbol": ticker_symbol, "period":period,"price_data": price_data}

# 複数の株価を比較する事を目的としたAPI
# 複数のティッカーシンボルをリストで受け取り、合致する企業の株価をユーザに返却する
@router.get("/compare_stocks/")
async def compare_stocks(ticker_symbol: Annotated[list[str], Query()] = None):
    # ticker_symbolを引数にして複数の企業の株価を取得できるようにする
    tickers = yf.Tickers(ticker_symbol)
    # 全企業の株価データを格納するリスト
    all_price_data = []
    for symbol in ticker_symbol:
        prices = tickers.tickers[symbol].history(period="5d")
        price_data = prices.reset_index().to_dict(orient="records")
        # 各ティッカーのデータを辞書形式でリストに追加
        all_price_data.append({"ticker_symbol": symbol, "price_data": price_data})
    return all_price_data
