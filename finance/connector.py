# coding:utf-8

"""
Esse módulo faz uma conexão a partir de um proxy se o usuário prover a classe 
com login e senha, ou conecta diretamente na url caso contrário.

"""

__version__ = '0.01'
__date__    = '2013-12-31'
__author__  = 'Liz Alexandrita de Souza Barreto'

#--- LICENSE -------------------------------------------------------------------
# 
#--- CHANGES -------------------------------------------------------------------
#
#--- TO DO ---------------------------------------------------------------------
#	* Criar função para pegar o endereço mais recente do proxy para ser usado. 
#	  A lista de proxies se encontra em http://webcorporativo/proxy/websense.pac
#	  E não esqueça de adicionar o unittest referente à sua nova função. Oras.
#	* Criar função que decida usar ou não conexão com o proxy pelas regras
#	  encontradas também em http://webcorporativo/proxy/websense.pac
#	* Adicionar headers. 
#	* 
# ------------------------------------------------------------------------------

import passwd
import urllib
import urllib2
import cookielib
import pickle
import signal

class Connector(object):
    def __init__(self, user):
        username = user['username']
        password = user['password']
        # Se o dicionário do usuário estiver vazio, não use proxy.
        if user['username'] == '' or user['password'] == '':
        	proxy_handler = urllib2.ProxyHandler({})
        	# Sempre guarde os cookies. Trust me on this...
        	cj = cookielib.LWPCookieJar()
        	self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        else:
        	# Quando houver login e senha, conecte ao proxy HARDCODED - Yuuuuk
        	proxy_handler = urllib2.ProxyHandler({'http': 'http://10.0.0.24:8080/'})
        	proxy_auth_handler = urllib2.HTTPBasicAuthHandler()
        	proxy_auth_handler.add_password('realm', 'host', username, password)
        	cj = cookielib.LWPCookieJar()
        	self.opener = urllib2.build_opener(proxy_handler, proxy_auth_handler,urllib2.HTTPCookieProcessor(cj))

    def read(self, url):
    	# Lê e devolve o conteúdo diretamente de url, ou requests
    	ret = self.opener.open(url)
    	self.content = ret.read()
    	return self.content
    	
    def parametric_connection(self, url, **form_param):
    	# Faz conexão com formulário de dados e devolve uma instância de request
    	form_param_encoded = urllib.urlencode(form_param)
    	req = urllib2.Request(url, form_param_encoded)
    	return req
