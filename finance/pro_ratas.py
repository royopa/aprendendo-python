# coding:utf-8

"""
Esse módulo efetua o cálculo dos índices pró-rata de IGP-M e IPCA
"""

__version__ = '0.1'
__date__    = '2013-12-31'
__author__  = 'Liz Alexandrita de Souza Barreto'

#--- LICENSE -------------------------------------------------------------------
#
#--- CHANGES -------------------------------------------------------------------
# 
#--- TO DO ---------------------------------------------------------------------
#	* 
#	* 

# Espaço para importações
import bizdays as bd
import datetime as dt
import locale

# Classe de funções que calculam pro-rata mensal do IGP-M e IPCA
class ProRataTempore:
	def __init__(self, cal):
		self.cal = cal
	
	# Função que retorna o número índice proporcional ao dia dado.
	# Por ser usada tanto para IGP-M quando IPCA (BM&F e Ativos), necessita 
	# indicar qual o dia inicia a contagem de dias úteis no mês e o dia que termina no formato ISO
	def index_month_day(self, range_days, biz_date, variation, index_last_publication, isPub):
		# range_days é uma lista com os seguintes dois elementos em ordem:
		# [dia inicial da contagem de dias úteis, dia final da contagem de dias úteis]
		# biz_date é o dia de refência que será efetuado o cálculo
		# variation é a variação percentual da prévia (ou publicação)
		# index_last_publication é o número índice da última publicação
		# isPub é uma lista que contém dois elementos: [booleano indicando se 
		# hoje é dia de publicação (True) ou não (False), string com o número
		# índice da publicação do mês anterior caso hoje seja dia de divulgação 
		# e caso contrário conterá uma string vazia]
		ref_month = dt.datetime.strptime(biz_date, '%Y-%m-%d').date().month
		biz_days_month = self.biz_days_month(range_days)
		biz_days = self.biz_days(biz_date, range_days[0])
		isPub, last_ind = isPub
		if not isPub:
			# Se não for dia da publicação, a última publicação capturada no
			# site da anbima será a publicação do mês anterior
			index_future = self.index_future(variation, index_last_publication)
			return [
				biz_date, biz_days_month,
				str(round(float(index_last_publication) * ((index_future/float(index_last_publication)) ** (float(biz_days)/float(biz_days_month))),3)), 
				str(round(index_future,3)), biz_days, variation, index_last_publication
			]
		else:
			# Se 'hoje' for dia da publicação, a última publicação captura no
			# site da anbima será o número índice de hoje, mas ainda precisamos
			# da publicação do mês anterior, portanto o usuário deve
			# explicitá-lo nos parâmetros da função
			index_future = float(index_last_publication)
			return [
				biz_date, biz_days_month, 
				str(round(float(last_ind) * ((index_future/float(last_ind)) ** (float(biz_days)/float(biz_days_month))),3)), 
				str(round(index_future,3)), biz_days, variation, last_ind
			]
	
	# Função que retorna o Futuro usado para o Cálculo do Pro-Rata de IGP-M,
	# IPCA BM&F e IPCA Ativos
	def index_future(self, variation, index_last_publication):
		return round(float(index_last_publication) * (1.0 + (float(variation)/100.0)),3)

	
	# Função que retorna a quantidade de dias úteis em um mês 
	# ou entre dois dias fixos
	def biz_days_month(self, range_days):
		day_init, day_end = range_days
		pro_rata_date = dt.datetime.strptime(day_init, '%Y-%m-%d').date()
		first_biz_day = self.cal.adjust_next(pro_rata_date.isoformat())
		pro_rata_date = dt.datetime.strptime(day_end, '%Y-%m-%d').date()
		last_biz_day = self.cal.adjust_next(pro_rata_date.isoformat())
		return self.cal.bizdays([first_biz_day, last_biz_day])
	
	# Função que retorna a quantidade de dias úteis entre o dia de referência e 
	# o dia de início da contagem
	def biz_days(self, biz_date, day_init):
		biz_date_dt = dt.datetime.strptime(biz_date, '%Y-%m-%d').date()
		pro_rata_date = dt.datetime.strptime(day_init, '%Y-%m-%d').date()
		first_biz_day = self.cal.adjust_next(pro_rata_date.isoformat())
		return self.cal.bizdays([first_biz_day, biz_date])
	
	# Função que guarda um log de cálculos de índices no formato do IGP-M
	# Para o IPCA também será usado apenas separando o BM&F de Ativos, pois têm 
	# dinâmicas diferentes
	def print_log(self, index_name, range_days, biz_date, variation, index_last_publication):
		index_month_day = []
		index_month_day = self.index_month_day(range_days, biz_date, variation, index_last_publication, isPub)
		biz_date = dt.datetime.strptime(biz_date,"%Y-%m-%d").date()
		locale.setlocale(locale.LC_TIME,'ptb')
		ref_month_year = biz_date.strftime('%B %Y')
		locale.setlocale(locale.LC_TIME,'')
		
		with open(index_name+' Pro-Rata '+ref_month_year+'.log', 'a+') as f:
			for i in index_month_day:
				f.write("%s," % i)
			f.write('\n')
