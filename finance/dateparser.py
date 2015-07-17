# coding:utf-8

import re
import datetime
import locale

'''
20130909
09/18/13
18/09/2013
09/09/2013
18 de Setembro de 2013
09/Set/2013
Wednesday Sep 18, 2013
'''

months_ptb = {
    "Janeiro": "01",
    "Fevereiro": "02",
    "Marco": "03",
    "Abril": "04",
    "Maio": "05",
    "Junho": "06",
    "Julho": "07",
    "Agosto": "08",
    "Setembro": "09",
    "Outubro": "10",
    "Novembro": "11",
    "Dezembro": "12",
}

def _parse_type_1(tokens):
    r"(\d\d?) de ([\w\S]+) de (\d\d\d\d)"
    #print tokens[1]
    return '%s-%s-%s' % (tokens[2], months_ptb[tokens[1]], tokens[0].zfill(2))

def parse_type_1(content):
    #locale.setlocale(locale.LC_TIME,'ptb') # tenta todos os formatos em portugues brasileiro antes
    #date_list.append(datetime.strptime(cont_list[j],fmt_list[j]))
    #print('>>>')
    #print(content)
    content = re.sub('Mar.+o', 'Marco', content)
    #print(content)
    m = re.match(_parse_type_1.__doc__, content)
    if m:
        return _parse_type_1(m.groups())
    else:
        raise Exception()


