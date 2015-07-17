# coding:utf-8

"""
Esse módulo faz o parser dos indicadores publicados pela Bolsa.
Possui funções de criação de urls de alguns sites que servirão de comparação
para os publicados.
"""

__version__ = '0.1'
__date__    = '2013-12-31'
__author__  = 'Liz Alexandrita de Souza Barreto'

#--- LICENSE -------------------------------------------------------------------
#
#--- CHANGES -------------------------------------------------------------------
# 
#--- TO DO ---------------------------------------------------------------------
#	* Transformar esse módulo em duas classes, uma só com as funções auxiliares
#	  e outra só com os parsers das publicações.
#	* Tirar as funções que lidam com sites externos desse módulo e colocar no
#	  módulo parsers.py
#	* Generalizar a função published_options para lidar com arquivos do RAPID de
#	  quaisquer ativos, published_RAPID_assets
#	* Adicionar os unittests dos índicadores que faltam (test_validation.py)
#	* 
#-------------------------------------------------------------------------------

import parsers
import re
import locale
from datetime import date, datetime, timedelta
import calendar
from decimal import *
import bizdays as bd


def ntn_date_creator(dateISOformat):
	# Gera uma data no formato que as urls das ntns usam
	dateISOformat = datetime.strptime(dateISOformat,"%Y-%m-%d")
	locale.setlocale(locale.LC_TIME,'ptb')
	return dateISOformat.strftime('%d%b%Y')

def merc_sec_sites(dateISOformat, site):
	# Gera as urls do mercado secundário da anbima que as ntns usam
	return {
		'igpm_ntnc':'http://www.anbima.com.br/merc_sec/resultados/msec_'+ ntn_date_creator(dateISOformat) + '_ntn-c.asp',
		'ipca_ntnb':'http://www.anbima.com.br/merc_sec/resultados/msec_'+ ntn_date_creator(dateISOformat) + '_ntn-b.asp',
		'ntnbcf_ltn_lft_anbima':'http://www.anbima.com.br/merc_sec/arqs/ms' + datetime.strptime(dateISOformat,"%Y-%m-%d").strftime('%y%m%d') + '.txt'
	}[site] # Fala sério esse switch é genial. Diguidim.

def ptax_url(dateISOformat):
	# Gera a url na qual o Banco Central disponibiliza o arquivo csv da ptax
	dateISOformat = datetime.strptime(dateISOformat,"%Y-%m-%d")
	base_url = 'http://www4.bcb.gov.br/Download/fechamento/'
	date_url = dateISOformat.strftime('%Y%m%d')
	ext = '.csv'
	return base_url + date_url + ext
	
def tr_tbf_maturity(dateISOformat):
	# Gera o intervalo entre as datas de vencimento e referência da TR e da TBF
	dateISOformat = datetime.strptime(dateISOformat,"%Y-%m-%d").date()
	tr_tbf_maturity = []
	# Gera o delta de dias a partir de "ontem" para trás até ajustar a data de 
	# referência com a de vencimento.
	# Para tirar mais dúvidas sobre isso, ou entre no DFA Taxas Referenciais e
	# verifique os padrões das datas, veja o unittest dessa função e consulte
	# o sistema do BaCen
	if dateISOformat.month == 1: # Trata a exceção de janeiro 
		delta = 1
	else:
		delta = calendar.monthrange(dateISOformat.year,dateISOformat.month)[1]-calendar.monthrange(dateISOformat.year,dateISOformat.month-1)[1]
		if (datetime(dateISOformat.year,dateISOformat.month,dateISOformat.day)-timedelta(days=1)).day == calendar.monthrange(dateISOformat.year,dateISOformat.month-1)[1]:
			delta+=1
	
	for i in range(0,delta):
		if dateISOformat.month + 1 == 13: # Trata a exceção de dezembro 
			tr_tbf_maturity.append((datetime(dateISOformat.year+1,1,dateISOformat.day)-timedelta(days=i)).date().isoformat())
		else:
			tr_tbf_maturity.append((datetime(dateISOformat.year,dateISOformat.month+1,dateISOformat.day)-timedelta(days=i)).date().isoformat())

	return tr_tbf_maturity


