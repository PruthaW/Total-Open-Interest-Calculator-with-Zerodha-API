import mysql.connector

mydb = mysql.connector.connect(host="localhost",user="Username",password="Password",database="DBname")
conn = mydb.cursor()
#print "Opened database successfully";

conn.execute('''CREATE TABLE DeltaOIZerodhaTBankNifty
         (strikePrice  		Float(10,2) NOT NULL,
		 expiryDate  		Date NOT NULL,
		 LoadDate 			DATE NOT NULL,
         LoadTime 			VarCHar(30) NOT NULL,
		 DeltaIO 			Float(10,2),
		 Timestamp 			Timestamp,
		 DonChainUpper20 	Float(10,2),
		 DonChainLowerP20 	Float(10,2),
		 DonChainUpper10 	Float(10,2),
		 DonChainLower10 	Float(10,2),
		 DonChainMid10 		Float(10,2),
		 DonChainMid20 		Float(10,2),
		 DonChainWidth10 	Float(10,2),
		 DonChainWidth20 	Float(10,2),
		 PRIMARY KEY (LoadDate,LoadTime, expiryDate,strikePrice)
         );''');

mydb.commit();

conn.close();
