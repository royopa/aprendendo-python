#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
from datetime import date
import Quandl


# Faz a consulta de dados históricos do Quandl e retorna um array Numpy
def get_prices(stock, startDate, endDate):
    # Retorna os últimos 252 registros de cotaçÃµes
    data = Quandl.get(
        stock, trim_start=startDate,
        trim_end=endDate,
        returns="numpy"
    )

    return data


# Verifica se existe datas faltando entre dados históricos da ação e de mercado
def check_missing_date_prices(stock_prices, market_prices):
    # transforma os dados históricos num array com de datas de preços
    stock_dates = get_datas_by_prices(stock_prices)
    # transforma os dados históricos num array com de datas de mercdo
    market_dates = get_datas_by_prices(market_prices)

    for stock_date in stock_dates:
        if stock_date not in market_dates:
            print('Data não existe nos dados de mercado: ', stock_date)

    for market_date in market_dates:
        if market_date not in stock_dates:
            print('Data não existe nos dados da ação: ', market_date)

    return False


# Transforma o array de preços retornados pelo Quantl num array de datas
def get_datas_by_prices(prices):

    # array com as datas que serão armazenadas
    datas = []

    # Percorre cada linha (ou seja, dia a dia)
    for price in prices:
        # Adiciona o elemento data no array
        datas.append(price[0])

    # Retorna os resultados
    return datas


# Transforma o array de preços retornados pelo Quantl
# num array Numpy somente com os preços de fechamento (index)
def get_closing_prices(prices, index):

    # preços de fechamento que serão os preços de fechamento diÃƒÂ¡rios
    closing_prices = []

    # Percorre cada linha (ou seja, dia a dia)
    for price in prices:
        # Adiciona o elemento preço de fechamento no array, depois
        # de convertÃƒÂª-lo para float
        closing_prices.append(float(price[index]))

    # Retorna os resultados como um array Numpy
    return np.array(closing_prices)


# Calcula o beta de uma ação dados os preços bem como os preços para o mercado
# como um todo (como um índice, Bovespa por exemplo).
# Os dois arrays devem ter o mesmo tamanho.
# O resultado é o beta arredondado com duas casas decimais
def calc_beta(stock, market):

    # Calcula e armazena o tamanho dos arrays porque eles serão usados vÃ¡rias
    stock_len = len(stock)
    market_len = len(market)

    # Decide qual o conjunto de dados tem menos itens, pois para calcular o
    # beta é necessÃ¡rio que os dados da ação e de mercado tenha a mesma
    # quantidade de registros
    smallest = market_len
    if stock_len < market_len:
        smallest = stock_len

    # Cria zero arrays que serão preenchidos com os retornos das açÃµes.
    # Os dados de retorno sempre serão uma unidade menor do que os arrays
    # originais
    stock_ret = np.zeros(smallest - 1)
    market_ret = np.zeros(smallest - 1)

    # Percorre cada preço dado
    for cur in range(smallest - 1):
        # O retorno é igual ao preço atual dividido pelo preço anterior menos 1.
        # Devido a isso, vamos sempre começar com o segundo preço
        stock_ret[cur] = (stock[cur + 1] / stock[cur]) - 1
        market_ret[cur] = (market[cur + 1] / market[cur]) - 1

    covar_stock_market = np.cov(stock_ret, market_ret)[0, 1]
    print('Covariância ação/mercado: ', covar_stock_market)

    var_market = np.var(market_ret)
    print('Variância mercado: ', var_market)

    # Beta é igual a covariância do ativo e dos retornos do mercado,
    # dividido pela variância dos retornos do mercado.
    # Além disso, estou arredondado o beta para duas casas decimais.
    return np.around(covar_stock_market / var_market, decimals=2)

# data atual
today = date.today()
# data de início para pegar os dados de mercado - 5 anos
startDate = date(today.year - 5, today.month, today.day)
startDate = '2009-05-07'
endDate = '2011-12-16'

# pega os dados do índice Bovespa
stock = 'YAHOO/INDEX_BVSP'
market_prices = get_prices(stock, startDate, endDate)
# print(market_prices)
print('Mercado:', stock[stock.find('/')+1:])

# para os dados do YAHOO o índice de preço de fechamento ajustado é o 6
# ["Date","Open","High","Low","Close","Volume","Adjusted Close"]
closing_prices_stock = get_closing_prices(market_prices, 6)
# print(closing_prices_stock)

# pega os dados da ação PETR4
stock = 'GOOG/BVMF_USIM5'
stock_prices = get_prices(stock, startDate, today)
# print(stock_prices)
print('Ação:', stock[stock.find('/')+1:])

# verifica se existe alguma data faltando entre os dados históricos
# por exemplo, feriados municipais quando a Bovespa não funciona
#check_missing_date_prices(stock_prices, market_prices)

# para os dados do GOOGLE o índice de preço de fechamento é o 4
# ["Date","Open","High","Low","Close","Volume"]
closing_prices_market = get_closing_prices(stock_prices, 4)
# print(closing_prices_market)

beta = calc_beta(closing_prices_stock, closing_prices_market)
print('O beta é = ', beta)
