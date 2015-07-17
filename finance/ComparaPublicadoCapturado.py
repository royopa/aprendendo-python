# coding:utf-8

"""
Esse módulo faz o trabalho sujo de conectar nos sites e devolver o conteúdo para
 os parsers e escrever o relatório em html
"""

__version__ = '0.1'
__date__    = '2013-12-31'
__author__  = 'Liz Alexandrita de Souza Barreto' # Adicione seu nome aki =]

#--- LICENSE -------------------------------------------------------------------
# 
#--- CHANGES -------------------------------------------------------------------
# Espaço para @ senhorit@ que assumir esse projeto anotar as mudanças para
# melhor. Ou não. Só não me culpe pelos seus bad codes e melhore os meus, oras.
#--- TO DO ---------------------------------------------------------------------
#	* Dividir esse programa em módulos?(seria uma boa?), funções de criação de html?
#	* Descobrir o problema de conexão com os sites do Banco Central
#	* Criar folha de estilos css para o relatório em html
#	* Investigar como resolver o problema da página das etfs ser "instável"
#	* Criar função que verifica primeiro o log de inflação para buscar o número
#	  índice publicado no mês anterior e caso não haja log, verificar a 
#	  existência da lista isPub ou pop-upar uma tela para input manual <<Perigo! Perigo! Perigo!>>
#	* Padronizar nomenclatura de variáveis (principalmente da parte de criação de html)
#	* Investigar qual é o gargalo de tempo do código e porque varia tanto (conexões???)
#	* 
#	* 
#	* 
# ------------------------------------------------------------------------------

# Espaço para importações
import os
import connector
import validation as vd
import passwd
import ProxyLogin as pl
from datetime import date, datetime, timedelta
import operator
import HTML
import bizdays as bd
import zipfile
from StringIO import StringIO
import pro_ratas as prt

# Define datas utilizadas ao longo do programa
last_biz_day = bd.Calendar('ANBIMA').offset(date.today().isoformat(),-1)
vna_date = datetime.strftime(date.today(),'%d/%m/%Y')
vna_mth_yr = datetime.strftime(date.today(),'%m/%Y')

# Conecta no proxy para acessar as páginas externas
user = pl.proxy_login()
conn = connector.Connector(user)

# Dados Publicados no mesmo formato
url_dict = dict(selic = 'https://www.selic.rtm/extranet/consulta/taxaSelic.do?method=listarTaxaDiaria', 
	ipca = 'http://www.anbima.com.br/indicadores/indicadores.asp',
	igpm = 'http://www.anbima.com.br/indicadores/indicadores.asp',
	ipca_index = 'http://www.anbima.com.br/indicadores/indicadores.asp',
	igpm_index = 'http://www.anbima.com.br/indicadores/indicadores.asp',
	euro_bce = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml',
	cdi_cetip = 'http://www.cetip.com.br/',
	irfm_anbima = 'http://www.anbima.com.br/ima/arqs/ima_completo.xml'
	)
contents = dict([url,conn.read(url_dict[url])] for url in url_dict)
dictionary = dict([url, vd.fparser(url,contents[url])] for url in contents)


# ------------------------------------------------------------------------------
# Verifica Data de Validade das Prévias do IGPM e IPCA
# Na página de indicadores da anbima, na qual pegamos igpm e ipca (sem data), 
# o respectivo parser captura apenas a projeção e não a divulgação, portanto 
# é necessário verificar as datas das prévias e escolher qual valor utilizar
# ------------------------------------------------------------------------------

# Números Índice Divulgados
ipca_index_url = 'http://www.anbima.com.br/indicadores/indicadores.asp'
igpm_index_url = 'http://www.anbima.com.br/indicadores/indicadores.asp'

ipca_index_dict = vd.fparser('ipca_index', conn.read(ipca_index_url))
igpm_index_dict = vd.fparser('igpm_index', conn.read(igpm_index_url))
ipca_index_dict = dict(sorted(ipca_index_dict.iteritems(), key=operator.itemgetter(0)))
igpm_index_dict = dict(sorted(igpm_index_dict.iteritems(), key=operator.itemgetter(0)))

# Variações Divulgadas
ipca_var_dict = vd.fparser('ipca_var', conn.read(ipca_index_url))
igpm_var_dict = vd.fparser('igpm_var', conn.read(igpm_index_url))
ipca_var_dict = dict(sorted(ipca_var_dict.iteritems(), key=operator.itemgetter(0)))
igpm_var_dict = dict(sorted(igpm_var_dict.iteritems(), key=operator.itemgetter(0)))

# Variações das Prévias
igpm_anbima_prev_url = 'http://portal.anbima.com.br/informacoes-tecnicas/precos/indices-de-precos/Pages/igp-m.aspx'
ipca_anbima_prev_url = 'http://portal.anbima.com.br/informacoes-tecnicas/precos/indices-de-precos/Pages/ipca.aspx'
igpm_dict = vd.fparser('igpm_anbima_previas', conn.read(igpm_anbima_prev_url))
ipca_dict = vd.fparser('ipca_anbima_previas', conn.read(ipca_anbima_prev_url))

#
# Compara data de captura com as datas de validade das prévias do IPCA
#
capt_date = datetime.strptime(dictionary['ipca']['date'], "%Y-%m-%d")
if capt_date < datetime.strptime(ipca_dict['valdate1'], "%Y-%m-%d"):
	# Estamos antes da primeira prévia, e portanto usamos a divulgação
	dictionary['ipca']['value'] = ipca_var_dict['value']
	ipca_var_bmf = ipca_var_dict['value']
else:
	if capt_date < datetime.strptime(ipca_dict['valdate2'], "%Y-%m-%d"):
		# Estamos depois da primeira prévia e antes da segunda
		dictionary['ipca']['value'] = ipca_dict['value1']
		ipca_var_bmf = ipca_dict['value1']
	else:
		# Estamos na segunda prévia e antes da divulgação
		dictionary['ipca']['value'] = ipca_dict['value2']
		ipca_var_bmf = ipca_dict['value1']
			
#
# Compara data de captura com as datas de validade das prévias do IGPM
#
capt_date = datetime.strptime(dictionary['igpm']['date'], "%Y-%m-%d")
if capt_date < datetime.strptime(igpm_dict['valdate1'], "%Y-%m-%d"):
	dictionary['igpm']['value'] = igpm_var_dict['value']
else:
	if capt_date < datetime.strptime(igpm_dict['valdate2'], "%Y-%m-%d"):
		dictionary['igpm']['value'] = igpm_dict['value1']
	else:
		if capt_date < datetime.strptime(igpm_dict['valdate3'], "%Y-%m-%d"):
			dictionary['igpm']['value'] = igpm_dict['value2']
		else:
			dictionary['igpm']['value'] = igpm_dict['value3']

