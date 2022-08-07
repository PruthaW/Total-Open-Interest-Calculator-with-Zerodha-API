import pandas as pd
from datetime import date
from datetime import timedelta
import datetime 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from nsetools import Nse
import mysql.connector
#from kiteconnect import KiteConnect
import logging
import time
from kiteconnect import KiteConnect
import requests

#Create and configure #logging
logging.basicConfig(filename="LogFileCal.log",format='%(asctime)s %(message)s',filemode='w')
dataZerodha = pd.read_csv('zerodha.txt', header = None)
api_key=dataZerodha.iloc[0][0]
access_token=dataZerodha.iloc[0][1]
#Creating an object
#logging=logging.getlogging()
staticNiftyLots=-1
staticNiftyLotsBuy=1

def sendEmail(msg):
	#The mail addresses and password
    sender_address = 'sender email address'
    sender_pass = 'sendwer password'
    receiver_address = 'reciver email address'
	#Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Zerodha Order not execution error '   #The subject line
	#The body and the attachments for the mail
    message.attach(MIMEText(msg, 'plain'))
	#Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.sendmail(sender_address, 'pruthaw@gmail.com', text)
    session.quit()
    print('Mail Sent')
    logging.info('Mail Sent')
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)
def placeZerodhaOrder(tradingsymbolValue,exchangeValue,transaction_typeValue,quantityValue,order_typeValue,productValue):
    print("hi")
    try:
        order_id = kite.place_order(tradingsymbol=tradingsymbolValue,
                                    exchange=exchangeValue,
                                    transaction_type=transaction_typeValue,
                                    quantity=quantityValue,
                                    order_type=order_typeValue,
                                    product=productValue,
                                    variety=kite.VARIETY_REGULAR)

        print("Order placed. ID is: {}".format(order_id))
        logging.info("Order placed. ID is: {}".format(order_id))
    except Exception as e:
        print("Order placement failed: ",e)
        logging.info("Order placement failed: ",e)

