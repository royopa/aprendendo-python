# coding:utf-8

"""
Esse módulo contém funções que recebem o conteúdo das páginas dos indicadores e
extraem as informações de indicadores e datas de referência (ou de validade 
quando for aplicável) e devolvem um dicionário contendo todas essas informações.
"""

__version__ = '0.1'
__date__    = '2013-12-31'
__author__  = 'Liz Alexandrita de Souza Barreto'

#--- LICENSE -------------------------------------------------------------------
# 
#--- CHANGES -------------------------------------------------------------------
# 
#--- TO DO ---------------------------------------------------------------------
#	* Dividir esse módulo em duas classes: uma para as funções auxiliares que 
#	  lidam com as datas e urls e outra só com os parsers
#	* Fazer testes (test_parsers.py) das funções de igpm e ipca (número índice e
#	  variações divulgadas)
#	* 
#	* 
#-------------------------------------------------------------------------------


import locale
from datetime import datetime
import re
from BeautifulSoup import *
import collections as clt

def dateISOer(content):
	# Minha obra-prima da gambiarra de locales
	dflt_fmt = {8:'%Y%m%d', 10:'%d/%m/%Y',11:'%d/%b/%Y','more':'%d de %B de %Y'} # define os formatos a serem lidos pelo tamanho da string recebida

	aux = len(content)
	aux = [aux if aux<=12 else 'more'][0]
	fmt=dflt_fmt[aux]

	try:
		locale.setlocale(locale.LC_TIME,'ptb') # tenta todos os formatos em português brasileiro antes
		date=datetime.strptime(content,fmt)	
	except:
		locale.setlocale(locale.LC_TIME,'english') # tenta os formatos em inglês
		try:
			date=datetime.strptime(content,'%A %b %d, %Y') 
		except:
			date=datetime.strptime(content,'%m/%d/%y') # possui 8 caracteres também

	isodate = date.date().isoformat()

	locale.setlocale(locale.LC_TIME,'') # reseta o formato local de data

	return isodate

def isYYYYMMDD(content):
	try:
		locale.setlocale(locale.LC_TIME,'ptb')
		datetime.strptime(content, '%Y%m%d')
		return True
	except:
		return False

def isDDMMYYYY(content):
	try:
		locale.setlocale(locale.LC_TIME,'ptb')
		datetime.strptime(content, '%d/%m/%Y')
		return True
	except:
		return False

def euro_bce(content):
	'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
	Euro_USD = re.findall("<Cube currency=.USD. rate=.(\d.\d\d\d\d).", content)[0]
	date_ref = re.findall("<Cube time=.(\d\d\d\d.\d\d.\d\d).>", content)[0]
	return dict(id='EURO_BCE', date=date_ref, value=Euro_USD)
	
def ipca(content):
	'http://www.anbima.com.br/indicadores/indicadores.asp'
	strlist=[]
	tdcont = BeautifulSoup(content).table.findAll('td')
	for td in tdcont:
		for contd in td.contents:
			try:
				if 'IPCA' in contd.findPrevious('a'):
					strlist.append(contd.string)
			except:
				pass
			
	ipca_anbima = str(strlist[1]).replace(',','.')
	date_ref = re.findall('Data e Hora da .ltima Atualiza..o: (\d*/\d*/\d*)',content)[0]
	date_ref = dateISOer(date_ref)
	
	
	return dict(id='IPCA_ANBIMA', date = date_ref,
		value = ipca_anbima
		)

def igpm(content):
	'http://www.anbima.com.br/indicadores/indicadores.asp'
	strlist=[]
	tdcont = BeautifulSoup(content).table.findAll('td')
	for td in tdcont:
		for contd in td.contents:
			try:
				if 'IGP-M' in contd.findPrevious('a'):
					strlist.append(contd.string)
			except:
				pass
		
	igpm_anbima = str(strlist[1]).replace(',','.')
	date_ref = re.findall('Data e Hora da .ltima Atualiza..o: (\d*/\d*/\d*)',content)[0]
	date_ref = dateISOer(date_ref)
	
	return dict(id='IGPM_ANBIMA', date = date_ref,
		value = igpm_anbima
		)
	