# ------------------------------------------------------------------------------
# Cálculo de Pro-ratas de IGP-M e IPCA
# ------------------------------------------------------------------------------

prt_cal = prt.ProRataTempore(bd.Calendar('ANBIMA'))

# CUIDADO! INFORMAÇÃO HARDCODED - ler TO DO list acima
igpm_bmf = prt_cal.index_month_day(['2013-11-01','2013-12-01'],date.today().isoformat(), \
	igpm_var_dict['value'], igpm_index_dict['value'], [True,'533.621'])
igpm_pub = prt_cal.index_month_day(['2013-10-31','2013-11-28'],date.today().isoformat(), \
	igpm_var_dict['value'], igpm_index_dict['value'], [True,'533.621'])
ipca_bmf = prt_cal.index_month_day(['2013-11-15','2013-12-15'], date.today().isoformat(), \
	ipca_var_bmf, ipca_index_dict['value'], [False,''])
ipca_ativos = prt_cal.index_month_day(['2013-11-15','2013-12-15'], date.today().isoformat(), \
	dictionary['ipca']['value'], ipca_index_dict['value'], [False,''])


# ------------------------------------------------------------------------------
# Dados não publicados de Títulos Públicos
# ------------------------------------------------------------------------------

# Cria a url com data do site da anbima - porque tem uma parte dele com data
unpub_tresury = vd.merc_sec_sites(last_biz_day, 'ntnbcf_ltn_lft_anbima')
unpub_tresury_dict = vd.fparser('ntnbcf_ltn_lft_anbima',conn.read(unpub_tresury))
unpub_tresury_dict = dict([i, unpub_tresury_dict[i]] for i in unpub_tresury_dict if i not in 'id')
unpub_tresury_dict = dict(sorted(unpub_tresury_dict.iteritems(), key=operator.itemgetter(0)))


# ------------------------------------------------------------------------------
# Dados Não Publicados CMT
# ------------------------------------------------------------------------------
cmt_url = 'http://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield'
cmt_dict = vd.fparser('cmt_tresury',conn.read(cmt_url))

# ------------------------------------------------------------------------------
# Dados Não Publicados PTAX Bacen
# ------------------------------------------------------------------------------
# Querido site do Banco Central, consegui exatamente UM indicador seu...

bcb_ptax_url = vd.ptax_url(date.today().isoformat())
param_bcb_ptax_dict = vd.fparser('bcb_ptax',conn.read(bcb_ptax_url))

# ------------------------------------------------------------------------------
# Dados Não Publicados VNA_LFT
# ------------------------------------------------------------------------------

vna_url = 'http://www.anbima.com.br/vna/vna.asp'
vna_temp_dict = {
	'filtro':'filtro', \
	'codigo':'210100', 'sigla':'', \
	'tpRendimento':'org.jboss.seam.ui.NoSelectionConverter.noSelectionValue', \
	'indiceCorrecao':'org.jboss.seam.ui.NoSelectionConverter.noSelectionValue', \
	'pagamento':'org.jboss.seam.ui.NoSelectionConverter.noSelectionValue', \
	'dataPagInputDate':'', \
	'dataPagInputCurrentDate':vna_mth_yr, \
	'dataVencIniInputDate':vna_date, \
	'dataVencIniInputCurrentDate':vna_mth_yr, \
	'dataVencFimInputCurrentDate':vna_mth_yr, \
	'btnConsultar':'Consultar',
	'javax.faces.ViewState':'j_id4'
}

req_instance = conn.parametric_connection(vna_url, **vna_temp_dict)
vna_lft_dict = vd.fparser('vna_lft', conn.read(req_instance))

# ------------------------------------------------------------------------------
# Dados não publicados no mesmo formato
# ------------------------------------------------------------------------------

unpub_url_dict = dict(igpm_ntnc = vd.merc_sec_sites(last_biz_day, 'igpm_ntnc'),
	ipca_ntnb = vd.merc_sec_sites(last_biz_day, 'ipca_ntnb'),
	est_selic = 'http://www.anbima.com.br/indicadores/indicadores.asp',
	)
unpub_cont = dict([url,conn.read(unpub_url_dict[url])] for url in unpub_url_dict)
unpub_dict = dict([url, vd.fparser(url,unpub_cont[url])] for url in unpub_cont)
unpub_dict = [[i,unpub_dict[i]] for i in unpub_dict]
unpub_dict.append(['vna_lft',vna_lft_dict])
unpub_dict = dict(unpub_dict)
unpub_dict = dict(sorted(unpub_dict.iteritems(), key=operator.itemgetter(0)))

'''
# ------------------------------------------------------------------------------
# Dados não publicados TR_TBF  -  NÃO FUNCIONA
# ------------------------------------------------------------------------------

tr_tbf_url = 'https://www3.bcb.gov.br/sgspub/consultarvalores/consultarValoresSeries.do?method=consultarValores'

tr_tbf_req_dict = {
	'optSelecionaSerie':'226',
	'optSelecionaSerie':'253',
	'dataInicio':'341',
	'dataFim':'',
	'selTipoArqDownload':'1',
	'chkPaginar':'on',
	'hdOidSeriesSelecionadas':'226;253',
	'hdPaginar':'true',
	'bilServico':'[SGSFW2301]'
	
}

req_instance = conn.parametric_connection(tr_tbf_url, **tr_tbf_req_dict)
tr_tbf_dict = vd.fparser('tr_tbf',conn.read(req_instance))
#print tr_tbf_dict
'''

'''
# ------------------------------------------------------------------------------
#  Dados Não Publicados Dólar Intradiário Bacen - NÃO FUNCIONA TAMBÉM
# ------------------------------------------------------------------------------

dataini = datetime.strptime(date.today().isoformat(),"%Y-%m-%d")
dataini = dataini.strftime('%d/%m/%Y')

bcb_open_url = 'https://www3.bcb.gov.br/ptax_internet/consultaBoletim.do?method=consultarBoletim'
req_dict ={
	'RadOpcao':'3',
	'DATAINI':dataini,
	'DATAFIM':'----------------------',
	'ChkMoeda':'61'
}

req_instance = conn.parametric_connection(bcb_open_url, **req_dict)
content_bcb_open = conn.read(req_instance)
print content_bcb_open
param_bcb_opem_dict = vd.fparser('bcb_open',content_bcb_open)
'''

# ------------------------------------------------------------------------------
# Extração os dados financeiros publicados no site da bovespa para validação 
# com as capturas automáticas dos parsers. Não necessita  de (na real não pode ter)
# conexão com proxy. A partir deste ponto não se pode adicionar trechos de código 
# que conectam a páginas externas.
# ------------------------------------------------------------------------------
user = {}
user['username'] = ''
user['password'] = ''

conn = connector.Connector(user)

#'''
# ------------------------------------------------------------------------------
# Dados Não Publicados ETF
# ------------------------------------------------------------------------------

