#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

# receber os três números
numero1 = input("Digite o primeiro número (inteiro): ")
# converter número para inteiro
numero1 = int(numero1)

numero2 = input("Digite o segundo número (inteiro): ")
numero2 = int(numero2)

numero3 = input("Digite o terceiro número (inteiro): ")
numero3 = int(numero3)

#calcula a média dos três números e converte o resultado para decimal
media = float((numero1 + numero2 + numero3) / 3)

#tanto faz aspas simples como aspas duplas
#a funão str converte string, no nosso caso inteiro para string
print(
    'A média dos números ' + str(numero1) + 
    ', ' + str(numero2) + ', ' + str(numero3) + ' é ' + str(media)
    )