def ipca_index(content):
	'http://www.anbima.com.br/indicadores/indicadores.asp'
	strlist=[]
	tdcont = BeautifulSoup(content).table.findAll('td')
	for td in tdcont:
		for contd in td.contents:
			try:
				if 'IPCA (' in contd:
					strlist.append(contd.findNext(text='Número Índice'.decode('utf-8')).findNext().string)
			except:
				pass
	
	ipca_anbima = str(strlist[0]).replace('.','').replace(',','.')
	date_ref = re.findall('Data e Hora da .ltima Atualiza..o: (\d*/\d*/\d*)',content)[0]
	date_ref = dateISOer(date_ref)
	
	return dict(id='IPCA_ANBIMA_INDICE', date = date_ref,
		value = ipca_anbima
		)


def igpm_index(content):
	'http://www.anbima.com.br/indicadores/indicadores.asp'
	strlist=[]
	tdcont = BeautifulSoup(content).table.findAll('td')
	for td in tdcont:
		for contd in td.contents:
			try:
				if 'IGP-M (' in contd:
					strlist.append(contd.findNext(text='Número Índice'.decode('utf-8')).findNext().string)
			except:
				pass
	
	igpm_anbima = str(strlist[0]).replace(',','.')
	date_ref = re.findall('Data e Hora da .ltima Atualiza..o: (\d*/\d*/\d*)',content)[0]
	date_ref = dateISOer(date_ref)
	
	return dict(id='IGPM_ANBIMA_INDICE', date = date_ref,
		value = igpm_anbima
		)



def ipca_var(content):
	'http://www.anbima.com.br/indicadores/indicadores.asp'
	strlist=[]
	tdcont = BeautifulSoup(content).table.findAll('td')
	for td in tdcont:
		for contd in td.contents:
			try:
				if 'IPCA (' in contd:
					strlist.append(contd.findNext(text='Var % no mês'.decode('utf-8')).findNext().string)
			except:
				pass
	
	ipca_anbima = str(strlist[0]).replace('.','').replace(',','.')
	date_ref = re.findall('Data e Hora da .ltima Atualiza..o: (\d*/\d*/\d*)',content)[0]
	date_ref = dateISOer(date_ref)
	
	return dict(id='IPCA_VARIACAO', date = date_ref,
		value = ipca_anbima
		)


def igpm_var(content):
	'http://www.anbima.com.br/indicadores/indicadores.asp'
	strlist=[]
	tdcont = BeautifulSoup(content).table.findAll('td')
	for td in tdcont:
		for contd in td.contents:
			try:
				if 'IGP-M (' in contd:
					strlist.append(contd.findNext(text='Var % no mês'.decode('utf-8')).findNext().string)
			except:
				pass
	
	igpm_anbima = str(strlist[0]).replace(',','.')
	date_ref = re.findall('Data e Hora da .ltima Atualiza..o: (\d*/\d*/\d*)',content)[0]
	date_ref = dateISOer(date_ref)
	
	return dict(id='IGPM_VARIACAO', date = date_ref,
		value = igpm_anbima
		)

def ipca_anbima_previas(content):
	'http://portal.anbima.com.br/informacoes-tecnicas/precos/indices-de-precos/Pages/ipca.aspx'
	tdcont = BeautifulSoup(content).findAll('td')
	genlist = []
	for td in tdcont:
		try:
			genlist.append(re.findall('(\d,\d\d)',str(td))[0].replace(',','.'))
		except:
			try:
				genlist.append(re.findall('(\d\d.\d\d.\d\d\d\d)',str(td))[0])
			except:
				genlist.append('')
	
	calcdate1 = str(dateISOer(genlist[3]))
	calcdate2 = str(dateISOer(genlist[6]))
	value1 = str(genlist[4])
	value2 = str(genlist[7])
	valdate1 = str(dateISOer(genlist[5]))
	valdate2 = str(dateISOer(genlist[8]))
		
	return dict(id='IPCA_ANBIMA_PREVIA',
		calcdate1=calcdate1,
		calcdate2=calcdate2,
		value1=value1,
		value2=value2,
		valdate1=valdate1,
		valdate2=valdate2
		)

def igpm_anbima_previas(content):
	'http://portal.anbima.com.br/informacoes-tecnicas/precos/indices-de-precos/Pages/igp-m.aspx'
	tdcont = BeautifulSoup(content).table.findAll('td')
	genlist = []
	for td in tdcont:
		try:
			genlist.append(re.findall('(\d,\d\d)',str(td))[0].replace(',','.'))
		except:
			try:
				genlist.append(re.findall('(\d\d.\d\d.\d\d\d\d)',str(td))[0])
			except:
				genlist.append('')

	calcdate1=dateISOer(genlist[3])
	calcdate2=dateISOer(genlist[6])
	calcdate3=dateISOer(genlist[9])
	value1=genlist[4]
	value2=genlist[7]
	value3=genlist[10]
	valdate1=dateISOer(genlist[5])
	valdate2=dateISOer(genlist[8])
	valdate3=dateISOer(genlist[11])
	
	return dict(id='IGPM_ANBIMA_PREVIA',
		calcdate1=calcdate1,
		calcdate2=calcdate2,
		calcdate3=calcdate3,
		value1=value1,
		value2=value2,
		value3=value3,
		valdate1=valdate1,
		valdate2=valdate2,
		valdate3=valdate3
		)