# A página das ETFs é bem ´sensível´, eventualmente ela não carrega, ou demora 
# muito para carregar. Isso é devido muito possivelmente à variável 
# __VIEWSTATE ser dinâmica, ou seja, mudar diariamente, ou o arquivo não ser 
# carregado por TI no site, ou não ter chegado na BM&F... mimimimi
# Às vezes carregar manualmente a página no browser antes de rodar o código, funciona.
req_dict = {
	'__EVENTTARGET':'ctl00$contentPlaceHolderConteudo$etf$tabETF',
	'__EVENTARGUMENT':'ctl00$contentPlaceHolderConteudo$etf$tabETF$tabValorReferencia',
	'__VIEWSTATE':'/wEPDwUJOTQyNDYyODI3D2QWAmYPDxYIHgRub2RlBSQ4ZjExNTk1Ni03YjM2LTRhMTktYjFkNy05OTY1MjQ2ZmVlZTMeClBhcmVudE5vZGUFLC9wdC1ici9pbnRyb3MvaW50cm8tZnVuZG9zLmFzcHg/SWRpb21hPXB0LWJyHgtDdXJyZW50Tm9kZQUmL2V0Zi9mdW5kby1kZS1pbmRpY2UuYXNweD9JZGlvbWE9cHQtYnIeCkN1cnJlbnRVcmwFJi9ldGYvZnVuZG8tZGUtaW5kaWNlLmFzcHg/SWRpb21hPXB0LWJyZBYCAgMPZBYCAgEPZBYKAgEPZBYIAgMPFgIeB1Zpc2libGVoZAIMDxYGHgdvbmNsaWNrBRB0aGlzLnZhbHVlID0gJyc7HgZvbmJsdXIFMWlmKHRoaXMudmFsdWUgPT0gJycpIHt0aGlzLnZhbHVlPSBub21lVGV4dEJ1c2NhO30eCm9ua2V5cHJlc3MFJHJldHVybiBrZXlQcmVzc1Blc3F1aXNhKHRoaXMsZXZlbnQpO2QCDQ8PFgIeDU9uQ2xpZW50Q2xpY2sFHHJldHVybiBWZXJpZmljYXJDYW1wb0J1c2NhKClkZAIODxYCHgRUZXh0BaAxPGRpdiBpZD0nbWVudSc+PHVsIGlkPSdtZW51SG9yaXonPjxsaSBpZD0nYWJtZmJvdmVzcGEnPjxhIGhyZWY9JyMnIGNsYXNzPSdhYm1mYm92ZXNwYScgaWQ9J2xpbmtBYm1mJz48aW1nIHNyYz0nL3NoYXJlZC9jc3MvaW1nL3RyYW5zcC5naWYnIC8+PC9hPjx1bCBvbm1vdXNlb3Zlcj0ibGlua0FibWYuY2xhc3NOYW1lPSdhYm1mYm92ZXNwYWhvdmVyJzsiIG9ubW91c2VvdXQ9ImxpbmtBYm1mLmNsYXNzTmFtZT0nYWJtZmJvdmVzcGEnOyI+PGxpPjxhIGhyZWY9Jy9wdC1ici9pbnRyb3MvaW50cm8tc29icmUtYS1ib2xzYS5hc3B4JyB0YXJnZXQ9Jyc+TyBxdWUgYSBCb2xzYSBmYXo8L2E+PC9saT48bGk+PGEgaHJlZj0nL3B0LWJyL2EtYm1mYm92ZXNwYS92aXNpdGFzLWEtYm9sc2EvdmlzaXRhcy1hLWJvbHNhLmFzcHgnIHRhcmdldD0nJz5WaXNpdGUgYSBCb2xzYTwvYT48L2xpPjxsaT48YSBocmVmPScvcHQtYnIvYS1ibWZib3Zlc3BhL3VuaWRhZGVzL3VuaWRhZGVzLmFzcHgnIHRhcmdldD0nJz5Ob3NzYXMgdW5pZGFkZXM8L2E+PC9saT48bGk+PGEgaHJlZj0nL3B0LWJyL2EtYm1mYm92ZXNwYS9wYXJjZXJpYS1lc3RyYXRlZ2ljYS1jbWVncm91cC9wYXJjZXJpYS1lc3RyYXRlZ2ljYS5hc3B4JyB0YXJnZXQ9Jyc+UGFyY2VyaWFzIEVzdHJhdMOpZ2ljYXM8L2E+PC9saT48bGk+PGEgaHJlZj0nL3B0LWJyL2EtYm1mYm92ZXNwYS90cmFiYWxoZS1jb25vc2NvL3RyYWJhbGhlLWNvbm9zY28uYXNweCcgdGFyZ2V0PScnPlRyYWJhbGhlIG5hIEJvbHNhPC9hPjwvbGk+PGxpPjxhIGhyZWY9Jy9zYWxhLWRlLWltcHJlbnNhL3NhbGFpbXByZW5zYS5hc3B4P2lkaW9tYT1wdC1icicgdGFyZ2V0PScnPlNhbGEgZGUgSW1wcmVuc2E8L2E+PC9saT48bGk+PGEgaHJlZj0nL3B0LWJyL2EtYm1mYm92ZXNwYS9wdWJsaWNhY29lcy5hc3B4JyB0YXJnZXQ9Jyc+UHVibGljYcOnw7VlczwvYT48L2xpPjwvdWw+PC9saT48bGkgaWQ9J21lcmNhZG8nPjxhIGhyZWY9JyMnIGNsYXNzPSdtZXJjYWRvc2hvdmVyJyBpZD0nbGlua01lcmNhZG8nPjxpbWcgc3JjPScvc2hhcmVkL2Nzcy9pbWcvdHJhbnNwLmdpZicgLz48L2E+PHVsPjxsaT48YSBocmVmPScvcHQtYnIvbWVyY2Fkb3MvYWNvZXMuYXNweCcgdGFyZ2V0PScnPkHDp8O1ZXMgPC9hPjwvbGk+PGxpPjxhIGhyZWY9Jy9wdC1ici9tZXJjYWRvcy9tZXJjYWRvcmlhcy1lLWZ1dHVyb3MuYXNweCcgdGFyZ2V0PScnPk1lcmNhZG9yaWFzIGUgRnV0dXJvczwvYT48L2xpPjxsaT48YSBocmVmPScvcHQtYnIvaW50cm9zL2ludHJvLWNhbWJpby5hc3B4JyB0YXJnZXQ9Jyc+Q8OibWJpbzwvYT48L2xpPjxsaT48YSBocmVmPScvcHQtYnIvaW50cm9zL2ludHJvLWF0aXZvcy5hc3B4JyB0YXJnZXQ9Jyc+QXRpdm9zPC9hPjwvbGk+PGxpPjxhIGhyZWY9Jy9wdC1ici9pbnRyb3MvaW50cm8tZnVuZG9zLmFzcHgnIHRhcmdldD0nJz5GdW5kb3MgLyBFVEZzPC9hPjwvbGk+PGxpPjxhIGhyZWY9Jy9wdC1ici9pbnRyb3MvaW50cm8tbGVpbG9lcy5hc3B4JyB0YXJnZXQ9Jyc+TGVpbMO1ZXM8L2E+PC9saT48bGk+PGEgaHJlZj0nL1JlbmRhLUZpeGEvUmVuZGFGaXhhLmFzcHgnIHRhcmdldD0nJz5SZW5kYSBGaXhhPC9hPjwvbGk+PGxpPjxhIGhyZWY9Jy9wdC1ici9pbnRyb3MvaW50cm8tb3V0cm9zLXRpdHVsb3MuYXNweCcgdGFyZ2V0PScnPk91dHJvcyBUw610dWxvczwvYT48L2xpPjwvdWw+PC9saT48bGkgaWQ9J2NlbnRyb2RlaW5mb3JtYWNvZXMnPjxhIGhyZWY9JyMnIGNsYXNzPSdjZW50cm9kZWluZm9ybWFjb2VzJyBpZD0nbGlua0NlbnRybyc+PGltZyBzcmM9Jy9zaGFyZWQvY3NzL2ltZy90cmFuc3AuZ2lmJyAvPjwvYT48dWwgb25tb3VzZW92ZXI9ImxpbmtDZW50cm8uY2xhc3NOYW1lPSdjZW50cm9kZWluZm9ybWFjb2VzaG92ZXInOyIgb25tb3VzZW91dD0ibGlua0NlbnRyby5jbGFzc05hbWU9J2NlbnRyb2RlaW5mb3JtYWNvZXMnOyI+PGxpPjxhIGhyZWY9Jy9wdC1ici9lZHVjYWNpb25hbC9jdXJzb3MvY3Vyc29zLmFzcHgnIHRhcmdldD0nJz5DdXJzb3M8L2E+PC9saT48bGk+PGEgaHJlZj0nL3B0LWJyL2VkdWNhY2lvbmFsL3NpbXVsYWRvcmVzL3NpbXVsYWRvcmVzLmFzcHgnIHRhcmdldD0nJz5TaW11bGFkb3JlczwvYT48L2xpPjxsaT48YSBocmVmPScvcHQtYnIvZWR1Y2FjaW9uYWwvb3JjYW1lbnRvLXBlc3NvYWwuYXNweCcgdGFyZ2V0PScnPk9yw6dhbWVudG8gcGVzc29hbDwvYT48L2xpPjxsaT48YSBocmVmPScvcHQtYnIvZWR1Y2FjaW9uYWwvdmlkZW9zLWZvbGhldG9zLWVkdWNhdGl2b3MuYXNweCcgdGFyZ2V0PScnPlbDrWRlb3MgZSBGb2xoZXRvcyBFZHVjYXRpdm9zPC9hPjwvbGk+PGxpPjxhIGhyZWY9Jy9zaGFyZWQvaWZyYW1lLmFzcHg/aWRpb21hPXB0LWJyJnVybD1odHRwOi8vd3d3LmJtZmJvdmVzcGEuY29tLmJyL3B0LWJyL2VkdWNhY2lvbmFsL2VkdWNhci9Gb3JtSW5zY3JpY2FvUGFsZXN0cmFBY2Vzc29JbnN0LmFzcCcgdGFyZ2V0PScnPlBhbGVzdHJhcyBJbnN0aXR1Y2lvbmFpczwvYT48L2xpPjxsaT48YSBocmVmPScvcHQtYnIvZWR1Y2FjaW9uYWwvaW5pY2lhdGl2YXMuYXNweCcgdGFyZ2V0PScnPkluaWNpYXRpdmFzPC9hPjwvbGk+PC91bD48L2xpPjxsaSBpZD0nYWJhc2Vydmljb3MnPjxhIGhyZWY9JyMnIGNsYXNzPSdhYmFzZXJ2aWNvcycgaWQ9J2xpbmtTZXJ2aWNvJz48aW1nIHNyYz0nL3NoYXJlZC9jc3MvaW1nL3RyYW5zcC5naWYnIC8+PC9hPjx1bCBvbm1vdXNlb3Zlcj0ibGlua1NlcnZpY28uY2xhc3NOYW1lPSdzZXJ2aWNvc2hvdmVyJzsiIG9ubW91c2VvdXQ9ImxpbmtTZXJ2aWNvLmNsYXNzTmFtZT0nYWJhc2Vydmljb3MnOyI+PGxpPjxhIGhyZWY9Jy9wdC1ici9pbnRyb3MvaW50cm8tY29uZWN0aXZpZGFkZS5hc3B4JyB0YXJnZXQ9Jyc+U29sdcOnw7VlcyBkZSBDb25lY3RpdmlkYWRlPC9hPjwvbGk+PGxpPjxhIGhyZWY9Jy9wdC1ici9pbnRyb3MvaW50cm8tc2Vydmljb3MtZGUtaW5mb3JtYWNhby5hc3B4JyB0YXJnZXQ9Jyc+U2VydmnDp29zIGRlIEluZm9ybWHDp8OjbzwvYT48L2xpPjxsaT48YSBocmVmPScvcHQtYnIvaW50cm9zL2ludHJvLXNvbHVjb2VzLXBhcmEtbmVnb2NpYWNhby5hc3B4JyB0YXJnZXQ9Jyc+U29sdcOnw7VlcyBwYXJhIE5lZ29jaWHDp8OjbzwvYT48L2xpPjxsaT48YSBocmVmPScvcHQtYnIvaW50cm9zL2ludHJvLXNlcnZpY29zLWRlLXBvcy1uZWdvY2lhY2FvLmFzcHgnIHRhcmdldD0nJz5TZXJ2acOnb3MgZGUgUMOzcy1uZWdvY2lhw6fDo288L2E+PC9saT48bGk+PGEgaHJlZj0nL3B0LWJyL2ludHJvcy9pbnRyby1jZXJ0aWZpY2FjYW8uYXNweCcgdGFyZ2V0PScnPkNlcnRpZmljYcOnw6NvPC9hPjwvbGk+PGxpPjxhIGhyZWY9Jy9wdC1ici9zZXJ2aWNvcy9zb2x1Y29lcy1wYXJhLWVtcHJlc2FzL3NvbHVjb2VzLXBhcmEtZW1wcmVzYXMuYXNweCcgdGFyZ2V0PScnPlNvbHXDp8O1ZXMgcGFyYSBFbXByZXNhczwvYT48L2xpPjxsaT48YSBocmVmPScvcHQtYnIvaW50cm9zL2ludHJvLWVtcHJlc3RpbW8tZGUtYXRpdm9zLmFzcHgnIHRhcmdldD0nJz5FbXByw6lzdGltbyBkZSBBdGl2b3M8L2E+PC9saT48bGk+PGEgaHJlZj0naHR0cDovL3d3dy5ibWZib3Zlc3BhLmNvbS5ici9iYW5jbycgdGFyZ2V0PSdfYmxhbmsnPkJhbmNvIEJNJkZCT1ZFU1BBPC9hPjwvbGk+PC91bD48L2xpPjxsaSBpZD0ncmVndWxhY2FvJz48YSBocmVmPScjJyBjbGFzcz0ncmVndWxhY2FvJyBpZD0nbGlua1JlZ3VsYWNhbyc+PGltZyBzcmM9Jy9zaGFyZWQvY3NzL2ltZy90cmFuc3AuZ2lmJyAvPjwvYT48dWwgb25tb3VzZW92ZXI9ImxpbmtSZWd1bGFjYW8uY2xhc3NOYW1lPSdyZWd1bGFjYW9ob3Zlcic7IiBvbm1vdXNlb3V0PSJsaW5rUmVndWxhY2FvLmNsYXNzTmFtZT0ncmVndWxhY2FvJzsiPjxsaT48YSBocmVmPScvcHQtYnIvaW50cm9zL2ludHJvLWN1c3Rvcy1lLXRyaWJ1dG9zLmFzcHgnIHRhcmdldD0nJz5DdXN0b3MgZSBUcmlidXRvczwvYT48L2xpPjxsaT48YSBocmVmPScvcHQtYnIvaW50cm9zL2ludHJvLWhvcmFyaW9zLWRlLW5lZ29jaWFjYW8uYXNweCcgdGFyZ2V0PScnPkhvcsOhcmlvcyBkZSBOZWdvY2lhw6fDo288L2E+PC9saT48bGk+PGEgaHJlZj0nL3B0LWJyL3JlZ3VsYWNhby9jYWxlbmRhcmlvLWRvLW1lcmNhZG8vY2FsZW5kYXJpby1kby1tZXJjYWRvLmFzcHgnIHRhcmdldD0nJz5DYWxlbmTDoXJpbyBkbyBNZXJjYWRvPC9hPjwvbGk+PGxpPjxhIGhyZWY9Jy9wdC1ici9pbnRyb3MvaW50cm8tcmVndWxhbWVudG9zLWUtbm9ybWFzLmFzcHgnIHRhcmdldD0nJz5SZWd1bGFtZW50b3MgZSBOb3JtYXM8L2E+PC9saT48bGk+PGEgaHJlZj0naHR0cDovL3d3dy5ic20tYXV0b3JyZWd1bGFjYW8uY29tLmJyL2hvbWUuYXNwJyB0YXJnZXQ9J19ibGFuayc+U3VwZXJ2aXPDo28gZGUgTWVyY2FkbyAtIEJTTTwvYT48L2xpPjxsaT48YSBocmVmPScvb2ZpY2lvc0NvbXVuaWNhZG9zL29maWNpb3NDb211bmljYWRvcy5hc3B4P2lkaW9tYT1wdC1icicgdGFyZ2V0PScnPkNvbXVuaWNhZG9zIGFvIE1lcmNhZG88L2E+PC9saT48L3VsPjwvbGk+PGxpIGlkPSdwYXJ0aWNpcGFudGVzJz48YSBocmVmPScjJyBjbGFzcz0ncGFydGljaXBhbnRlcycgaWQ9J2xpbmtQYXJ0aWNpcGFudGVzJz48aW1nIHNyYz0nL3NoYXJlZC9jc3MvaW1nL3RyYW5zcC5naWYnIC8+PC9hPjx1bCBvbm1vdXNlb3Zlcj0ibGlua1BhcnRpY2lwYW50ZXMuY2xhc3NOYW1lPSdwYXJ0aWNpcGFudGVzaG92ZXInOyIgb25tb3VzZW91dD0ibGlua1BhcnRpY2lwYW50ZXMuY2xhc3NOYW1lPSdwYXJ0aWNpcGFudGVzJzsiPjxsaT48YSBocmVmPScvcHQtYnIvaW50cm9zL2ludHJvLWNvcnJldG9yYXMuYXNweCcgdGFyZ2V0PScnPkNvcnJldG9yYXM8L2E+PC9saT48bGk+PGEgaHJlZj0nL0FnZW50ZXMvYWdlbnRlcy5hc3B4JyB0YXJnZXQ9Jyc+QWdlbnRlcyBkZSBDdXN0w7NkaWEgZSBDb21wZW5zYcOnw6NvPC9hPjwvbGk+PGxpPjxhIGhyZWY9Jy9zaGFyZWQvaWZyYW1lLmFzcHg/YWx0dXJhPTE0NTAmaWRpb21hPXB0LWJyJnVybD13d3cyLmJtZi5jb20uYnIvcGFnZXMvcG9ydGFsL2JtZmJvdmVzcGEvYXNzb2NpYWRvczEvYXNzb2NpYWRvc1Blc3F1aXNhMS5hc3AnIHRhcmdldD0nJz5PdXRyb3MgUGFydGljaXBhbnRlczwvYT48L2xpPjxsaT48YSBocmVmPScvcHQtYnIvUGFydGljaXBhbnRlcy9QUU8vUHJvZ3JhbWEtZGUtcXVhbGlmaWNhY2FvLW9wZXJhY2lvbmFsLmFzcHgnIHRhcmdldD0nJz5Qcm9ncmFtYSBkZSBRdWFsaWZpY2HDp8OjbyBPcGVyYWNpb25hbDwvYT48L2xpPjxsaT48YSBocmVmPScvc2hhcmVkL2lmcmFtZS5hc3B4P2FsdHVyYT00MDAmaWRpb21hPXB0LWJyJnVybD1odHRwOi8vd3d3LmJtZmJvdmVzcGEuY29tLmJyL3B0LWJyL21lcmNhZG9zL21lcmNhZG9yaWFzLWUtZnV0dXJvcy9wYXJ0aWNpcGFudGVzL2RvY3VtZW50YWNhby1jYWRhc3RyYWwuYXNwJyB0YXJnZXQ9Jyc+RG9jdW1lbnRhw6fDo28gQ2FkYXN0cmFsPC9hPjwvbGk+PC91bD48L2xpPjxsaSBpZD0naW52aXN0YWphJz48YSBocmVmPScjJyBjbGFzcz0naW52aXN0YWphJyBpZD0nbGlua2ludmlzdGFqYSc+PGltZyBzcmM9Jy9zaGFyZWQvY3NzL2ltZy90cmFuc3AuZ2lmJyAvPjwvYT48dWwgb25tb3VzZW92ZXI9ImxpbmtpbnZpc3RhamEuY2xhc3NOYW1lPSdpbnZpc3RhamFob3Zlcic7IiBvbm1vdXNlb3V0PSJsaW5raW52aXN0YWphLmNsYXNzTmFtZT0naW52aXN0YWphJzsiPjxsaT48YSBocmVmPScvY29tby1pbnZlc3Rpci1uYS1ib2xzYS5hc3B4JyB0YXJnZXQ9Jyc+Q29tbyBpbnZlc3RpciBlbSBhw6fDtWVzIDwvYT48L2xpPjxsaT48YSBocmVmPScvcHQtYnIvbWVyY2Fkb3Mvb3V0cm9zLXRpdHVsb3MvdGVzb3Vyby1kaXJldG8vY29tby1pbnZlc3Rpci1uby10ZXNvdXJvLWRpcmV0by5hc3B4JyB0YXJnZXQ9Jyc+Q29tbyBpbnZlc3RpciBubyBUZXNvdXJvIERpcmV0bzwvYT48L2xpPjxsaT48YSBocmVmPScvZXRmL2NvbW8taW52ZXN0aXItZW0tZXRmcy5hc3B4JyB0YXJnZXQ9Jyc+Q29tbyBpbnZlc3RpciBlbSBFVEZzPC9hPjwvbGk+PGxpPjxhIGhyZWY9Jy9GdW5kb3MtTGlzdGFkb3MvY29tby1pbnZlc3Rpci1lbS1mdW5kb3MtaW1vYmlsaWFyaW9zLmFzcHgnIHRhcmdldD0nJz5Db21vIGludmVzdGlyIGVtIGZ1bmRvcyBpbW9iaWxpw6FyaW9zPC9hPjwvbGk+PGxpPjxhIGhyZWY9Jy9wdC1ici9pbnRyb3MvaW50cm8tdGlwb3MtZGUtaW52ZXN0aW1lbnRvcy5hc3B4JyB0YXJnZXQ9Jyc+VGlwb3MgZGUgaW52ZXN0aW1lbnRvczwvYT48L2xpPjwvdWw+PC9saT48L3VsPjwvZGl2PmQCCQ9kFgICBQ9kFgICAw8PZBYCHwUFYndpbmRvdy5vcGVuKCdodHRwOi8vd3d3LmJtZmJvdmVzcGEuY29tLmJyL2V0Zi9mdW5kby1kZS1pbmRpY2UuYXNweD9JZGlvbWE9cHQtYnImdmVyc2FvPWltcHJlc3NhbycpZAILD2QWAgIBD2QWBGYPFCsAAg8WAh4NU2VsZWN0ZWRJbmRleAIBZBQrAAIUKwACZGQUKwACZGRkAgIPDxYEHwoCAR4FQ291bnQCAmQWBGYPDxYEHgJJRAUPcGd2RVRGc0xpc3RhZG9zHwRoZBYCAgEPZBYCZg9kFgQCAw8WAh4LXyFJdGVtQ291bnQCDxYeAgEPZBYUAgEPDxYCHgtOYXZpZ2F0ZVVybAUqRVRGRGV0YWxoZS5hc3B4P0NvZGlnbz1YQk9WMTEmaWRpb21hPXB0LUJSZBYEZg8WAh8JBQ9DQUlYQUVURlhCT1YgQ0lkAgEPFgIfCWVkAgMPFgIfCQUGWEJPVjExZAIFDxYCHwkFCjA4LzExLzIwMTNkAgcPFgIfCQUFNTIs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AgMPFgIfCQUFMjIsMDJkAgUPFgIfCQUFMjEsNTZkAgcPFgIfCQUFMjIsMDhkAgkPFgIfCQUFMjEsNzFkAgsPDxYGHwkFBS0xLDQzHw8FCG5lZ2F0aXZvHxACAmRkAgkPZBYMAgEPFgIfCQUKRUNPTyAgICAgIGQCAw8WAh8JBQU1NiwwM2QCBQ8WAh8JBQU1NSwwMmQCBw8WAh8JBQU1NiwwM2QCCQ8WAh8JBQU1NSw1NmQCCw8PFgYfCQUFLTAsODUfDwUIbmVnYXRpdm8fEAICZGQCCg9kFgwCAQ8WAh8JBQpQSUJCICAgICAgZAIDDxYCHwkFBTkxLDgxZAIFDxYCHwkFBTkwLDIwZAIHDxYCHwkFBTkxLDg3ZAIJDxYCHwkFBTkwLDk3ZAILDw8WBh8JBQUtMCw5Nh8PBQhuZWdhdGl2bx8QAgJkZAILD2QWDAIBDxYCHwkFCkRJVk8gICAgICBkAgMPFgIfCQUFMzUsMTVkAgUPFgIfCQUFMzQsNTZkAgcPFgIfCQUFMzUsMjFkAgkPFgIfCQUFMzQsODJkAgsPDxYGHwkFBS0wLDk4Hw8FCG5lZ2F0aXZvHxACAmRkAgwPZBYMAgEPFgIfCQUKRklORCAgICAgIGQCAw8WAh8JBQU0Miw5NmQCBQ8WAh8JBQU0MSw3OGQCBw8WAh8JBQU0Miw5NmQCCQ8WAh8JBQU0MiwyOGQCCw8PFgYfCQUFLTEsNjAfDwUIbmVnYXRpdm8fEAICZGQCDQ9kFgwCAQ8WAh8JBQpHT1ZFICAgICAgZAIDDxYCHwkFBTIxLDQ5ZAIFDxYCHwkFBTIxLDA3ZAIHDxYCHwkFBTIxLDQ5ZAIJDxYCHwkFBTIxLDI2ZAILDw8WBh8JBQUtMSwxMB8PBQhuZWdhdGl2bx8QAgJkZAIOD2QWDAIBDxYCHwkFCk1BVEIgICAgICBkAgMPFgIfCQUFMTksMTNkAgUPFgIfCQUFMTgsODdkAgcPFgIfCQUFMTksMjFkAgkPFgIfCQUFMTksMTVkAgsPDxYGHwkFBDAsMTEfDwUIcG9zaXRpdm8fEAICZGQCDw9kFgwCAQ8WAh8JBQpJU1VTICAgICAgZAIDDxYCHwkFBTI0LDkyZAIFDxYCHwkFBTI0LDQ2ZAIHDxYCHwkFBTI0LDkyZAIJDxYCHwkFBTI0LDY5ZAILDw8WBh8JBQUtMCw5NB8PBQhuZWdhdGl2bx8QAgJkZAINDw9kFgIfBQUcaGlzdG9yeS5iYWNrKCk7IHJldHVybiBmYWxzZWQCEw8PFgIfBGdkZBgDBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAwUrY3RsMDAkY29udGVudFBsYWNlSG9sZGVyQ29udGV1ZG8kZXRmJG1wZ0VURgUbY3RsMDAkbWVudUJPVkVTUEFTZWN1bmRhcmlvBStjdGwwMCRjb250ZW50UGxhY2VIb2xkZXJDb250ZXVkbyRldGYkdGFiRVRGBTdjdGwwMCRjb250ZW50UGxhY2VIb2xkZXJDb250ZXVkbyRldGYkbXZ3VmFsb3JSZWZlcmVuY2lhDw9kZmQFNGN0bDAwJGNvbnRlbnRQbGFjZUhvbGRlckNvbnRldWRvJGV0ZiRtdndFVEZzTGlzdGFkb3MPD2RmZOjw72jsEPl9Ys5BnCP4WNL6mC/j',
	'__EVENTVALIDATION':'/wEWBgL1ncvTAgKatY+lDgLz2ISXCALR05XvBgKWjICHCwK0s+TyDh9deCG52udWPt7QTuuNm6jc+FM9',
	'ctl00$ucTopo$btnBusca':'Busca',
	'ctl00$menuBOVESPASecundario':'',
	'ctl00$contentPlaceHolderConteudo$etf$tabETF':'{"State":{"SelectedIndex":1},"TabState":{"ctl00_contentPlaceHolderConteudo_etf_tabETF_tabETFsListados":{"Selected":false},"ctl00_contentPlaceHolderConteudo_etf_tabETF_tabValorReferencia":{"Selected":true}}}',
	'ctl00$contentPlaceHolderConteudo$etf$mpgETF_Selected':"1",
	'cboAgentesCorretorasNome':'#',
	'cboAgentesCorretorasCodigo':'#'
}
param_etf_url = 'http://www.bmfbovespa.com.br/etf/fundo-de-indice.aspx?Idioma=pt-br'
req_instance = conn.parametric_connection(param_etf_url, **req_dict)
param_etf_dict = vd.fparser('etfs',conn.read(req_instance))
#'''


