from os import sep
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
        self.indice_etiquetas = 0
        self.indice_heap = 0
        self.indice_stack = 0
        self.pila = []
        self.cuadruplos = TS.Cuadruplos()
        self.etiquetas = {}
        self.etiqueta = "main"
        self.ambito_ejecucion = "global"
        
        
    def agregar_token(self,id,temporal,linea):
        self.pila.append({"id":id, "valor":temporal, "ambito":self.ambito_ejecucion, "linea": linea})

    def imprimir3D(self):
        for etiqueta in self.etiquetas:
            self.salida += "\nfunc " + etiqueta + " () {\n" 
            for cuadruplo in self.etiquetas[etiqueta]:
                if cuadruplo.operador != "=":
                    self.salida += "{0} = {1} {2} {3};".format(cuadruplo.resultado,cuadruplo.arg1,cuadruplo.operador,cuadruplo.arg2) + "\n"
                else:
                    self.salida += "{0} = {1} {2};".format(cuadruplo.resultado,cuadruplo.arg1,cuadruplo.arg2) + "\n"
        self.salida += "}\n"

    def traducir(self,instruccion):
        self.salida = 'package main'+' \n'+ 'import(\"fmt\") \nvar stack [30000]float64  \nvar heap [300000]float64  \nvar P,H float64\n'
        self.recolectar(instruccion)
        self.salida = self.salida +  str(self.imprimir_temporales())
        self.imprimir3D()
        print(self.salida)

    def imprimir_temporales(self):
        temporales = 'var '
        for indiceaux in range(0,self.indice_temporal):
            if self.indice_temporal > 0 or indiceaux < (self.indice_temporal -1):
                temporales += 't'+str(indiceaux)+', '
            else: 
                temporales += 't' + str(indiceaux) +' '
        temporales = temporales +  'float64'
        return temporales

    def recolectar(self, instruccion):
        if not isinstance(instruccion, StructsIn) or not isinstance(instruccion, Funcion):
            self.etiquetas["main"] = []
            for instr in instruccion:
                if isinstance(instr, Declaracion): self.recolectar_declaracion(instr,self.ts)
        else: 
            print('funciones y structs')
    
    def recolectar_declaracion(self,instruccion,ts):
        if ts.verificar(instruccion.id, ts) == False:
            last_temp = self.procesar_operacion(instruccion.valor,ts)
            temp = self.generarHeap()
            simbolo = TS.Simbolo(instruccion.id,temp , instruccion.tipo, instruccion.ambiente, instruccion.linea, instruccion.columna)
            ts.agregar(simbolo)
            self.agregar_token(instruccion.id,temp,instruccion.linea)
            nuevo_cuadruplo = TS.Cuadruplo(temp,last_temp," ", "=")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        else:
            last_temp = self.procesar_operacion(instruccion.valor,ts)
            temp = ts.get(instruccion.id,ts).valor
            tempaux = self.regresarHeap(temp)
            nuevo_cuadruplo = TS.Cuadruplo(tempaux,last_temp," ", "=")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)

    def procesar_operacion(self,operacion,ts):
        if isinstance(operacion, OperacionBinaria):
            return self.procesar_operacionBinaria(operacion,ts)
        elif isinstance(operacion, OperacionVariable):
            return self.procesar_valor(operacion,ts)
        elif isinstance(operacion, OperacionNumero):
            return self.procesar_valor(operacion,ts)
        elif isinstance(operacion, OperacionCadena):
            return self.procesar_valor(operacion,ts)
        elif isinstance(operacion, OperacionCaracter):
            return self.procesar_valor(operacion,ts)
        elif isinstance(operacion, OperacionBooleana):
            return self.procesar_valor(operacion,ts)

    def procesar_operacionBinaria(self,operacion,ts):
        op1 = self.procesar_operacion(operacion.opIzq, ts)
        op2 = self.procesar_operacion(operacion.opDer, ts)
        operador = operacion.operacion
        temp = self.generar_temporal()
        nuevo_cuadruplo = TS.Cuadruplo(temp,op1,op2,operador)
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        return temp

    def procesar_valor(self,expresion,ts):
        if isinstance(expresion,OperacionVariable):
            if ts.existepadre(expresion.id,ts):     
                valor = ts.get(expresion.id,ts)
                if "[" in valor.valor:
                    temp = self.generar_temporal()
                    nuevo_cuadrupo = TS.Cuadruplo(temp,valor.valor,"","=")
                    self.cuadruplos.agregar(nuevo_cuadrupo)
                    self.etiqueta[self.etiqueta].append(nuevo_cuadrupo)
                    return temp
                return valor.valor
        else:
            return expresion.val

    def generar_temporal(self):
        salida = "t{0}".format(self.indice_temporal)
        self.indice_temporal += 1
        return salida

    def generarHeap(self):
        salida = "P = {0} ;".format(self.indice_heap)
        salida += "\nheap[int(P)]"
        self.indice_heap += 1
        return salida
    
    def regresarHeap(self,inicio):
        aux = self.indice_heap - 1
        aux2 = inicio.split(sep = " ")
        ret = self.contardif(aux,aux2[2])
        salida = "P = P - " + str(ret) + ";"
        salida += "\nheap[int(P)]"
        return salida
    
    def contardif(self,inicio,fin):
        cont = 0
        ini = int(inicio)
        print(ini, " ", fin)
        while(int(ini) != int(fin)):
            ini -= 1
            cont += 1
        return cont