def irfm_anbima(content):
	'http://www.anbima.com.br/ima/arqs/ima_completo.xml'
	IRF_total = re.findall("<TOTAL  T_Indice='TOTAL' T_Num_Indice='(\d.\d\d\d.\d\d\d\d\d\d)'",content)[0]
	date_ref = re.findall("<TOTAIS DT_REF=.(\d\d.\d\d.\d\d\d\d)",content)[0]
	IRF_total = IRF_total.replace('.','')
	IRF_total = IRF_total.replace(',','.')
	
	return dict(id='IRFM_ANBIMA',
		date = dateISOer(date_ref),
		value = IRF_total
		)

def ntnbcf_ltn_lft_anbima(content):
	
	content = content.split('\n')
	lft = [cont for cont in content if 'LFT' in cont]
	flds = lft[0].count('@') + 1
	
	lft_list = [cont.replace(',','.').replace('@',',').split(',') for cont in content if 'LFT' in cont]
	ltn_list = [cont.replace(',','.').replace('@',',').split(',') for cont in content if 'LTN' in cont]
	ntnb_list = [cont.replace(',','.').replace('@',',').split(',') for cont in content if 'NTN-B' in cont]
	ntnc_list = [cont.replace(',','.').replace('@',',').split(',') for cont in content if 'NTN-C' in cont]
	ntnf_list = [cont.replace(',','.').replace('@',',').split(',') for cont in content if 'NTN-F' in cont]
	
	
	
	lft = [['Titulo','Data Referencia','Codigo SELIC','Data Base/Emissao','Data Vencimento','Tx. Maxima','Tx. Minima','Tx. Indicativas','PU','Desvio padrao','Interv. Ind. Inf. (D0)','Interv. Ind. Sup. (D0)','Interv. Ind. Inf. (D+1)','Interv. Ind. Sup. (D+1)','Criterio']]
	ltn = [['Titulo','Data Referencia','Codigo SELIC','Data Base/Emissao','Data Vencimento','Tx. Maxima','Tx. Minima','Tx. Indicativas','PU','Desvio padrao','Interv. Ind. Inf. (D0)','Interv. Ind. Sup. (D0)','Interv. Ind. Inf. (D+1)','Interv. Ind. Sup. (D+1)','Criterio']]
	ntnb = [['Titulo','Data Referencia','Codigo SELIC','Data Base/Emissao','Data Vencimento','Tx. Maxima','Tx. Minima','Tx. Indicativas','PU','Desvio padrao','Interv. Ind. Inf. (D0)','Interv. Ind. Sup. (D0)','Interv. Ind. Inf. (D+1)','Interv. Ind. Sup. (D+1)','Criterio']]
	ntnc = [['Titulo','Data Referencia','Codigo SELIC','Data Base/Emissao','Data Vencimento','Tx. Maxima','Tx. Minima','Tx. Indicativas','PU','Desvio padrao','Interv. Ind. Inf. (D0)','Interv. Ind. Sup. (D0)','Interv. Ind. Inf. (D+1)','Interv. Ind. Sup. (D+1)','Criterio']]
	ntnf = [['Titulo','Data Referencia','Codigo SELIC','Data Base/Emissao','Data Vencimento','Tx. Maxima','Tx. Minima','Tx. Indicativas','PU','Desvio padrao','Interv. Ind. Inf. (D0)','Interv. Ind. Sup. (D0)','Interv. Ind. Inf. (D+1)','Interv. Ind. Sup. (D+1)','Criterio']]

	for i in range(0,len(lft_list),flds):
		for j in range(len(lft_list)):
			lft.append(lft_list[i:i+flds][j])
	for i in range(1,len(lft)):
		lft[i][1]=dateISOer(lft[i][1])
		lft[i][3]=dateISOer(lft[i][3])
		lft[i][4]=dateISOer(lft[i][4])

	for i in range(0,len(ltn_list),flds):
		for j in range(len(ltn_list)):
			ltn.append(ltn_list[i:i+flds][j])
	for i in range(1,len(ltn)):
		ltn[i][1]=dateISOer(ltn[i][1])
		ltn[i][3]=dateISOer(ltn[i][3])
		ltn[i][4]=dateISOer(ltn[i][4])

	for i in range(0,len(ntnb_list),flds):
		for j in range(len(ntnb_list)):
			ntnb.append(ntnb_list[i:i+flds][j])
	for i in range(1,len(ntnb)):
		ntnb[i][1]=dateISOer(ntnb[i][1])
		ntnb[i][3]=dateISOer(ntnb[i][3])
		ntnb[i][4]=dateISOer(ntnb[i][4])

	for i in range(0,len(ntnc_list),flds):
		for j in range(len(ntnc_list)):
			ntnc.append(ntnc_list[i:i+flds][j])
	for i in range(1,len(ntnc)):
		ntnc[i][1]=dateISOer(ntnc[i][1])
		ntnc[i][3]=dateISOer(ntnc[i][3])
		ntnc[i][4]=dateISOer(ntnc[i][4])

	for i in range(0,len(ntnf_list),flds):
		for j in range(len(ntnf_list)):
			ntnf.append(ntnf_list[i:i+flds][j])
	for i in range(1,len(ntnf)):
		ntnf[i][1]=dateISOer(ntnf[i][1])
		ntnf[i][3]=dateISOer(ntnf[i][3])
		ntnf[i][4]=dateISOer(ntnf[i][4])

	return dict(id='NTNBCF_LTN_LFT_ANBIMA',
		LFT = lft,
		LTN = ltn,
		NTNB = ntnb,
		NTNC = ntnc,
		NTNF = ntnf
		)