# Faz download do arquivo:
# 'Mercado de Derivativos - Indicadores Econômicos e Agropecuários - Final'
# em formato ZIP publicado pela bovespa diariamente
last_bd = datetime.strptime(last_biz_day, "%Y-%m-%d").date()
bulletim_date = last_bd.strftime('%d/%m/%Y')

bulletim_url = 'http://www.bmf.com.br/arquivos1/download.asp'
bulletim_req_dict = {
	'C10':'ON',
	'T10':bulletim_date
}
req_instance = conn.parametric_connection(bulletim_url, **bulletim_req_dict)
# Este trecho devolve um arquivo zip - ou deveria
content_bulletim = StringIO(conn.read(req_instance))
zf = zipfile.ZipFile(content_bulletim, "r")
zf.extractall("C:\Users\libarreto\Documents\SVN\Estudos\DataMonitor\datamonitor")

# Essa função retorna o dicionário com o arquivo Indic.txt parsed (parseado???)
# e escreve a tabela na variável bulletim necessária para a função da biblioteca
# validation.py
with open('Indic.txt') as f:
	content = f.read()
vd.published_econ_agri_indic(content) # não preciso do dicionário nesse caso
url_valid = 'http://www.bmf.com.br/bmfbovespa/pages/boletim1/bd_manual/indicadoresFinanceiros1.asp'
bulletim = 'IndicRelatorio' + last_biz_day + '.txt'
validict = vd.validation_parser(conn.read(url_valid), bulletim)

