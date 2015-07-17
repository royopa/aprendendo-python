# -*- coding: utf-8 -*-
import requests
import json


http://www.debentures.com.br/exploreosnd/consultaadados/emissoesdedebentures/puhistorico_e.asp?op_exc=False&ativo=DASA12++++&dt_ini=&dt_fim=&Submit.x=10&Submit.y=9

def get_url(url):
    # Get the page
    r = requests.get(url)
    # Convert it to a Python dictionary
    data = json.loads(r.text)
    ip = data['ip']

    return ip

qtdConsultas = int(input('Digite a quantidade de consultas: '))
url = 'http://ip.jsontest.com/'
list = []
i = 0

while i < qtdConsultas:

    ip = get_url(url)

    print(i)
    print(ip)

    if ip not in list:
        list.append(ip)
    i = i + 1

print(sorted(list))