def igpm_ntnc(content):
	
	try:
		igpm = re.findall('M.dia apurada pelo Comit. de Acompanhamento Macroecon.mico da ANBIMA:  (.*)%', content)[0]
	except:
		try:
			igpm = re.findall('IGP-M final para .* : (.*)%', content)[0]
		except:
			igpm = re.findall('Proje..o IGP-M para .* : (\d*.\d*)%', content)[0]
	igpm = igpm.replace(',','.')
	refdate = re.findall('T.tulos P.blicos Federais.*\n.*<B>(.*)</B>',content)[0]
	
	return dict(id='IGPM_NTNC',
		date = dateISOer(refdate),
		value = igpm
		)


def ipca_ntnb(content):
	try:
		ipca = re.findall('IPCA final para .* :  (\d*,\d*)%',content)[0]
	except:
		try:
			ipca = re.findall('Proje..o IPCA para .*(\d*,\d*)%',content)[0]
		except:
			ipca = re.findall('M.dia apurada pel. Comit. de Acompanhamento Macroecon.mico da ANBIMA:\s*(\d*,\d*)%',content)[0]

	ipca = ipca.replace(',','.')
	refdate = re.findall('T.tulos P.blicos Federais.*\n.*<B>(.*)</B>',content)[0]

	
	return dict(id='IPCA_NTNB',
		date = dateISOer(refdate),
		value = ipca
		)


def selic(content):
	'https://www.selic.rtm/extranet/consulta/taxaSelic.do?method=listarTaxaDiaria'
	info = re.findall(">\d.*<",content)
	info = [i.strip("><") for i in info] # <Lista de Valores>
	refdate = info[0]
	refselic = info[1].replace(',','.')
	
	return dict(id='SELIC',
		date = dateISOer(refdate),
		value = refselic
		)

def est_selic(content):
	'http://www.anbima.com.br/indicadores/indicadores.asp'
	info = re.findall("Estimativa SELIC<sub>1</a></sub></td>...<td  height='35' valign='center'>(\d\d.\d\d.\d\d\d\d)</td>...<td  height='35' valign='center'>(\d.\d\d)</td>",content)[0]
	estdate = info[0]
	estselic = info[1].replace(',','.')
	return dict(id='ESTSELIC',
		date = dateISOer(estdate),
		value = estselic
		)


def cdi_cetip(content):
	'http://www.cetip.com.br/'
	info = re.findall('TaxDateDI.>Em (\d*.\d*.\d*).*[^\d]*(\d*.\d*)%',content)[0]
	cdidate = info[0]
	cditx = info[1].replace(',','.')
	
	return dict(id='CDICETIP',
		date = dateISOer(cdidate),
		value = cditx
		)