# Deixa ambos dicionários na mesma ordem
dictionary = dict(sorted(dictionary.iteritems(), key=operator.itemgetter(0)))
validict = dict(sorted(validict.iteritems(), key=operator.itemgetter(0)))

'''
# Escreve o status da validação de indicadores

if dictionary == validict:
	status = 'Validacao OK'
else:
	status = 'Erro durante Validacao'

print '\n' + status + '\n'
print 'Capturado : ', dictionary
print 'Publicado : ', validict
'''

#-------------------------------------------------------------------------------
# Construção do Relatório em HTML
#-------------------------------------------------------------------------------

# Dicionário de testes e cores para comparação das publicações com as capturas
result_colors = {
	True: None,
	False: 'RED',
}

# ------------------------------------------------------------------------------

#
# Conexões Diretas
#

# ------------------------------------------------------------------------------
# Dados Publicados
# ------------------------------------------------------------------------------

# Cria uma tabela com os valores capturados e os publicados
list_table = [[i, dictionary[i].items(),validict[i].items()] for i in dictionary]

# Separa os títulos das linhas em uma coluna separada
indics = [list_table[i][1][1][1] for i in range(len(list_table))]

# Cria as linhas da tabela em html
htmlindics =  [HTML.TableRow([indics[k]]) for k,i in enumerate(indics)]

