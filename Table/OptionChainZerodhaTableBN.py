import mysql.connector


mydb = mysql.connector.connect(host="localhost",user="Username",password="Password",database="DBName")
conn = mydb.cursor()
#print "Opened database successfully";

conn.execute('''CREATE TABLE OptionChainZerodhaBankNifty
         (timestamp 		VarCHar(30),
         TradingSymbol 	VarCHar(30), 
         LoadDate		Date,
         LoadTime        VarCHar(30),
         OI          	Float(10,2),
         Last_price  	Float(10,2),
         Last_quantity 	Int(10),
         Buy_quantity 	Int(10),
         Sell_quantity 	Int(10),
         Volume 		Int(15),
         Average_price 	Float(10,2),
         OI_day_high 	Float(10,2),
         OI_day_low 	Float(10,2),
         OHLC_Open 		Float(10,2),
         OHLC_High 		Float(10,2),
         OHLC_Low 		Float(10,2),
         OHLC_Close 	Float(10,2),
         Name 			VarCHar(30),
         Expirty_dt 	Date,
         Strikeprice 	Float(10,2) ,
         OptionType 	VarCHar(30),
         primary key (LoadDate,LoadTime,TradingSymbol,Expirty_dt,Strikeprice,OptionType)
         );''');

mydb.commit();

conn.close();