def etfs(content):
	'http://www.bmfbovespa.com.br/etf/fundo-de-indice.aspx?Idioma=pt-br'
	info = re.findall("DataPregao.*>(\d.*\d.*)</span>",content)[0]
	refdate = info
	
	tdcont = BeautifulSoup(content).table.findAll('td')
	etf_list = [contd.string.strip() for td in tdcont for contd in td.contents]
	etf_list = [j for i,j in enumerate(etf_list) if i not in sorted(range(10,(len(etf_list)+1),8)+range(12,(len(etf_list)+1),8))]
	etf_list = [i.encode('utf8').replace(',','.') for i in etf_list]
	aux = etf_list[5:]
	etf_vref = [['Código']+etf_list[:5]]
	for i in range(0,len(aux),6):
		etf_vref.append(aux[i:i+6])

	return dict(id='ETF',
		date = dateISOer(refdate),
		etf_iopv = etf_vref
		)

def cmt_tresury(content):
	'http://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield'
	thcont = BeautifulSoup(content).findAll('table',{'class':'t-chart'})[0].findAll('th')
	tdcont = BeautifulSoup(content).findAll('table',{'class':'t-chart'})[0].findAll('td',{'class':'text_view_data'})
	refdate = BeautifulSoup(content).findAll('div',{'class':'updated'})[0]
	
	cmt_header = [th.string for th in thcont]
	cmt_list = [td.string for td in tdcont]
	refdate = refdate.string.encode('utf-8')
	
	aux = cmt_header+cmt_list
	aux = [i.encode('utf-8') for i in aux]
	
	cmt=[]
	for i in range(0,len(aux),len(cmt_header)):
		cmt.append(aux[i:i+len(cmt_header)])
	
	for i in range(1,len(cmt)):
		cmt[i][0]=dateISOer(cmt[i][0])
	
	return dict(id='CMT',
		date = dateISOer(refdate),
		value = cmt
		)


def bcb_open(content):
	'https://www3.bcb.gov.br/ptax_internet/consultaBoletim.do?method=consultarBoletim'
	tdcont = BeautifulSoup(content).findAll('table',{'class':'tabela'})[0].findAll('td')
	exchg = [td.string for td in tdcont if td.string is not None]
	exchg = [i.encode('utf-8') for i in exchg]
	
	refdate = re.findall('Data da Cota..o: (\d\d.\d\d.\d\d\d\d)',content)[0]
	
	ex_table = []
	for i in range(0,len(exchg),5):
		ex_table.append(exchg[i:i+5])
	
	usd_ask = [i[4] for j,i in enumerate(ex_table) if 'USD' in ex_table[j][0]][0].replace(',','.')
	euro_ask = [i[4] for j,i in enumerate(ex_table) if 'EUR' in ex_table[j][0]][0].replace(',','.')
	jpy_ask = [i[4] for j,i in enumerate(ex_table) if 'JPY' in ex_table[j][0]][0].replace(',','.')
	
	
	return dict(id='BCB_Open',
		date = dateISOer(refdate),
		usd = usd_ask,
		euro = euro_ask,
		jpy = jpy_ask
		)

def bcb_ptax(content):
	
	table = content.replace(',','.').replace(';',',').replace('\r','')
	table = table.split('\n')
	table.pop()
	table = [i.split(',') for i in table]
	for i in table:
		i[0] = dateISOer(i[0])

	return dict(id='BCB_Ptax',
		ptax_table = table
		)

def tr_tbf(content):

	tdcont = BeautifulSoup(content).findAll('table',{'class':'tabela'})[2].findAll('span')
	tdcont = [contd.string.strip() for td in tdcont for contd in td.contents if contd.string is not None][14:]
	tdcont = [i.encode('utf-8').replace(',','.') for i in tdcont]

	table = [['Date','End date','TR','TBF']]
	for i in range(0,len(tdcont),4):
		table.append(tdcont[i:i+4])

	for i in range(1,len(table)):
		table[i][0] = dateISOer(table[i][0])
		table[i][1] = dateISOer(table[i][1])

	return dict(id='TR_TBF',
		tr_tbf = table,
		)

def vna_lft(content):
	'http://www.anbima.com.br/vna/vna.asp'
	vna = re.findall('210100</td>[^<]*<td>(\d*.\d*.\d*)</td>',content)[0].replace('.','').replace(',','.')
	refdate = re.findall('C.digo Selic.*</td>[^>]*><b>(\d*.\d*.\d*)</b></td>',content)[0]
	return dict(id='VNA_LFT',
		date = dateISOer(refdate),
		value = vna
		)