# Cria as colunas de capturados e publicados
sub_table1 = [list_table[i][1] for i in range(len(list_table))]
sub_table2 = [list_table[i][2] for i in range(len(list_table))]

# Cria o teste para comparação dos valores capturados e publicados
test_results = [False for i in sub_table1]

for k,j in enumerate(sub_table1):
	if j == sub_table2[k]:
		test_results[k] = True

colors = [result_colors[i] for i in test_results]

# Gera as linhas da tabelas em html com as cores dos testes
sub_table1 = [HTML.TableRow((sub_table1[i][0][1],sub_table1[i][2][1]), bgcolor=colors[i]) for i in range(len(sub_table1))]
sub_table2 = [HTML.TableRow((sub_table2[i][0][1],sub_table2[i][2][1]), bgcolor=colors[i]) for i in range(len(sub_table2))]

# Gera o código de tabela em html
htmlindics = HTML.table(htmlindics)
htmltable1 = HTML.table(sub_table1)
htmltable2 = HTML.table(sub_table2)

# Encadeia o header e as tabelas
table =  HTML.Table(header_row = ['Indicator','Captured','Published'])#,attribs={'bgcolor': 'white'})
table.rows = [[htmlindics, htmltable1, htmltable2]]

# Transforma o objeto da biblioteca HTML.py em string
htmlcode = str(table)


