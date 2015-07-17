#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from flask import Flask, jsonify
from flask.ext import restful

app = Flask(__name__)
api = restful.Api(app)

class BancoDb:
    def __init__(self, nome):
        self.nome = nome

    def findOneBancoByNome(self):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        t = ('%'+self.nome+'%',)
        for row in cursor.execute('SELECT * FROM instituicao_financeira WHERE nome LIKE ?', t):
            return [
                {'param': 'data_posicao', 'val': row[0]},
                {'param': 'cnpj', 'val': row[1]},
                {'param': 'nome', 'val': row[2]},
                {'param': 'segmento', 'val': row[3]},
                {'param': 'endereco', 'val': row[4]},
                {'param': 'complemento', 'val': row[5]},
                {'param': 'bairro', 'val': row[6]},
                {'param': 'cep', 'val': row[7]},
                {'param': 'municipio', 'val': row[8]},
                {'param': 'uf', 'val': row[9]},
                {'param': 'ddd', 'val': row[10]},
                {'param': 'fone', 'val': row[11]},
                {'param': 'carteira_comercial', 'val': row[12]},
                {'param': 'email', 'val': row[13]},
                {'param': 'site', 'val': row[14]}
            ]

class BancoApi(restful.Resource):
    def get(self, nome):
        db = BancoDb(nome)
        print("Parametro:", nome)
        list = db.findOneBancoByNome()
        return jsonify(results=list)        

api.add_resource(BancoApi, '/banco/<string:nome>')

if __name__ == '__main__':
    app.run(debug=True)                 