def fparser(parser_name, content):
	# Retorna o resultado das funções da biblioteca parsers.py
	return getattr(parsers, parser_name)(content)

def validation_parser(content, boletim):
	# Retorna um dicionário com todas as publicações do site da BM&F Bovespa
	# que conseguem conectar. Site parseado (Õ.o):
	'http://www.bmf.com.br/bmfbovespa/pages/boletim1/bd_manual/indicadoresFinanceiros1.asp'
	
	selic = published_selic(content)
	igpm = published_igpm(content)
	ipca = published_ipca(content)
	igpm_index = published_igpm_index(content)
	ipca_index = published_ipca_index(content)
	cdi_cetip = published_cdi_cetip(content)
	euro_bce = published_euro_bce(content)
	irfm_anbima = published_irfm_anbima(boletim)
	#tr_tbf = published_tr_tbf(boletim) # Fica comentado até resolver o problema
	# da conexão com o site da tr_tbf - do banco central
	return dict(
		selic = selic,
		igpm = igpm,
		ipca = ipca,
		igpm_index = igpm_index,
		ipca_index = ipca_index,
		cdi_cetip = cdi_cetip,
		euro_bce = euro_bce,
		irfm_anbima = irfm_anbima,
		#tr_tbf = tr_tbf
		)

def published_igpm(content):
	igpm = {}
	igpm['id'] = 'IGPM_ANBIMA'
	igpm['date'] = parsers.dateISOer(re.findall('\*Expectativa IGP-M.*para[^\d]*(\d*.\d*.\d*)',content)[0])
	igpm['value'] = re.findall('\*Expectativa IGP-M.*para[^\d]*\d*.\d*.\d*.*[^\d]* (\d*.\d*)%',content)[0]
	igpm['value'] = igpm['value'].replace(',','.')
	return igpm

	
def published_ipca(content):
	ipca = {}
	ipca['id'] = 'IPCA_ANBIMA'
	ipca['date'] = parsers.dateISOer(re.findall('\*Expectativa IPCA.*para[^\d]*(\d*.\d*.\d*)',content)[0])
	ipca['value'] = re.findall('\*Expectativa IPCA.*para[^\d]*\d*.\d*.\d*.*[^\d]* (\d*,\d*)%',content)[0]
	ipca['value'] = ipca['value'].replace(',','.')
	return ipca
	

def published_igpm_index(content):
	igpm = {}
	igpm['id'] = 'IGPM_ANBIMA_INDICE'
	igpm['date'] = parsers.dateISOer(re.findall('\*Expectativa IGP-M.*para[^\d]*(\d*.\d*.\d*)',content)[0])
	igpm['value'] = re.findall('tabelaTitulo.*Tarifa.*Valores de Refer.*[^I]*IGP-M.*&nbsp;(\d*,\d*)',content)[0]
	igpm['value'] = igpm['value'].replace(',','.')
	return igpm

	
def published_ipca_index(content):
	ipca = {}
	ipca['id'] = 'IPCA_ANBIMA_INDICE'
	ipca['date'] = parsers.dateISOer(re.findall('\*Expectativa IPCA.*para[^\d]*(\d*.\d*.\d*)',content)[0])
	ipca['value'] = re.findall('tabelaTitulo.*Tarifa.*Valores de Refer.*[^I]*IGP-M.*\d*,\d*.*[^I]*IPCA.*&nbsp;(\d*.\d*,\d*)',content)[0]
	ipca['value'] = ipca['value'].replace('.','').replace(',','.')
	return ipca


def published_igpm_pro_rata(content):
	igpm = {}
	igpm['id'] = 'IGPM_PRO_RATA'
	igpm['date'] = parsers.dateISOer(re.findall('IGP-M.* pro rata em.* (\d*/\d*/\d)*.*= \d*,\d*',content)[0])
	igpm['value'] = re.findall('IGP-M.* pro rata em.* \d*/\d*/\d*.*= (\d*,\d*)',content)[0]
	igpm['value'] = igpm['value'].replace(',','.')
	return igpm

	