# ------------------------------------------------------------------------------
# Dados Não Publicados
# ------------------------------------------------------------------------------

# Cria tabela com os dados de IGPM do ajuste de NTNC, IPCA do ajuste de NTNB, 
# Estimativa da Selic do dia atual e VNA da LFT
unpub_list_table = [[i, unpub_dict[i].items()] for i in unpub_dict]
# Separa os títulos das linhas em uma coluna separada
unpub_indics = [unpub_list_table[i][1][1][1] for i in range(len(unpub_list_table))]
# Cria as linhas da tabela em html
html_unpub_indics =  [HTML.TableRow([unpub_indics[k]]) for k,i in enumerate(unpub_indics)]
# Cria as colunas de capturados
unpub_sub_table1 = [unpub_list_table[i][1] for i in range(len(unpub_list_table))]
unpub_sub_table1 = [HTML.TableRow((unpub_sub_table1[i][0][1],unpub_sub_table1[i][2][1])) for i in range(len(unpub_sub_table1))]
# Gera o código html das tabelas
html_unpub_indics = HTML.table(html_unpub_indics)
html_unpub_table1 = HTML.table(unpub_sub_table1)
# Encadeia os títulos com as tabelas
table =  HTML.Table(header_row = ['Indicator','Captured'])
table.rows = [[html_unpub_indics, html_unpub_table1]]
# Transforma o objeto da biblioteca HTML.py em string
htmlcode_unpub = str(table)


