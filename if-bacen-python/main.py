#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xlrd, re, datetime, time, sqlite3, json
from flask import jsonify

def get_data_posicao(worksheet):
    cell_posicao = worksheet.cell_value(6, 0)
    data_posicao = cell_posicao[9:]
    data = time.strptime(data_posicao, "%d.%m.%Y")
    return time.strftime('%Y-%m-%d', data)

def open_workbook(path_file):
    workbook = xlrd.open_workbook(path_file)
    return workbook

def open_worksheet(path_file, name_worksheet):
    workbook = open_workbook(path_file)
    return workbook.sheet_by_name('Plan1')

def print_worksheet(worksheet):
    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    curr_row = -1

    while curr_row < num_rows:
        curr_row += 1
        row = worksheet.row(curr_row)
        print ('Row:', curr_row)
        curr_cell = -1
        while curr_cell < num_cells:
            curr_cell += 1
            # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
            cell_type = worksheet.cell_type(curr_row, curr_cell)
            cell_value = worksheet.cell_value(curr_row, curr_cell)
            print (' ', cell_type, ':', cell_value)

def create_tables(conn):
    c = conn.cursor()
    c.execute('''DROP TABLE instituicao_financeira''')
    # Create table
    c.execute('''CREATE TABLE instituicao_financeira
                 (
                    data_posicao text,
                    cnpj text,
                    nome text,
                    segmento text,
                    endereco text,
                    complemento text,
                    bairro text,
                    cep text,
                    municipio text,
                    uf text,
                    ddd text,
                    fone text,
                    carteira_comercial text,
                    email text,
                    site text
                )''')

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

def get_registros(worksheet):
    num_rows = worksheet.nrows - 1
    curr_row = -1
    registros = []
    data_posicao = get_data_posicao(worksheet)

    print('Data Posição: ', data_posicao)
    
    while curr_row < num_rows:
        row_if = []
        curr_row += 1
        row = worksheet.row_values(curr_row)

        cnpj     = str(row[0]).strip().replace(".","")[:8]
        nome     = str(row[1]).strip()
        segmento = str(row[2]).strip()

        if len(cnpj) > 0 and len(nome) > 0 and len(segmento) > 0 and cnpj != 'CNPJ':

            row = [data_posicao,
                   cnpj[:8],
                   nome,
                   segmento,
                   str(row[3]).strip(),
                   str(row[4]).strip(),
                   str(row[5]).strip(),
                   int(row[6]),
                   str(row[7]).strip(),
                   str(row[8]).strip(),
                   int(row[9]),
                   int(row[10]),
                   str(row[11]).strip(),
                   str(row[12]).strip().lower(),
                   str(row[13]).strip().lower()]
            
            registros.append(row)
        else:
            print('Registro não inserido', row)

    return registros

def insert_registros(conn, registros):
    c = conn.cursor()

    # Larger example that inserts many records at a time
    c.executemany('INSERT INTO instituicao_financeira VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', registros)

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

def findBancoByNome(nome):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    t = ('%'+nome+'%',)
    cursor.execute('SELECT * FROM instituicao_financeira WHERE nome LIKE ?', t)
    data = cursor.fetchall()
    return json.dumps(data)

def findOneBancoByNome(nome):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    t = ('%'+nome+'%',)
    for row in cursor.execute('SELECT * FROM instituicao_financeira WHERE nome LIKE ?', t):
        return row

#criação de base de dados e tabelas
#conn = sqlite3.connect('data.db')
#create_tables(conn)

#importação da base de bancos
#conn = sqlite3.connect('data.db')
#name_file = '201502BANCOS.xls'
#name_file = '201503BANCOS.xls'
#worksheet = open_worksheet(name_file, 'Plan1')
#registros = get_registros(worksheet)
#insert_registros(conn, registros)
#print(len(registros), "registros importados")


print(findOneBancoByNome('itau'))
