# -*- coding: utf-8 -*-
import requests


def get_url(url):
    # Get the page
    r = requests.get(url)
    print(url)
    return r

urls = [
    #'http://www.ojs.hol.es',
    #'http://www.tematres.esy.es',
    # 'http://www.trello-control-doc-pt-br.esy.es',
    'http://www.sicin.esy.es',
    'http://www.phpsp.esy.es',
    'http://www.citationbuilder.url.ph',
    'http://www.dspace.url.ph',
    'http://www.kdodoc.url.ph'
]

for url in urls:
    print(get_url(url))