# ------------------------------------------------------------------------------
# Dados ProRataTempore de IGP-M e IPCA
# ------------------------------------------------------------------------------
pro_rata_headers = ['Indicador','Data Ref','DU Total','Pro Rata','Futuro','DU do Mês','Var. %', 'Núm. Índ. Mês Ant.']
table_pro_rata = HTML.Table()
table_pro_rata.rows.append(HTML.TableRow(pro_rata_headers, header=True))

igpm_bmf.insert(0,'IGPM BM&f')
igpm_pub.insert(0,'IGPM DIVULGAÇÃO')
ipca_bmf.insert(0,'IPCA BM&F')
ipca_ativos.insert(0,'IPCA ATIVOS')

table_pro_rata.rows.append(HTML.TableRow(igpm_bmf))
table_pro_rata.rows.append(HTML.TableRow(igpm_pub))
table_pro_rata.rows.append(HTML.TableRow(ipca_bmf))
table_pro_rata.rows.append(HTML.TableRow(ipca_ativos))

htmlcode_pro_ratas = str(table_pro_rata)

# ------------------------------------------------------------------------------
# Dados Não Publicados do Tesouro
# ------------------------------------------------------------------------------

# Separa os headers numa lista
unpub_headers =  [list(unpub_tresury_dict[i])[0] for i in unpub_tresury_dict][0]
# Instancia um objeto table da biblioteca HTML.py
table_tresury =  HTML.Table()
# Anexa a linha de título diretamente como linha html
table_tresury.rows.append(HTML.TableRow(unpub_headers, header=True))
# Anexa as linhas da tabela diretamente como html
for j in unpub_tresury_dict:
	for k in range(len(list(unpub_tresury_dict[j]))):
		# Tira o título do corpo da tabela
		if 'Titulo' not in list(unpub_tresury_dict[j])[k]:
			table_tresury.rows.append(HTML.TableRow(list(unpub_tresury_dict[j])[k]))
# Transforma o objeto da biblioteca HTML.py em string
htmlcode_unpub_tresury = str(table_tresury)


# ------------------------------------------------------------------------------
# Dados CMT
# ------------------------------------------------------------------------------

# Extrai apenas a tabela de valores de CMT do dicionário retornado do parser
cmt_list = cmt_dict['value']
# Separa os títulos numa lista
cmt_headers = [cmt_list[0][i] for i in range(len(cmt_list[0]))]
# Instancia um objeto table da biblioteca HTML.py
table_cmt =  HTML.Table()
# Anexa a linha de título diretamente como linha html
table_cmt.rows.append(HTML.TableRow(cmt_headers, header=True))
# Anexa as linhas da tabela diretamente como html
for k,i in enumerate(cmt_list):
	if k != 0: # Tira os títulos do corpo da tabela 
		table_cmt.rows.append(HTML.TableRow(cmt_list[k]))
# Transforma o objeto da biblioteca HTML.py em string
htmlcode_unpub_cmt = str(table_cmt)


# ------------------------------------------------------------------------------
#
# Conexões Paramétricas - Por formulário
#

# ------------------------------------------------------------------------------
# Dados ETFs
# ------------------------------------------------------------------------------

# Extrai apenas a tabela de valores de ETFs do dicionário retornado do parser
param_list = param_etf_dict['etf_iopv']
# Hardcodeia (???) os títulos para não ter problema com encoding - trust me on this...
param_headers = ['Código','Abert.','Min.','Máx.','Último','Osc.(%)']

table_etf =  HTML.Table()
table_etf.rows.append(HTML.TableRow(param_headers, header=True))
for k,i in enumerate(param_list):
	if k != 0:
		table_etf.rows.append(HTML.TableRow(param_list[k]))

# Transforma o objeto da biblioteca HTML.py em string
htmlcode_unpub_etf = str(table_etf)

'''
# Dados BCB Dólar Intradiário - MALDITO NÃO FUNCIONA - alguém reclama com o cara
# que fez a conexão por proxy da BMF !!???!!!
'''

# ------------------------------------------------------------------------------
# Dados Ptax
# ------------------------------------------------------------------------------

param_bcb_ptax_list = param_bcb_ptax_dict['ptax_table'] 
# Hardcodeia (???) os títulos - porque eu não consegui fazer melhor - Catch me if you can.
param_headers = ['Data','Cod Moeda','Tipo','Moeda','Taxa Compra','Taxa Venda','Paridade Compra','Paridade Venda']

table_ptax =  HTML.Table()
table_ptax.rows.append(HTML.TableRow(param_headers, header=True))
for k,i in enumerate(param_bcb_ptax_list):
	if k != 0:
		table_ptax.rows.append(HTML.TableRow(param_bcb_ptax_list[k]))
# Neste ponto já imagino que você tenha lido a biblioteca do HTML.py
htmlcode_unpub_ptax = str(table_ptax) # Se ainda não leu, ´faiz´ favor.

#-------------------------------------------------------------------------------
# Gravação do Código HTML em arquivo - HOOOORAY!
#-------------------------------------------------------------------------------

HTMLFILE = 'HTML_report_' + date.today().isoformat() + '.html'
f = open(HTMLFILE, 'w')
f.write('<!DOCTYPE HTML><HTML>\n')
f.write('<HEAD><META charset="ISO-8859-1"></HEAD>\n')
f.write('<BODY style="font-family:Verdana; font-variant: small-caps; font-size:90%;">\n')
f.write('<CENTER><HEADER><H1><B>Validação de Capturas e Publicações</B></H1></HEADER>')
f.write(htmlcode)
f.write('<HEADER><H1><B>Captura de Indicadores sem Publicações</B></H1></HEADER>')
f.write(htmlcode_unpub)
f.write('<HEADER><H2><B>Cálculo de Pro Rata Tempore de Inflação</B></H2></HEADER>')
f.write(htmlcode_pro_ratas)
f.write('<HEADER><H2><B>Captura de ETFs em '+param_etf_dict['date']+'</B></H2></HEADER>')
f.write(htmlcode_unpub_etf)
f.write('<HEADER><H2><B>Captura de CMT</B></H2></HEADER>')
f.write(htmlcode_unpub_cmt)
f.write('<HEADER><H2><B>Captura de Indicadores de Títulos Públicos</B></H2></HEADER>')
f.write(htmlcode_unpub_tresury)
f.write('<HEADER><H2><B>Captura da PTAX do BaCen</B></H2></HEADER>')
f.write(htmlcode_unpub_ptax)
f.write('\n</CENTER></BODY></HTML>')
f.close()
