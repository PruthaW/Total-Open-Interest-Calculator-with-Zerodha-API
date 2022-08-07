import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Cursor
#import sqlite3
import pandas as pd
import matplotlib.dates as mdates
import mysql.connector

while('TRUE'):
    strikePrice = input("Enter Strike Price:")
    print("strikePrice is: " + strikePrice)

    fig = plt.figure()
    
    ax1 = fig.add_subplot(1,1,1)

    def animate(i):
        #print("Here ")
        db = mysql.connector.connect(host="localhost",user="Username",password="Password",database="DBName")
        DeltaIoPlot=pd.read_sql('select strikePrice,DeltaIO,LoadDate,LoadTime,DonChainLowerP20 ,DonChainUpper20,DonChainUpper10  ,DonChainLower10, DonChainMid10 from DeltaOIZerodhaTBankNifty where strikePrice='+strikePrice+' and loaddate ="2021-09-06"    order by LoadDate,loadTime ', db) 

        ax1.clear()
        x=DeltaIoPlot["LoadTime"].map(lambda x: str(x)[:-10])
        ax1.tick_params(axis='x', labelrotation = 90)
        plt.title("Donchain 10 BANKNIFTY for "+ strikePrice)
        
        ax1.plot(x, DeltaIoPlot["DonChainUpper10"],label='Second plot')
        ax1.plot(x, DeltaIoPlot["DonChainLower10"],label='Thrid plot')
        ax1.plot(x, DeltaIoPlot["DeltaIO"],label='first plot')
        db.close()



    ani = animation.FuncAnimation(fig, animate, interval=9000)
    plt.show()