def published_ipca_pro_rata(content):
	ipca = {}
	ipca['id'] = 'IPCA_PRO_RATA'
	ipca['date'] = parsers.dateISOer(re.findall('IPCA.* pro rata em.* (\d*/\d*/\d)*.*= \d*.\d*,\d*',content)[0])
	ipca['value'] = re.findall('IPCA.* pro rata em.* \d*/\d*/\d*.*= (\d*.\d*,\d*)',content)[0]
	ipca['value'] = ipca['value'].replace('.','').replace(',','.')
	return ipca


def published_selic(content):
	selic = {}
	selic['id'] = 'SELIC'
	selic['value'] = re.findall('SELIC: (\d*.\d*)% ao ano',content)[0]
	selic['value'] = selic['value'].replace(',','.')
	selic['date'] = parsers.dateISOer(re.findall('SELIC: \d*.\d*% ao ano \*[^\*]*\*Em (\d*.\d*.\d*)',content)[0])
	return selic

def published_cdi_cetip(content):
	cdi_cetip = {}
	cdi_cetip['id'] = 'CDICETIP'
	cdi_cetip['value'] = re.findall('Taxa Referencial de DI / Cetip[^(DI)]*.*: (\d*.\d*)%[^(Em)]*Em \d*.\d*.\d*',content)[0]
	cdi_cetip['value'] = cdi_cetip['value'].replace(',','.')
	cdi_cetip['date'] = parsers.dateISOer(re.findall('Taxa Referencial de DI / Cetip[^(DI)]*.*: \d*.\d*%[^(Em)]*Em (\d*.\d*.\d*)',content)[0])
	return cdi_cetip

def published_euro_bce(content):
	euro_bce = {}
	euro_bce['id'] = 'EURO_BCE'
	euro_bce['value'] = re.findall('Taxa de .* US\$.*[^*]*>Em \d*.\d*.\d* = (\d*.\d*).*[^*]*\*.* Banco Central Europeu',content)[0]
	euro_bce['value'] = euro_bce['value'].replace(',','.')
	euro_bce['date'] = parsers.dateISOer(re.findall('Taxa de .* US\$.*[^*]*>Em (\d*.\d*.\d*) = \d*.\d*.*[^*]*\*.* Banco Central Europeu',content)[0])
	return euro_bce

def published_irfm_anbima(content):
	# Deve receber o nome e caminho do arquivo IndicEconoAgropec-BoletimBMF_20131018.txt ao invés do site de indicadores da BM&F Bovespa
	irfm_anbima = {}
	irfm_anbima['id'] = 'IRFM_ANBIMA' 
	with open(content) as f:
		for line in f:
			if 'IRF' in line:
				temp = line.split(',')
				irfm_anbima['date'] = temp[3]
				irfm_anbima['value'] = temp[6]
	
	return irfm_anbima

def published_tr_tbf(content):
	# Deve receber o nome e caminho do arquivo IndicEconoAgropec-BoletimBMF_20131018.txt ao invés do site de indicadores da BM&F Bovespa
	table = [['Date','End date','TR','TBF']]
	tr = ''
	tbf = ''
	with open(content) as f:
		for line in f:
			temp = line.split(',')
			date_tr_tbf = datetime.strptime(temp[3],'%Y-%m-%d').date()
			# Arquivo está em ordem lexicográfica
			if 'TBF' + str(date_tr_tbf.day) in line:
				tbf = temp[6]
			if 'TR ' + str(date_tr_tbf.day) in line:
				tr = temp[6]
		if tr != '' and tbf != '':
			for i in range(len(tr_tbf_maturity(date_tr_tbf.isoformat()))):
				table.append([date_tr_tbf.isoformat(),tr_tbf_maturity(date_tr_tbf.isoformat())[i], tr, tbf])
	
	tr_tbf = {}
	tr_tbf['id'] = 'TR_TBF'
	tr_tbf['tr_tbf'] = table

	return tr_tbf
	
