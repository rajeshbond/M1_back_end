from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from fastapi import Response, status, HTTPException, Depends, APIRouter
import json
from datetime import datetime, time , timedelta , date
import requests, time
import pandas as pd
from sqlalchemy import func
from email import header
import requests, time 
from pandas import pandas as pd 
from datetime import datetime
from nsetools import Nse
import json
import yfinance as yf
import pandas as pd 


def datetotimestamp(date):
        return round(time.mktime(date.timetuple()))
def timestamptodate(timestamp):
        return datetime.fromtimestamp(timestamp)




router = APIRouter(
    prefix= '/intraday',
     tags=["Intraday_price"]
)


        
#----------------------------The funtion Starts here ---------------------   
@router.post("/")
def price_entery(db: Session = Depends(get_db)):
        
       
        
      
        is_true = True
        
        while is_true:
                watchlist = db.query(models.WatchList).all()
                start = datetotimestamp(date.today())
                time_frame = 5
                end = datetotimestamp(datetime.now())
                # print(watchlist)
                for row in watchlist:
                      
                        sybmol_query = db.query(models.Symbol).filter(models.Symbol.id == row.stock_id)
                        symbol = sybmol_query.first()
                        print(f"{row.stock_id} ---> {symbol.symbol}")
                        try:
                                url = 'https://priceapi.moneycontrol.com/techCharts/indianMarket/stock/history?symbol='+(symbol.symbol)+'&resolution='+str(time_frame)+'&from='+str(start)+'&to='+str(end)+'&countback=93&currencyCode=INR'
                                # print(url)
                                data = requests.get(url).json()
                                try: 
                                        for i in range(len(data['t'])):
                                                in_intraday = db.query(models.InterdayPrice).filter(models.InterdayPrice.date_stamp == data['t'][i],models.InterdayPrice.stock_id == row.stock_id).first()
                                                if in_intraday:
                                                        print("=========already intraday table=====")
                                                if data['s'] == 'ok' and not in_intraday:
                                                      
                                                
                                                        
                                                        price = {
                                                                        "stock_id": row.stock_id,
                                                                        "date_stamp":data['t'][i],
                                                                        "open":data['o'][i],
                                                                        "high":data['h'][i],
                                                                        "low":data['l'][i],
                                                                        "close":data['c'][i],
                                                                        "volume":data['v'][i],
                                                                        
                                                        }
                                                        
                                                

                                                        records = models.InterdayPrice(**price)
                                                        db.add(records)
                                                        db.commit()
                                                        print(price)
                                except:
                                        if in_intraday:
                                                print("i by pass the exception")
                                        else:
                                                with open("missing_entry_intraday.txt","a") as file :
                                                        file.write(f"{i}-->{row.stock_id} --> {symbol.symbol} ---> {url} \n ")
                        except:
                                with open("missing_symbols_intraday.txt","a") as file :
                                        file.write(f"\n{row.id}-->{symbol.symbol}  ")
                
        # time.sleep(60)        
               
#----------------------------The funtion ends here ---------------------        
        
        
@router.post("/nse")
def nsedata(db: Session = Depends(get_db)):
        
        is_true = True
        while is_true:
                watchlist = db.query(models.WatchList).all()
                for row in watchlist:
                        sybmol_query = db.query(models.Symbol).filter(models.Symbol.id == row.stock_id)
                        symbol = sybmol_query.first()
                        print(f"{row.stock_id} ---> {symbol.symbol}")
                        nse = Nse()
                        quote = nse.get_quote(symbol.symbol)    
                        in_watchlist_price = db.query(models.WatchlistPrice).filter(models.WatchlistPrice.lastPrice ==quote.get('lastPrice'),models.WatchlistPrice.stock_id == row.stock_id).first()
                        try:
                                if not in_watchlist_price:
                                        print(f"{quote.get('symbol')} {quote.get('lastPrice')} {quote.get('pChange')} {quote.get('quantityTraded')}")
                                        watchprice = {
                                                
                                                "stock_id" : symbol.id,
                                                "lastPrice": quote.get('lastPrice'),
                                                "pChange": quote.get('pChange'),
                                                
                                                
                                        }
                                        print(watchprice)
                                        records = models.WatchlistPrice(**watchprice)
                                        db.add(records)
                                        db.commit()
                        except:
                                pass

        
        return quote
        
