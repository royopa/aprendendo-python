# -*- coding: utf-8 -*-
import requests
import json


def get_url(url):
    # Get the page
    r = requests.get(url)
    # Convert it to a Python dictionary
    data = json.loads(r.text)
    ip = data['ip']

    return ip

qtdConsultas = int(input('Digite a quantidade de consultas: '))
url = 'http://www.telize.com/jsonip'
list = []
i = 0

while i < qtdConsultas:

    ip = get_url(url)

    print(i)
    print(ip)

    if ip not in list:
        list.append(ip)
        print(sorted(list))
    i = i + 1

print(sorted(list))
