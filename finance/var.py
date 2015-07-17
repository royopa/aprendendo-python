#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Choose a time period
d1 = datetime.datetime(2001, 1, 1)
d2 = datetime.datetime(2012, 1, 1)

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