def published_econ_agri_indic(content):
	# Retorna a tabela de indicadores extraída do arquivo txt do site da bovespa
	cont_list = content.split('\n')
	cont_list.pop(len(cont_list)-1)
	parseStr = lambda x: x.isalpha() and x or x.isdigit() and \
		int(x) or x.isalnum() and x or \
		len(set(string.punctuation).intersection(x)) == 1 and \
		x.count('.') == 1 and float(x) or x
	 
	table = [i for i in cont_list]
	for i in range(0,len(cont_list)):
		table[i] = [
			cont_list[i][0:6],
			cont_list[i][6:9],
			cont_list[i][9:11],
			parsers.dateISOer(cont_list[i][11:19]),
			cont_list[i][19:21],
			cont_list[i][21:46].strip(),
			str(DefaultContext.divide(Decimal(parseStr(cont_list[i][47:71])),DefaultContext.power(Decimal('10'),Decimal(parseStr(cont_list[i][71:73]))))),
			cont_list[i][71:73]
		]
	#'''
	last_biz_day = bd.Calendar('ANBIMA').offset(date.today().isoformat(),-1)
	f = open('IndicRelatorio' + last_biz_day + '.txt','w+')
	for m,i in enumerate(table):
		for k,j in enumerate(table[m]):
			f.write(table[m][k]+',')
		f.write('\n')
	f.close()
	#'''
	return dict(id='BOLETIM_ECON_AGRO',
		date = parsers.dateISOer(cont_list[1][11:19]),
		indic = table
		)

def published_options(content):

	cont_list = content.split('\n')
	cont_list.pop(len(cont_list)-1) # retira a linha vazia criada no split()
	
	# O Cabeçalho e o Rodapé possuem formatos diferentes
	header = []
	header = [
	cont_list[0][:2],
	cont_list[0][2:15],
	cont_list[0][15:23],
	cont_list[0][23:31]
	]
	
	footer = []
	footer = [
	cont_list[len(cont_list)-1][:2],
	cont_list[len(cont_list)-1][2:15],
	cont_list[len(cont_list)-1][15:23],
	cont_list[len(cont_list)-1][23:31],
	cont_list[len(cont_list)-1][31:42]
	]
	
	# Cria a lista com a mesma qtd de elementos da lista final
	table = [i for i in cont_list]
	
	# Cria lista com as linhas cortadas no campo correto segundo o arq de layout da bm&f bovespa
	for i in range(0,len(cont_list)):
		if i == 0:
			table[i] = header
		else:
			if i == len(cont_list)-1:
				table[i] = footer
			else:
				table[i] = [
				cont_list[i][0:2],
				cont_list[i][2:10],
				cont_list[i][10:12],
				cont_list[i][12:24],
				cont_list[i][24:27],
				cont_list[i][27:39],
				cont_list[i][39:49],
				cont_list[i][49:52],
				cont_list[i][52:56],
				cont_list[i][56:69],
				cont_list[i][69:82],
				cont_list[i][82:95],
				cont_list[i][95:108],
				cont_list[i][108:121],
				cont_list[i][121:134],
				cont_list[i][134:147],
				cont_list[i][147:152],
				cont_list[i][152:170],
				cont_list[i][170:188],
				cont_list[i][188:201],
				cont_list[i][201:202],
				cont_list[i][202:210],
				cont_list[i][210:217],
				cont_list[i][217:230],
				cont_list[i][230:242],
				cont_list[i][242:245]
				]
	# Extrai apenas os códigos de opções de compra e venda, exceto do header e do footer.			
	options = [i for j,i in enumerate(table) if j not in [0,len(table)-1] and (table[j][4] == '070' or table[j][4] == '080')]
	
	return dict(id='BOLETIM_OPCOES',
		date = parsers.dateISOer(header[3]),
		opt = options
		)

