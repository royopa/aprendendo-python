#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import Quandl

#petr4 = Quandl.get("GOOG/BVMF_PETR4", authtoken="m2atjgMb4x11YczvyR_Q")
#print(petr4.index)
#print(petr4.head())
#print(petr4)
#Note que petr4 é um DataFrame pandas, caso não queira ou não goste de trabalhar
#com pandas é possível obter os dados em um numpy array.

#petr4_np = Quandl.get("GOOG/BVMF_PETR4", returns='numpy', authtoken="m2atjgMb4x11YczvyR_Q")
#print(petr4_np.shape)
#print(petr4_np)


#Uma opção que eu acho muito legal é a opção de baixar os últimos n registros,
#pois pensando em processamento diário eu não precisaria ficar especificando as
#datas para download, sabendo sempre que a data atual é a referência. Para isso
#basta utilizar os parâmetros rows=n e sort_order='desc'. Vamos utilizar isso para
#baixar a última divulgação da taxa CDI da CETIP.
cdi = Quandl.get("BCB/4389", rows=1, sort_order='desc', authtoken="m2atjgMb4x11YczvyR_Q")
print(cdi)


#último ipca
ipca = Quandl.get("BCB/13522", rows=1, sort_order='desc', authtoken="m2atjgMb4x11YczvyR_Q")
print(ipca)


#Outra opção interessante, que eu particularmente não uso muito, é a definição de
#frequência dos dados. No entanto, as vezes é interessante analisar as séries temporais
#em frequências menores como mensal ou anual. Vamos ver como baixar os dados do Índice
#Bovespa em cotação mensal.
#bvsp = Quandl.get("YAHOO/INDEX_BVSP", collapse="monthly")
#print(bvsp.head(10))

ceoc11b = Quandl.get("GOOG/BVMF_CEOC11B", authtoken="m2atjgMb4x11YczvyR_Q")
print(ceoc11b)
