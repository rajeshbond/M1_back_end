from .. import models, schemas, utls # importing models schemase , utls  # added 
from .. import models, schemas, utls,oauth2 # importing models schemase , utls  # added
from fastapi import Response, status, HTTPException, Depends, APIRouter # added 
from sqlalchemy.orm import Session  # added
from ..database import get_db #added
import pandas as pd
import operator,collections
from typing import List, Optional
from sqlalchemy import func
from nsetools import Nse

import json

router = APIRouter(
    prefix= '/watchlist',
     tags=["Watchlist"]
) 

@router.post("/",status_code= status.HTTP_201_CREATED)
def addtowatchlist(wlist: schemas.WatchListIn,db: Session = Depends(get_db),
                    current_user: int = Depends(oauth2.get_current_user)):
    
    stock_query  = db.query(models.Symbol).filter(models.Symbol.symbol == wlist.symbol.upper())
    print(wlist)
    stock = stock_query.first()
    if not stock:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f" {wlist.symbol.upper()} not a active stock ") 
    symbol_present_query = db.query(models.WatchList).filter(models.WatchList.stock_id==stock.id,models.WatchList.user_id == current_user.id)
    symbol_present = symbol_present_query.first()
    
    if symbol_present:
        raise HTTPException(status_code= status.HTTP_208_ALREADY_REPORTED, detail=f" {wlist.symbol.upper()} already present in your watchlist ") 

    watch = {
        
        "user_id": current_user.id,
        "stock_id": stock.id
        
    }
    records = models.WatchList(**watch)
    db.add(records)
    db.commit()
    print(watch)
    # now code for instant symbol data 
    nse = Nse()
    quote = nse.get_quote(wlist.symbol.upper())
    print("============================")
    print(quote)
    watchprice = {
                                                
        "stock_id" : stock.id,
        "lastPrice": quote.get('lastPrice'),
        "pChange": quote.get('pChange'),
                                                
                                                
    }
    print(watchprice)
    records = models.WatchlistPrice(**watchprice)
    db.add(records)
    db.commit()
    print(watchprice)
    return watch, watchprice

# @router.get("/",response_model= List[schemas.PostOut])
# def displayuser(db: Session = Depends(get_db),
#                     current_user: int = Depends(oauth2.get_current_user)):
#     user_query = db.query(models.WatchList).filter(models.WatchList.user_id == current_user.id)
#     # symbol= db.query(models.Symbol).all()
#     user = user_query.all()
#     list={}
#     # for id in user:
#     #     symbol= db.query(models.Symbol).filter(models.Symbol.id == id.stock_id).first()
#     #     list.append(symbol.symbol)
#     #     print(symbol.symbol) 
    
#     # return sorted(list)
#     count = 0 
#     for id in user:
#         symbol= db.query(models.Symbol).filter(models.Symbol.id == id.stock_id).first()
#         list[count] = symbol.symbol
#         list[count] = symbol.name_of_the_company
#         # list[count] = symbol.name_of_the_company
        
#         list.update()
#         count +=1
  
#     # return item
#     return collections.OrderedDict(sorted(list.items(), key=lambda kv: kv[1]))

@router.get("/")
def displayuser(db: Session = Depends(get_db),
                    current_user: int = Depends(oauth2.get_current_user)):
    print("================================")
    user_query = db.query(models.WatchList).filter(models.WatchList.user_id == current_user.id)
    user = user_query.order_by(models.WatchList.stock_id.asc()).all()
   
    list={}

    count = 0 
    for id in user:
        symbol= db.query(models.Symbol).filter(models.Symbol.id == id.stock_id).first()
        watchprice = db.query(models.WatchlistPrice).filter(models.WatchlistPrice.stock_id == id.stock_id).order_by(models.WatchlistPrice.id.desc()).first()
        # watchprice_query = db.query(models.WatchlistPrice,func.max(models.WatchlistPrice.id))
        # print(f"{watchprice.id} {watchprice.stock_id} {watchprice.lastPrice} {watchprice.pChange}")
        try:
            list[count] = {
                
                "symbol_id": symbol.id,
                "symbol" : symbol.symbol,
                "lastPrice":watchprice.lastPrice,
                "pChange":watchprice.pChange,
                "name_of_the_company" : symbol.name_of_the_company
            }
           
            count +=1
        except:
            pass
    
    # list_json = json.dumps(list)
  
    return list
    
    # return collections.OrderedDict(sorted(symbol_id.items(), key=lambda kv: kv[1])),collections.OrderedDict(sorted(symbol1.items(), key=lambda kv: kv[1])), collections.OrderedDict(sorted(name_of_the_company.items(), key=lambda kv: kv[1])),collections.OrderedDict(
    #     sorted(lastPrice.items(), key=lambda kv: kv[1])),pChange
        
@router.post("/addsearch",status_code= status.HTTP_201_CREATED)
def addtowaatchlist_search(wlist: schemas.WatchiLstInCompany,db: Session = Depends(get_db),
                    current_user: int = Depends(oauth2.get_current_user)):
    
    stock_query  = db.query(models.Symbol).filter(models.Symbol.name_of_the_company == wlist.name_of_the_company.upper())
    # print(wlist)
    stock = stock_query.first()
  
    if not stock: 
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail=f" {wlist.name_of_the_company.upper()} not a active stock ") 
    
    symbol_present_query = db.query(models.WatchList).filter(models.WatchList.stock_id==stock.id,models.WatchList.user_id == current_user.id)
    symbol_present = symbol_present_query.first()
    
    if symbol_present:
        raise HTTPException(status_code= status.HTTP_208_ALREADY_REPORTED, detail=f" {wlist.name_of_the_company.upper()} already present in your watchlist ") 

    watch = {
        
        "user_id": current_user.id,
        "stock_id": stock.id
        
    }
    records = models.WatchList(**watch)
    db.add(records)
    db.commit()
    print(watch)
    nse = Nse()
    quote = nse.get_quote(stock.symbol)
    print("============================")
    print(quote)
    watchprice = {
                                                
        "stock_id" : stock.id,
        "lastPrice": quote.get('lastPrice'),
        "pChange": quote.get('pChange'),
                                                
                                                
    }
    print(watchprice)
    records = models.WatchlistPrice(**watchprice)
    db.add(records)
    db.commit()
    print(watchprice)
    return watch, watchprice

