from Instruccion import Instruccion


import Gramatica as g
import TablaSimbolo as TS
import math
from Expresion import *
from Instruccion import *
import Error as err
import subprocess



class Traducir:
    def __init__(self, Instruccion, ts):
        self.instruccion = Instruccion
        self.ts = ts
        self.salida = ''
        self.indice_temporal = 0
        self.indice_heap = 0
        self.indice_stack = 0
        self.main = {}
        self.funciones = {}
        self.structs = {}



    def traducir(self,instruccion):
        self.salida = 'package main'+' \n'+ 'import(\"fmt\") \nvar STACK [30000]float64  \nvar HEAP [300000]float64  \nvar P,H float64'
        self.recolectar(instruccion)

    def recolectar(self, instruccion):
        print('a')


    def procesar_instrucciones(self,instruccion,ts):
        print('hola')
        
        print(self.salida)