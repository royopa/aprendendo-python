#!/usr/bin/env python2
# -*- coding: utf-8 -*-


from pandas.io.data import DataReader

import matplotlib.pyplot as plt
import datetime
import pandas as pd
import numpy as np


###############################################################################
# Retrieve the data from Internet

# Choose a time period 
d1 = datetime.datetime(2014, 4, 1) #startDate
d2 = datetime.datetime(2015, 4, 1) #endDate

#get the tickers
stock = "PETR4.SA"
price = DataReader(stock, "yahoo",d1,d2)['Adj Close']
price = price.asfreq('B').fillna(method='pad')

ret = price.pct_change()

#choose the quantile
quantile=0.05
#the vol window
volwindow=50
#and the Var window for rolling 
varwindow=250


#simple VaR using all the data
unnormedquantile=pd.expanding_quantile(ret,quantile)

#similar one using a rolling window 
unnormedquantileR=pd.rolling_quantile(ret,varwindow,quantile)

#we can also normalize the returns by the vol
vol=pd.rolling_std(ret,volwindow)*np.sqrt(256)
unitvol=ret/vol

#and get the expanding or rolling quantiles
Var=pd.expanding_quantile(unitvol,quantile)
VarR=pd.rolling_quantile(unitvol,varwindow,quantile)

normedquantile=Var*vol
normedquantileR=VarR*vol


ret2=ret.shift(-1)

courbe=pd.DataFrame({'returns':ret2,
              'quantiles':unnormedquantile,
              'Rolling quantiles':unnormedquantileR,
              'Normed quantiles':normedquantile,
              'Rolling Normed quantiles':normedquantileR,
              })
courbe.plot()
plt.show()

courbe['nqBreak']=np.sign(ret2-normedquantile)/(-2) +0.5
courbe['nqBreakR']=np.sign(ret2-normedquantileR)/(-2) +0.5
courbe['UnqBreak']=np.sign(ret2-unnormedquantile)/(-2) +0.5
courbe['UnqBreakR']=np.sign(ret2-unnormedquantileR)/(-2) +0.5


nbdays=price.count()

print( 'Number of returns worse than the VaR')
print( 'Ideal Var                : ', (quantile)*nbdays)
print( 'Simple VaR               : ', np.sum(courbe['UnqBreak']))
print( 'Normalized VaR           : ', np.sum(courbe['nqBreak']))
print( '---------------------------')
print( 'Ideal Rolling Var        : ', (quantile)*(nbdays-varwindow))
print( 'Rolling VaR              : ', np.sum(courbe['UnqBreakR']))
print( 'Rolling Normalized VaR   : ', np.sum(courbe['nqBreakR']))
