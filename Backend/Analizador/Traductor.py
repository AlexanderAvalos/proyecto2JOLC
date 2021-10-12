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
        self.indice_if = 0
        
    def agregar_token(self,id,temporal,linea):
        self.pila.append({"id":id, "valor":temporal, "ambito":self.ambito_ejecucion, "linea": linea})

    def imprimir3D(self):
        for etiqueta in self.etiquetas:
            self.salida +=  etiqueta + ': \n'
            for cuadruplo in self.etiquetas[etiqueta]:
                if cuadruplo.operador == "if":
                    self.salida += "  if ({0})  goto {1};".format(cuadruplo.arg1, cuadruplo.resultado) + "\n"
                elif cuadruplo.operador == "print":
                    self.salida += "  fmt.printf(\"{0}\",{1});".format(cuadruplo.arg2,cuadruplo.arg1) + "\n"
                elif cuadruplo.operador == "goto":
                    self.salida += "  goto {0};".format(cuadruplo.resultado) + "\n"
                elif cuadruplo.operador == "etiqueta":
                    self.salida += "  {0}:".format(cuadruplo.resultado) + "\n"
                elif cuadruplo.operador != "=":
                    self.salida += "  {0} = {1} {2} {3};".format(cuadruplo.resultado,cuadruplo.arg1,cuadruplo.operador,cuadruplo.arg2) + "\n"
                else:
                    self.salida += "  {0} = {1} {2};".format(cuadruplo.resultado,cuadruplo.arg1,cuadruplo.arg2) + "\n"
        self.salida += "\n"

    def traducir(self,instruccion):
        self.salida = 'package main'+' \n'+ 'import(\"fmt\") \nvar stack [30000]float64  \nvar heap [300000]float64  \nvar P,H float64\n'
        self.recolectar(instruccion)
        self.salida = self.salida +  str(self.imprimir_temporales())
        self.imprimir3D()
        print(self.salida)

    def imprimir_temporales(self):
        temporales = 'var '
        for indiceaux in range(0,self.indice_temporal):
            if self.indice_temporal > 0 and indiceaux < (self.indice_temporal -1):
                temporales += 't'+str(indiceaux)+', '
            else: 
                temporales += 't' + str(indiceaux) +' '
        temporales = temporales +  'float64 \n'
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
            temp = self.generarstack()
            simbolo = TS.Simbolo(instruccion.id,temp , instruccion.tipo, instruccion.ambiente, instruccion.linea, instruccion.columna)
            ts.agregar(simbolo)
            self.agregar_token(instruccion.id,temp,instruccion.linea)
            nuevo_cuadruplo = TS.Cuadruplo(temp,last_temp,"", "=")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        else:
            last_temp = self.procesar_operacion(instruccion.valor,ts)
            temp = ts.get(instruccion.id,ts).valor
            tempaux = self.regresarstack(temp)
            nuevo_cuadruplo = TS.Cuadruplo(tempaux,last_temp,"", "=")
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
        if operacion.operacion != '/' and operacion.operacion != '^' :
            op1 = self.procesar_operacion(operacion.opIzq, ts)
            op2 = self.procesar_operacion(operacion.opDer, ts)
            operador = operacion.operacion
            temp = self.generar_temporal()
            nuevo_cuadruplo = TS.Cuadruplo(temp,op1,op2,operador)
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
            return temp
        else:
            if operacion.operacion == '/':
                op1 = self.procesar_operacion(operacion.opIzq, ts)
                op2 = self.procesar_operacion(operacion.opDer, ts)
                operador = operacion.operacion
                #operador1
                tempop1 = self.generar_temporal()
                nuevo_cuadruplop1 = TS.Cuadruplo(tempop1,op1,"","=")
                self.cuadruplos.agregar(nuevo_cuadruplop1)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplop1)
                #operador 2
                tempop2 = self.generar_temporal()
                nuevo_cuadruplop2 = TS.Cuadruplo(tempop2,op2,"","=")  
                self.cuadruplos.agregar(nuevo_cuadruplop2)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplop2)
                #if
                nueva_etiqueta = self.generar_etiqueta()
                nuevo_cuadruploIf = TS.Cuadruplo(nueva_etiqueta,"{0}!= 0".format(tempop2),"goto","if")
                self.cuadruplos.agregar(nuevo_cuadruploIf)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploIf)
                #intrucciones
                nuevo_cuadruploError = TS.Cuadruplo(" ","77","%c","print")
                self.cuadruplos.agregar(nuevo_cuadruploError)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                nuevo_cuadruploError = TS.Cuadruplo(" ","97","%c","print")
                self.cuadruplos.agregar(nuevo_cuadruploError)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                nuevo_cuadruploError = TS.Cuadruplo(" ","116","%c","print")
                self.cuadruplos.agregar(nuevo_cuadruploError)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                nuevo_cuadruploError = TS.Cuadruplo(" ","104","%c","print")
                self.cuadruplos.agregar(nuevo_cuadruploError)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                nuevo_cuadruploError = TS.Cuadruplo(" ","69","%c","print")
                self.cuadruplos.agregar(nuevo_cuadruploError)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                nuevo_cuadruploError = TS.Cuadruplo(" ","114","%c","print")
                self.cuadruplos.agregar(nuevo_cuadruploError)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                nuevo_cuadruploError = TS.Cuadruplo(" ","114","%c","print")
                self.cuadruplos.agregar(nuevo_cuadruploError)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                nuevo_cuadruploError = TS.Cuadruplo(" ","111","%c","print")
                self.cuadruplos.agregar(nuevo_cuadruploError)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                nuevo_cuadruploError = TS.Cuadruplo(" ","114","%c","print")
                self.cuadruplos.agregar(nuevo_cuadruploError)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                temp = self.generar_temporal()
                nuevo_cuadruplo = TS.Cuadruplo(temp,"0","","")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                #goto
                nueva_etiqueta2 = self.generar_etiqueta()
                nuevo_cuadruplogoto = TS.Cuadruplo(nueva_etiqueta2,"","","goto")
                self.cuadruplos.agregar(nuevo_cuadruplogoto)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
                #etiqueta1
                nuevo_cuadruploeti = TS.Cuadruplo(nueva_etiqueta,"","","etiqueta")
                self.cuadruplos.agregar(nuevo_cuadruploeti)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)
                nuevo_cuadruplo = TS.Cuadruplo(temp,op1,op2,operador)
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                #etiqueta2
                nuevo_cuadruploeti2 = TS.Cuadruplo(nueva_etiqueta2,"","","etiqueta")
                self.cuadruplos.agregar(nuevo_cuadruploeti2)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti2)
                return temp
            else:
                self.generar_potencia(operacion.opIzq,operacion.opDer,ts)

    def generar_potencia(self,operador1,operador2,ts):
        op1 = self.procesar_valor(operador1,ts)
        op2 = self.procesar_valor(operador2,ts)
        cont = 0
        if op2 == 0: 
            print("temporal",cont," = 1" )
            print("temporal",cont)
        elif op2 == 1:
            print("temporal",cont," = ",op1)
            print("temporal",cont)
        elif op2 == 2:
            print("temporal",cont," = ",op1, " * ", op1 )
            print("temporal",cont)
        elif op2 > 2:
                print("temporaln 1 = ",op1, " * ", op1 )
                for num in range(2,op2):
                    print("temporaln",num, "= temporaln",num-1 ,"*", op1)
                    cont = num
                print("temporal",cont)

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

    def generarstack(self):
        salida = "P = {0} ;".format(self.indice_heap)
        salida += "\n  stack[int(P)]"
        self.indice_heap += 1
        return salida
    
    def regresarstack(self,inicio):
        aux = self.indice_heap - 1
        aux2 = inicio.split(sep = " ")
        ret = self.contardif(aux,aux2[2])
        salida = "P = P - " + str(ret) + ";"
        salida += "\n  stack[int(P)]"
        return salida
    
    def contardif(self,inicio,fin):
        cont = 0
        ini = int(inicio)
        print(ini, " ", fin)
        while(int(ini) != int(fin)):
            ini -= 1
            cont += 1
        return cont

    def generar_etiqueta(self):
        salida = "L{0}".format(self.indice_etiquetas)
        self.indice_etiquetas += 1
        return salida

    def generar_if(self):
        salida = "if{0}".format(self.indice_if)
        self.indice_if += 1
        return salida