def orderPlaceCallBuy(DonChainUpper10,DonchainPrev,CurrentLastPrice,SMALastPrice,CurrentOI,SMAOI,db,tradingSymbol,LatestDate,LatestTime,strikePrice,conn):
    #print("strikePrice : "+str(strikePrice)+" LatestDate"+str(LatestDate)+" LatestTime:"+str(LatestTime)+" DonChainUpper10: "+str(DonChainUpper10)+" DonchainPrev : "+str(DonchainPrev)+" CurrentLastPrice: "+str(CurrentLastPrice)+" SMALastPrice : "+str(SMALastPrice)+" CurrentOI: "+str(CurrentOI)+" SMAOI : "+str(SMAOI))
    SQLEntryQ ='select sum(EntryQuantity) from OrderZerodhaBankNifty where tradingSymbol="'+tradingSymbol+'" and EntryFunct="orderPlaceCallBuy"'
    #print(SQLEntryQ)
    EntryQ = pd.read_sql(SQLEntryQ,db)
    #print(EntryQ.iloc[0][0])
    if(EntryQ.iloc[0][0] == 0 or EntryQ.iloc[0][0] == None):
        EntryQOverallVal=0
        SQLEntryOverallQ = 'select sum(EntryQuantity) from OrderZerodhaBankNifty where EntryFunct="orderPlaceCallBuy"'
        EntryQOverall=pd.read_sql(SQLEntryOverallQ,db)
        #print(EntryQ.iloc[0][0])
        if(EntryQOverall.iloc[0][0] ==None):
            EntryQOverallVal=0
        else:
            EntryQOverallVal=EntryQOverall.iloc[0][0]

        SQLRenko ='select distinct BrickColor from Renko where IndexName="BANKNIFTY" order by SrNo desc LIMIT 3;'
        Renko = pd.read_sql(SQLRenko,db)
        if(len(Renko.index)==1 and Renko.iloc[0][0]=="GREEN"):
            #if(DonChainUpper10 > DonchainPrev) and (CurrentLastPrice > SMALastPrice) and (CurrentOI < SMAOI) and  (EntryQOverallVal <staticNiftyLotsBuy):
            if(DonChainUpper10 > DonchainPrev)  and  (EntryQOverallVal <staticNiftyLotsBuy):
                print("-------------orderPlaceCallBuy : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"--------BANKNIFTY-----")
                logging.info("-------------orderPlaceCallBuy : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"-------BANKNIFTY------")
                #print("CurrentLastPrice"+str(CurrentLastPrice))
                #print("CurrentOI"+str(CurrentOI))
                #print("SMALastPrice"+str(SMALastPrice))
                #print("SMAOI"+str(SMAOI))
                #print("DonchainPrev"+str(DonchainPrev))
                conn.execute("INSERT INTO OrderZerodhaBankNifty(DonChainUpper10,CurrentLastPrice,CurrentOI,SMALastPrice,SMAOI,DonchainPrev,tradingSymbol,LoadDate,LoadTime,strikePrice,TradeDesc,EntryFunct,TradeType,EntryQuantity,Timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(DonChainUpper10),str(CurrentLastPrice),str(CurrentOI),str(SMALastPrice),str(SMAOI),str(DonchainPrev),str(tradingSymbol),str(LatestDate),str(LatestTime),str(strikePrice),'BUY','orderPlaceCallBuy','ENTRY',1,str(datetime.datetime.now())))
                db.commit()
                
                tradingsymbolValue=tradingSymbol.replace('NFO:','')
                exchangeValue=kite.EXCHANGE_NFO
                transaction_typeValue=kite.TRANSACTION_TYPE_BUY
                quantityValue = 25
                order_typeValue = kite.ORDER_TYPE_MARKET
                productValue = kite.PRODUCT_NRML
                placeZerodhaOrder(tradingsymbolValue,exchangeValue,transaction_typeValue,quantityValue,order_typeValue,productValue)

def orderPlacePutBuy(DonChainLower10,DonchainPrev,CurrentLastPrice,SMALastPrice,CurrentOI,SMAOI,db,tradingSymbol,LatestDate,LatestTime,strikePrice,conn):
    #print("strikePrice : "+str(strikePrice)+" LatestDate"+str(LatestDate)+" LatestTime:"+str(LatestTime)+" DonChainUpper10: "+str(DonChainUpper10)+" DonchainPrev : "+str(DonchainPrev)+" CurrentLastPrice: "+str(CurrentLastPrice)+" SMALastPrice : "+str(SMALastPrice)+" CurrentOI: "+str(CurrentOI)+" SMAOI : "+str(SMAOI))
    SQLEntryQ = 'select sum(EntryQuantity) from OrderZerodhaBankNifty where tradingSymbol="'+tradingSymbol+'" and EntryFunct="orderPlacePutBuy"'
    #print(SQLEntryQ)
    EntryQ = pd.read_sql(SQLEntryQ,db)
    #print(EntryQ.iloc[0][0])
    if(EntryQ.iloc[0][0] == 0 or EntryQ.iloc[0][0] == None):
        EntryQOverallVal=0
        SQLEntryOverallQ = 'select sum(EntryQuantity) from OrderZerodhaBankNifty where EntryFunct="orderPlacePutBuy"'
        EntryQOverall=pd.read_sql(SQLEntryOverallQ,db)
        #print(EntryQ.iloc[0][0])
        if(EntryQOverall.iloc[0][0] ==None):
            EntryQOverallVal=0
        else:
            EntryQOverallVal=EntryQOverall.iloc[0][0]

        SQLRenko ='select distinct BrickColor from Renko where IndexName="NIFTY50" order by SrNo desc LIMIT 3;'
        Renko = pd.read_sql(SQLRenko,db)
        if(len(Renko.index)==1 and Renko.iloc[0][0]=="RED"):
            #if(DonChainLower10 < DonchainPrev) and (CurrentLastPrice > SMALastPrice) and (CurrentOI < SMAOI) and  (EntryQOverallVal <staticNiftyLotsBuy):
            if(DonChainLower10 < DonchainPrev)  and  (EntryQOverallVal <staticNiftyLotsBuy):
                print("-------------orderPlacePutBuy : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"------BANKNIFTY-------")
                logging.info("-------------orderPlacePutBuy : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"-----BANKNIFTY--------")
                #print("CurrentLastPrice"+str(CurrentLastPrice))
                #print("CurrentOI"+str(CurrentOI))
                #print("SMALastPrice"+str(SMALastPrice))
                #print("SMAOI"+str(SMAOI))
                #print("DonchainPrev"+str(DonchainPrev))
                conn.execute("INSERT INTO OrderZerodhaBankNifty(DonChainLower10,CurrentLastPrice,CurrentOI,SMALastPrice,SMAOI,DonchainPrev,tradingSymbol,LoadDate,LoadTime,strikePrice,TradeDesc,EntryFunct,TradeType,EntryQuantity,Timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(DonChainLower10),str(CurrentLastPrice),str(CurrentOI),str(SMALastPrice),str(SMAOI),str(DonchainPrev),str(tradingSymbol),str(LatestDate),str(LatestTime),str(strikePrice),'BUY','orderPlacePutBuy','ENTRY',1,str(datetime.datetime.now())))
                db.commit()
                tradingsymbolValue=tradingSymbol.replace('NFO:','')
                exchangeValue=kite.EXCHANGE_NFO
                transaction_typeValue=kite.TRANSACTION_TYPE_BUY
                quantityValue = 25
                order_typeValue = kite.ORDER_TYPE_MARKET
                productValue = kite.PRODUCT_NRML
                placeZerodhaOrder(tradingsymbolValue,exchangeValue,transaction_typeValue,quantityValue,order_typeValue,productValue)

def orderPlaceCallSell(DonChainLower10,DonchainPrev,CurrentLastPrice,SMALastPrice,db,tradingSymbol,LatestDate,LatestTime,strikePrice,conn,NiftyCurrntPrice):
    if(strikePrice > NiftyCurrntPrice):
        EntryQOverallVal=0
        SQLEntryQ = 'select sum(EntryQuantity) from OrderZerodhaBankNifty where tradingSymbol="'+tradingSymbol+'" and EntryFunct="orderPlaceCallSell"'
        SQLEntryOverallQ = 'select sum(EntryQuantity) from OrderZerodhaBankNifty where EntryFunct="orderPlaceCallSell"'
        
        #print(SQLEntryQ)
        EntryQ = pd.read_sql(SQLEntryQ,db)
        EntryQOverall=pd.read_sql(SQLEntryOverallQ,db)
        #print(EntryQ.iloc[0][0])
        if(EntryQOverall.iloc[0][0] ==None):
            EntryQOverallVal=0
        else:
            EntryQOverallVal=EntryQOverall.iloc[0][0]
        if(EntryQ.iloc[0][0] == 0 or EntryQ.iloc[0][0] == None):
            if(DonChainLower10 < DonchainPrev) and (CurrentLastPrice < SMALastPrice) and  (EntryQOverallVal >staticNiftyLots):
                print("-------------orderPlaceCallSell : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"-------BANKNIFTY------")
                logging.info("-------------orderPlaceCallSell : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"------BANKNIFTY-------")
                conn.execute("INSERT INTO OrderZerodhaBankNifty(DonChainLower10,CurrentLastPrice,SMALastPrice,DonchainPrev,tradingSymbol,LoadDate,LoadTime,strikePrice,TradeDesc,EntryFunct,TradeType,EntryQuantity,Timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(DonChainLower10),str(CurrentLastPrice),str(SMALastPrice),str(DonchainPrev),str(tradingSymbol),str(LatestDate),str(LatestTime),str(strikePrice),'SELL','orderPlaceCallSell','ENTRY',-1,str(datetime.datetime.now())))
                db.commit()
                tradingsymbolValue=tradingSymbol.replace('NFO:','')
                exchangeValue=kite.EXCHANGE_NFO
                transaction_typeValue=kite.TRANSACTION_TYPE_SELL
                quantityValue = 50
                order_typeValue = kite.ORDER_TYPE_MARKET
                productValue = kite.PRODUCT_NRML
                placeZerodhaOrder(tradingsymbolValue,exchangeValue,transaction_typeValue,quantityValue,order_typeValue,productValue)

def orderPlacePutSell(DonChainUpper10,DonchainPrev,CurrentLastPrice,SMALastPrice,db,tradingSymbol,LatestDate,LatestTime,strikePrice,conn,NiftyCurrntPrice):
    
    if(strikePrice < NiftyCurrntPrice):
        EntryQOverallVal=0
        SQLEntryQ = 'select sum(EntryQuantity) from OrderZerodhaBankNifty where tradingSymbol="'+tradingSymbol+'" and EntryFunct="orderPlacePutSell"'
        SQLEntryOverallQ = 'select sum(EntryQuantity) from OrderZerodhaBankNifty where EntryFunct="orderPlacePutSell"'
        
        #print(SQLEntryQ)
        EntryQ=pd.read_sql(SQLEntryQ,db)
        EntryQOverall=pd.read_sql(SQLEntryOverallQ,db)
        #print(EntryQ.iloc[0][0])
        if(EntryQOverall.iloc[0][0] ==None):
            EntryQOverallVal=0
        else:
            EntryQOverallVal=EntryQOverall.iloc[0][0]
        if(EntryQ.iloc[0][0] == 0 or EntryQ.iloc[0][0] == None):
            if(DonChainUpper10 > DonchainPrev) and (CurrentLastPrice < SMALastPrice) and (EntryQOverallVal >staticNiftyLots):
                print("-------------orderPlacePutSell : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"------BANKNIFTY-------")
                logging.info("-------------orderPlacePutSell : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"-------BANKNIFTY------")
                conn.execute("INSERT INTO OrderZerodhaBankNifty(DonChainUpper10,CurrentLastPrice,SMALastPrice,DonchainPrev,tradingSymbol,LoadDate,LoadTime,strikePrice,TradeDesc,EntryFunct,TradeType,EntryQuantity,Timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(DonChainUpper10),str(CurrentLastPrice),str(SMALastPrice),str(DonchainPrev),str(tradingSymbol),str(LatestDate),str(LatestTime),str(strikePrice),'SELL','orderPlacePutSell','ENTRY',-1,str(datetime.datetime.now())))
                db.commit()
                tradingsymbolValue=tradingSymbol.replace('NFO:','')
                exchangeValue=kite.EXCHANGE_NFO
                transaction_typeValue=kite.TRANSACTION_TYPE_SELL
                quantityValue = 50
                order_typeValue = kite.ORDER_TYPE_MARKET
                productValue = kite.PRODUCT_NRML
                placeZerodhaOrder(tradingsymbolValue,exchangeValue,transaction_typeValue,quantityValue,order_typeValue,productValue)

def orderExitCallBuy(DeltaOI,DonChainMid10,db,tradingSymbol,LatestDate,LatestTime,strikePrice,conn):
    SQLRenko ='select distinct BrickColor from Renko where IndexName="BANKNIFTY" order by SrNo desc LIMIT 2;'
    Renko = pd.read_sql(SQLRenko,db)
    if((len(Renko.index)==1 and Renko.iloc[0][0]=="RED") or(DeltaOI < DonChainMid10)):
    #if(DeltaOI < DonChainMid10):
        #print("Execute Call Buy option  "+str(strikePrice))
        SQLEntryQ = 'select sum(EntryQuantity) from OrderZerodhaBankNifty where tradingSymbol="'+tradingSymbol+'" and EntryFunct="orderPlaceCallBuy"'
        EntryQ = pd.read_sql(SQLEntryQ,db)
        if(EntryQ.iloc[0][0] != None):
            if(EntryQ.iloc[0][0] > 0):
                print("-------------orderExitCallBuy : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"-------BANKNIFTY------")
                logging.info("-------------orderExitCallBuy : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"------BANKNIFTY-------")
                conn.execute("INSERT INTO OrderZerodhaBankNifty(DeltaOI,DonChainMid10,tradingSymbol,LoadDate,LoadTime,strikePrice,TradeDesc,EntryFunct,TradeType,EntryQuantity,Timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(DeltaOI),str(DonChainMid10),str(tradingSymbol),str(LatestDate),str(LatestTime),str(strikePrice),'SELL','orderPlaceCallBuy','EXIT',-1,str(datetime.datetime.now())))
                db.commit()
                tradingsymbolValue=tradingSymbol.replace('NFO:','')
                exchangeValue=kite.EXCHANGE_NFO
                transaction_typeValue=kite.TRANSACTION_TYPE_SELL
                quantityValue = 25
                order_typeValue = kite.ORDER_TYPE_MARKET
                productValue = kite.PRODUCT_NRML
                placeZerodhaOrder(tradingsymbolValue,exchangeValue,transaction_typeValue,quantityValue,order_typeValue,productValue)

def orderExitPutBuy(DeltaOI,DonChainMid10,db,tradingSymbol,LatestDate,LatestTime,strikePrice,conn):
    SQLRenko ='select distinct BrickColor from Renko where IndexName="BANKNIFTY" order by SrNo desc LIMIT 2;'
    Renko = pd.read_sql(SQLRenko,db)
    if((len(Renko.index)==1 and Renko.iloc[0][0]=="GREEN") or (DeltaOI > DonChainMid10)):
    #if(DeltaOI > DonChainMid10):
        #print("Execute Put Buy option "+str(strikePrice))
        SQLEntryQ = 'select sum(EntryQuantity) from OrderZerodhaBankNifty where tradingSymbol="'+tradingSymbol+'" and EntryFunct="orderPlacePutBuy"'
        EntryQ = pd.read_sql(SQLEntryQ,db)
        if(EntryQ.iloc[0][0] != None):
            if(EntryQ.iloc[0][0] > 0):
                print("-------------orderExitPutBuy : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"-------BANKNIFTY------")
                logging.info("-------------orderExitPutBuy : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"-------BANKNIFTY------")
                conn.execute("INSERT INTO OrderZerodhaBankNifty(DeltaOI,DonChainMid10,tradingSymbol,LoadDate,LoadTime,strikePrice,TradeDesc,EntryFunct,TradeType,EntryQuantity,Timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(DeltaOI),str(DonChainMid10),str(tradingSymbol),str(LatestDate),str(LatestTime),str(strikePrice),'SELL','orderPlacePutBuy','EXIT',-1,str(datetime.datetime.now())))
                db.commit()
                tradingsymbolValue=tradingSymbol.replace('NFO:','')
                exchangeValue=kite.EXCHANGE_NFO
                transaction_typeValue=kite.TRANSACTION_TYPE_SELL
                quantityValue = 25
                order_typeValue = kite.ORDER_TYPE_MARKET
                productValue = kite.PRODUCT_NRML
                placeZerodhaOrder(tradingsymbolValue,exchangeValue,transaction_typeValue,quantityValue,order_typeValue,productValue)

def orderExitCallSell(DeltaOI,DonChainMid10,db,tradingSymbol,LatestDate,LatestTime,strikePrice,conn):
    if(DeltaOI > DonChainMid10):
        #print("Execute Call sell option "+str(strikePrice))
        SQLEntryQ = 'select sum(EntryQuantity) from OrderZerodhaBankNifty where tradingSymbol="'+tradingSymbol+'" and EntryFunct="orderPlaceCallSell"'
        EntryQ = pd.read_sql(SQLEntryQ,db)
        if(EntryQ.iloc[0][0] != None):
            if(EntryQ.iloc[0][0] < 0):
                print("-------------orderExitCallSell : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"------BANKNIFTY-------")
                logging.info("-------------orderExitCallSell : "+str(strikePrice)+"--------BANKNIFTY-----")
                conn.execute("INSERT INTO OrderZerodhaBankNifty(DeltaOI,DonChainMid10,tradingSymbol,LoadDate,LoadTime,strikePrice,TradeDesc,EntryFunct,TradeType,EntryQuantity,Timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(DeltaOI),str(DonChainMid10),str(tradingSymbol),str(LatestDate),str(LatestTime),str(strikePrice),'BUY','orderPlaceCallSell','EXIT',1,str(datetime.datetime.now())))
                db.commit()
                tradingsymbolValue=tradingSymbol.replace('NFO:','')
                exchangeValue=kite.EXCHANGE_NFO
                transaction_typeValue=kite.TRANSACTION_TYPE_BUY
                quantityValue = 50
                order_typeValue = kite.ORDER_TYPE_MARKET
                productValue = kite.PRODUCT_NRML
                placeZerodhaOrder(tradingsymbolValue,exchangeValue,transaction_typeValue,quantityValue,order_typeValue,productValue)

def orderExitPutSell(DeltaOI,DonChainMid10,db,tradingSymbol,LatestDate,LatestTime,strikePrice,conn):
    if(DeltaOI < DonChainMid10):
        #print("Execute Put sell option "+str(strikePrice))
        SQLEntryQ = 'select sum(EntryQuantity) from OrderZerodhaBankNifty where tradingSymbol="'+tradingSymbol+'" and EntryFunct="orderPlacePutSell"'
        EntryQ = pd.read_sql(SQLEntryQ,db)
        if(EntryQ.iloc[0][0] != None):
            if(EntryQ.iloc[0][0] < 0):
                print("-------------orderExitPutSell : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"------BANKNIFTY-------")
                logging.info("-------------orderExitPutSell : "+str(strikePrice)+" and tradingSymbol :"+str(tradingSymbol)+"------BANKNIFTY-------")
                conn.execute("INSERT INTO OrderZerodhaBankNifty(DeltaOI,DonChainMid10,tradingSymbol,LoadDate,LoadTime,strikePrice,TradeDesc,EntryFunct,TradeType,EntryQuantity,Timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(DeltaOI),str(DonChainMid10),str(tradingSymbol),str(LatestDate),str(LatestTime),str(strikePrice),'BUY','orderPlacePutSell','EXIT',1,str(datetime.datetime.now())))
                db.commit()
                tradingsymbolValue=tradingSymbol.replace('NFO:','')
                exchangeValue=kite.EXCHANGE_NFO
                transaction_typeValue=kite.TRANSACTION_TYPE_BUY
                quantityValue = 50
                order_typeValue = kite.ORDER_TYPE_MARKET
                productValue = kite.PRODUCT_NRML
                placeZerodhaOrder(tradingsymbolValue,exchangeValue,transaction_typeValue,quantityValue,order_typeValue,productValue)

def OptionChainCal():
    #try:
        #nse = Nse()
        #quoteNifty = nse.get_index_quote("nifty 50")
        #print("Nifty value" + str(quoteNifty))
        #database connection
        #conn = sqlite3.connect('Momentum.db')
        dataZerodha = pd.read_csv('zerodha.txt', header = None)
        api_key=dataZerodha.iloc[0][0]
        access_token=dataZerodha.iloc[0][1]
        URL = "https://api.kite.trade/quote?api_key=" + api_key + "&access_token=" + access_token + "&i=NSE:NIFTY+50&i=NSE:NIFTY+BANK"
        print(URL)
        
        # sending get request and saving the response as response object
        request = requests.get(url = URL)

        # extracting data in json format
        data = request.json()
        BankNiftyPrice = data["data"]["NSE:NIFTY BANK"]["last_price"]
        NiftyPrice = data["data"]["NSE:NIFTY 50"]["last_price"]
        print("BankNiftyPrice : "+str(BankNiftyPrice))
        print("NiftyPrice : "+str(NiftyPrice))

        db = mysql.connector.connect(host="localhost",user="Prutha",password="Prutha$30",database="Momentum")
        conn = db.cursor()
        #read max oad date
        #print("Got in OptionChainCalculation")
        maxdate = pd.read_sql('select max(loadDate)  from OptionChainZerodhaBankNifty ', db) 
        LatestDate = str(maxdate.iloc[0][0])
        print(LatestDate)
        #read max load time
        maxtime = pd.read_sql('select max(loadTime),min(loadTime)  from OptionChainZerodhaBankNifty where loadDate="'+LatestDate+'"', db) 
        LatestTime = maxtime.iloc[0][0]
        minTime = maxtime.iloc[0][1]
        print("Latest time :"+LatestTime)
        logging.info("Latest time :"+LatestTime)
        print("Start time : "+minTime)
        logging.info("Start time : "+minTime)
        #next Thusday logic
        Expiry = pd.read_sql('select min(expiry) from InstrumentStatic where name in ("BANKNIFTY")', db)
        Expiry=Expiry.iloc[0][0]
        #today = date.today()
        #Expiry = today + datetime.timedelta( (3-today.weekday()) % 7 )

        print('Expiry : '+str(Expiry))
        logging.info('Expiry : '+str(Expiry))
        BoundType='Upper'
        #get distinct strick price
        SQLdistinctStrikePrice = 'select distinct strikePrice  from OptionChainZerodhaBankNifty where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" and LoadTime="'+LatestTime+'";'
        
        #print(SQLdistinctStrikePrice)
        distinctStrikeP = pd.read_sql(SQLdistinctStrikePrice,db)
        print("--------------------------------------------------------------------------BANKNIFTY-------------------------------------------------------------------")
        logging.info("-------------------------------------------------------------------------BANKNIFTY--------------------------------------------------------------------")
        #print(distinctStrikeP)
        for i in range(distinctStrikeP.size):
                strikePrice = distinctStrikeP.iloc[i][0]
                #print("Strike Price :"+str(strikePrice))
                timestamp = datetime.datetime.now()
                lot = 50
                strikePricePlusSix = strikePrice + (6 * lot)
                strikePriceMinusSix = strikePrice- (6 * lot)
                #print("strikePricePlusSix " +str(strikePricePlusSix))
                #print("strikePriceMinusSix :" +str(strikePriceMinusSix))
                SQLsumOIPut = 'select sum(coalesce(OI,0))  from OptionChainZerodhaBankNifty where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" AND strikePrice between '+str(strikePriceMinusSix)+' and '+str(strikePricePlusSix)+' and OptionType ="'+'PE'+'" and LoadTime="'+LatestTime+'";'
                #print(SQLsumOIPut)
                SQLsumOICall = 'select sum(coalesce(OI,0))  from OptionChainZerodhaBankNifty where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" AND strikePrice between '+str(strikePriceMinusSix)+' and '+str(strikePricePlusSix)+' and OptionType ="'+'CE'+'" and LoadTime="'+LatestTime+'";'
                #print(SQLsumOICall)
                sumOIPut = pd.read_sql(SQLsumOIPut,db)
                sumOICall = pd.read_sql(SQLsumOICall,db)
                #print(sumOIPut.fillna(0))
                
                DeltaOI = sumOIPut.fillna(0) - sumOICall.fillna(0)
                DeltaOI = DeltaOI.iloc[0][0]
                #print("Delta OI : " + str(DeltaOI))

                DonChainUpper20 = DeltaOI
                DonChainLowerP20 = DeltaOI

                DonChainUpper10 = DeltaOI
                DonChainLower10 = DeltaOI

                DonChainMid10 = DeltaOI
                DonChainMid20 = DeltaOI

                DonChainWidth10 = DeltaOI
                DonChainWidth20 = DeltaOI


                if(LatestTime == minTime):
                    BoundValue = 25000 + DeltaOI
                    #print("In 0 ")
                else:
                    SQLLowestDT20 = 'SELECT min(DeltaIO) FROM (SELECT DeltaIO ,LoadTime FROM DeltaOIZerodhaTBankNifty A where LoadDate = "'+LatestDate+'"  and strikePrice='+str(strikePrice)+' and  expiryDate ="'+str(Expiry)+'" ORDER BY timestamp DESC LIMIT 20) A'
                    #print(SQLLowestDT20)
                    LowestDT20 = pd.read_sql(SQLLowestDT20,db)
                    SQLHighestDT20 = 'SELECT max(DeltaIO) FROM (SELECT DeltaIO ,LoadTime FROM DeltaOIZerodhaTBankNifty A where LoadDate = "'+LatestDate+'"  and strikePrice='+str(strikePrice)+' and  expiryDate ="'+str(Expiry)+'"  ORDER BY timestamp DESC LIMIT 20) A'
                    #print(SQLHighestDT20)
                    HighestDT20 = pd.read_sql(SQLHighestDT20,db)

                    SQLLowestDT10 = 'SELECT min(DeltaIO) FROM (SELECT DeltaIO ,LoadTime FROM DeltaOIZerodhaTBankNifty A where LoadDate = "'+LatestDate+'"  and strikePrice='+str(strikePrice)+' and  expiryDate ="'+str(Expiry)+'"  ORDER BY timestamp DESC LIMIT 10) A'
                    #print(SQLLowestDT10)
                    LowestDT10 = pd.read_sql(SQLLowestDT10,db)
                    #print(LowestDT10)
                    SQLHighestDT10 = 'SELECT max(DeltaIO) FROM (SELECT DeltaIO ,LoadTime FROM DeltaOIZerodhaTBankNifty A where LoadDate = "'+LatestDate+'"  and strikePrice='+str(strikePrice)+' and  expiryDate ="'+str(Expiry)+'" ORDER BY timestamp DESC LIMIT 10) A'
                    #print(SQLHighestDT10)
                    HighestDT10 = pd.read_sql(SQLHighestDT10,db)
                    #print(HighestDT10)

                    DonChainUpper20 = HighestDT20.iloc[0][0]
                    DonChainLowerP20 = LowestDT20.iloc[0][0]

                    DonChainUpper10 = HighestDT10.iloc[0][0]
                    DonChainLower10 = LowestDT10.iloc[0][0]

                    DonChainUpper20 = max(DonChainUpper20,DeltaOI)
                    DonChainUpper10 = max(DonChainUpper10,DeltaOI)

                    DonChainLowerP20 = min(DonChainLowerP20,DeltaOI)
                    DonChainLower10 = min(DonChainLower10,DeltaOI)

                    DonChainMid10 = (DonChainLower10 + DonChainUpper10)/2
                    DonChainMid20 = (DonChainLowerP20 + DonChainUpper20)/2

                    DonChainWidth10 = (DonChainUpper10-DonChainLower10)
                    DonChainWidth20 = (DonChainUpper20-DonChainLowerP20)
                
                CurrentLastPriceCall = 0
                CurrentOICall = 0
                SMALastPriceCall = 0
                SMAOICall = 0
                DonchainPrevCall = 0
                CurrentLastPricePut = 0
                CurrentOIPut = 0
                SMALastPricePut = 0
                SMAOIPut = 0
                DonchainPrevPut = 0     
                CurrentLastPrice = 0
                CurrentOI = 0
                SMALastPrice = 0
                SMAOI = 0
                DonchainPrev = 0          
                # Call Buy
                if(strikePrice > (BankNiftyPrice * 0.997) ) and (strikePrice < (BankNiftyPrice * 1.003) and datetime.datetime.now().time()>datetime.time(9,42)):
                    SQLCallDataBuy = 'select label, Value    from ( \
                        SELECT coalesce(DonChainUpper10,0) as Value, "DonchainPrev" as label  FROM (SELECT DonChainUpper10 ,LoadTime FROM DeltaOIZerodhaTBankNifty  where LoadDate = "'+LatestDate+'"  and strikePrice='+str(strikePrice)+' and  expiryDate ="'+str(Expiry)+'"  ORDER BY timestamp DESC LIMIT 1) B \
                        union \
                        select coalesce(OI,0) ,"CurrentOI"  from OptionChainZerodhaBankNifty where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" AND strikePrice ='+str(strikePrice)+' and OptionType ="CE" and LoadTime="'+LatestTime+'" \
                        union \
                        SELECT avg(coalesce(OI,0)),"SMAOI" FROM (SELECT OI ,LoadTime FROM OptionChainZerodhaBankNifty A where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" AND strikePrice ='+str(strikePrice)+' and OptionType ="CE"  ORDER BY timestamp DESC LIMIT 20) C \
                        union \
                        select coalesce(last_price,0) ,"CurrentLastPrice" from OptionChainZerodhaBankNifty where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" AND strikePrice ='+str(strikePrice)+' and OptionType ="CE" and LoadTime="'+LatestTime+'" \
                        union \
                        SELECT avg(coalesce(last_price,0)) ,"SMALastPrice" FROM (SELECT last_price ,LoadTime FROM OptionChainZerodhaBankNifty A where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" AND strikePrice ='+str(strikePrice)+' and OptionType ="CE"  ORDER BY timestamp DESC LIMIT 10) D \
                        ) A'
                    
                    #print(SQLCallData)
                    CallDataBuy = pd.read_sql(SQLCallDataBuy,db)
                    #print(CallData)

                    for x in CallDataBuy.index:
                        if(CallDataBuy.iloc[x][0]) == 'CurrentLastPrice':
                            CurrentLastPriceCall =CallDataBuy.iloc[x][1]
                            #print("CurrentLastPrice"+str(CurrentLastPrice))
                        if(CallDataBuy.iloc[x][0]) == 'CurrentOI':
                            CurrentOICall = CallDataBuy.iloc[x][1]
                            #print("CurrentOI"+str(CurrentOI))
                        if(CallDataBuy.iloc[x][0]) == 'SMALastPrice':
                            SMALastPriceCall = CallDataBuy.iloc[x][1]
                            #print("SMALastPrice"+str(SMALastPrice))
                        if(CallDataBuy.iloc[x][0]) == 'SMAOI':
                            SMAOICall = CallDataBuy.iloc[x][1]
                            #print("SMAOI"+str(SMAOI))
                        if(CallDataBuy.iloc[x][0]) == 'DonchainPrev':
                            DonchainPrevCall = CallDataBuy.iloc[x][1]
                            #print("DonchainPrev"+str(DonchainPrev))
                        
                        #Put Buy
                        SQLPutDataBuy ='select label, Value    from ( \
                            SELECT coalesce(DonChainLower10,0) as Value, "DonchainPrev" as label  FROM (SELECT DonChainLower10 ,LoadTime FROM DeltaOIZerodhaTBankNifty  where LoadDate = "'+LatestDate+'"  and strikePrice='+str(strikePrice)+' and  expiryDate ="'+str(Expiry)+'"  ORDER BY timestamp DESC LIMIT 1) B \
                            union \
                            select coalesce(OI,0) ,"CurrentOI"  from OptionChainZerodhaBankNifty where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" AND strikePrice ='+str(strikePrice)+' and OptionType ="PE" and LoadTime="'+LatestTime+'" \
                            union \
                            SELECT avg(coalesce(OI,0)),"SMAOI" FROM (SELECT OI ,LoadTime FROM OptionChainZerodhaBankNifty A where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" AND strikePrice ='+str(strikePrice)+' and OptionType ="PE"  ORDER BY timestamp DESC LIMIT 20) C \
                            union \
                            select coalesce(last_price,0) ,"CurrentLastPrice" from OptionChainZerodhaBankNifty where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" AND strikePrice ='+str(strikePrice)+' and OptionType ="PE" and LoadTime="'+LatestTime+'" \
                            union \
                            SELECT avg(coalesce(last_price,0)) ,"SMALastPrice" FROM (SELECT last_price ,LoadTime FROM OptionChainZerodhaBankNifty A where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" AND strikePrice ='+str(strikePrice)+' and OptionType ="PE"  ORDER BY timestamp DESC LIMIT 10) D\
                            ) A'
                        
                        #print(SQLCallData)
                        PutDataBuy = pd.read_sql(SQLPutDataBuy,db)
                        #print(CallData)

                        for x in PutDataBuy.index:
                            if(PutDataBuy.iloc[x][0]) == 'CurrentLastPrice':
                                CurrentLastPricePut = PutDataBuy.iloc[x][1]
                                #print("CurrentLastPrice"+str(CurrentLastPrice))
                            if(PutDataBuy.iloc[x][0]) == 'CurrentOI':
                                CurrentOIPut = PutDataBuy.iloc[x][1]
                                #print("CurrentOI"+str(CurrentOI))
                            if(PutDataBuy.iloc[x][0]) == 'SMALastPrice':
                                SMALastPricePut = PutDataBuy.iloc[x][1]
                                #print("SMALastPrice"+str(SMALastPrice))
                            if(PutDataBuy.iloc[x][0]) == 'SMAOI':
                                SMAOIPut = PutDataBuy.iloc[x][1]
                                #print("SMAOI"+str(SMAOI))
                            if(PutDataBuy.iloc[x][0]) == 'DonchainPrev':
                                DonchainPrevPut = PutDataBuy.iloc[x][1]
                                #print("DonchainPrev"+str(DonchainPrev))
                
                #print(str(timestamp)+","+str(strikePrice)+","+str(Expiry)+","+str(DeltaOI)+","+str(LatestDate)+","+LatestTime+","+str(DonChainUpper20 )+","+str(DonChainLowerP20)+","+str(DonChainUpper10 )+","+str(DonChainLower10 )+","+str(DonChainMid10   )+","+str(DonChainMid20   )+","+str(DonChainWidth10 )+","+str(DonChainWidth20 ))
                conn.execute("INSERT INTO DeltaOIZerodhaTBankNifty(timestamp,strikePrice,expiryDate,DeltaIO,LoadDate,LoadTime,DonChainUpper20  ,DonChainLowerP20 ,DonChainUpper10  ,DonChainLower10  ,DonChainMid10    ,DonChainMid20    ,DonChainWidth10  ,DonChainWidth20  ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(str(timestamp),str(float(strikePrice)),str(Expiry),str(float(DeltaOI)),LatestDate,LatestTime,str(float(DonChainUpper20 )),str(float(DonChainLowerP20)),str(float(DonChainUpper10) ),str(float(DonChainLower10 )),str(float(DonChainMid10 )  ),str(float(DonChainMid20   )),str(float(DonChainWidth10 )),str(float(DonChainWidth20 ))))
                db.commit()
                
                SQLTradingSymbolCE = 'select distinct TradingSymbol  from OptionChainZerodhaBankNifty where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" AND strikePrice ='+str(strikePrice)+' and OptionType ="'+'CE'+'" and LoadTime="'+LatestTime+'"'
                TradingSymbolCE = pd.read_sql(SQLTradingSymbolCE,db)

                SQLTradingSymbolPE = 'select distinct TradingSymbol  from OptionChainZerodhaBankNifty where loadDate="'+LatestDate+'" and Expirty_dt="'+str(Expiry)+'" AND strikePrice ='+str(strikePrice)+' and OptionType ="'+'PE'+'" and LoadTime="'+LatestTime+'"'
                TradingSymbolPE = pd.read_sql(SQLTradingSymbolPE,db)
                
                if(strikePrice > (BankNiftyPrice * 0.997) ) and (strikePrice < (BankNiftyPrice * 1.003) and datetime.datetime.now().time()>datetime.time(9,42)):
                #if(strikePrice > (quoteNifty.get("lastPrice") * 0.995) ) and (strikePrice < (quoteNifty.get("lastPrice") * 1.005) and datetime.datetime.now().time()>datetime.time(9,42)):
                    #print("IN-------------------")
                    orderPlaceCallBuy(DonChainUpper10,DonchainPrevCall,CurrentLastPriceCall,SMALastPriceCall,CurrentOICall,SMAOICall,db,TradingSymbolCE.iloc[0][0],LatestDate,LatestTime,strikePrice,conn)
                    orderPlacePutBuy(DonChainLower10,DonchainPrevPut,CurrentLastPricePut,SMALastPricePut,CurrentOIPut,SMAOIPut,db,TradingSymbolPE.iloc[0][0],LatestDate,LatestTime,strikePrice,conn)
                    orderPlaceCallSell(DonChainLower10,DonchainPrevPut,CurrentLastPriceCall,SMALastPriceCall,db,TradingSymbolCE.iloc[0][0],LatestDate,LatestTime,strikePrice,conn,BankNiftyPrice)
                    orderPlacePutSell(DonChainUpper10,DonchainPrevCall,CurrentLastPricePut,SMALastPricePut,db,TradingSymbolPE.iloc[0][0],LatestDate,LatestTime,strikePrice,conn,BankNiftyPrice)

                orderExitCallBuy(DeltaOI,DonChainMid10,db,TradingSymbolCE.iloc[0][0],LatestDate,LatestTime,strikePrice,conn)
                orderExitCallSell(DeltaOI,DonChainMid10,db,TradingSymbolCE.iloc[0][0],LatestDate,LatestTime,strikePrice,conn)
                orderExitPutBuy(DeltaOI,DonChainMid10,db,TradingSymbolPE.iloc[0][0],LatestDate,LatestTime,strikePrice,conn)
                orderExitPutSell(DeltaOI,DonChainMid10,db,TradingSymbolPE.iloc[0][0],LatestDate,LatestTime,strikePrice,conn)

                #print("Inserted")
        print("Data Inserted to Delta OI Bank Nifty table at "+str(datetime.datetime.now() ))
        logging.info("Data Inserted to Delta OI Bank Nifty table at "+str(datetime.datetime.now() ))
        print("---------------------------------------------------------------BANKNIFTY------------------------------------------------------------------------------")
        logging.info("-------------------------------------------------------------------BANKNIFTY--------------------------------------------------------------------------")
        conn.close()
   


if __name__ == '__main__':
    OptionChainCal()