import mysql.connector

mydb = mysql.connector.connect(host="localhost",user="Username",password="Password",database="DBName")
conn = mydb.cursor()
#print "Opened database successfully";

conn.execute('''CREATE TABLE OrderZerodhaBankNifty
         (TradingSymbol         VarCHar(30) NOT NULL,
         TradeDesc              VarCHar(30) ,
		 TradeType              VarCHar(30) ,
         EntryFunct             VarCHar(30),
		 EntryTime              Timestamp,
         EntryPrice             Float(10,2) ,
		 EntryQuantity          Float(10,2),
		 LoadDate               DATE,
		 LoadTime               VarCHar(30),
         Timestamp              Timestamp,
         CurrentLastPrice       Float(10,2),
         CurrentOI              Float(10,2),
         SMALastPrice           Float(10,2),
         SMAOI                  Float(10,2),
         DonchainPrev           Float(10,2),
         strikePrice            Float(10,2),
         DonChainUpper10        Float(10,2),
         DonChainLower10        Float(10,2),
         DeltaOI                Float(10,2),
         DonChainMid10          Float(10,2)
         );''');
#PRIMARY KEY (TradingSymbol,TradeType, EntryTime,EntryPrice,EntryQuentity,LoadDate,)
mydb.commit();

conn.close();