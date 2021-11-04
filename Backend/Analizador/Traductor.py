from enum import Flag
from os import sep, truncate
from Instruccion import Instruccion
import Gramatica as g
import TablaSimbolo as TS
from Expresion import *
from Instruccion import *
import Error as err
from Estructura_Funcion import *
 
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
        self.imp_cadena = False
        self.generarmulti = 0
        self.is_string = False
        self.continueaux = ""
        self.breakaux = ""
        self.lst_funcion = []
        self.ope_return = ""
        self.contadoraux = 0
        self.is_arreglo = False
        self.is_condicion = False
        self.contadorultimo = 0
        self.contaux = 0
        self.activo = False
        self.tempreturn = ''
        self.is_math = False
        self.iscontinue = False
        self.isbreak = False

    def agregar_token(self,id,temporal,linea):
        self.pila.append({"id":id, "valor":temporal, "ambito":self.ambito_ejecucion, "linea": linea})

    def imprimir3D(self):
        for etiqueta in self.etiquetas:
            self.salida +=  "func "+etiqueta + '(){ \n'
            for cuadruplo in self.etiquetas[etiqueta]:
                if cuadruplo.operador == "if":
                    self.salida += "  if ({0})  ".format(cuadruplo.arg1)+"{" +" goto {0}; ".format( cuadruplo.resultado) +"}"+ "\n"
                elif cuadruplo.operador == "print":
                    self.salida += "  fmt.Printf(\"{0}\",{1});".format(cuadruplo.arg2,cuadruplo.arg1) + "\n"
                elif cuadruplo.operador == "goto":
                    self.salida += "  goto {0};".format(cuadruplo.resultado) + "\n"
                elif cuadruplo.operador == "etiqueta":
                    self.salida += "  {0}:".format(cuadruplo.resultado) + "\n"
                elif cuadruplo.operador == "metodo":
                    self.salida += "  {0}".format(cuadruplo.resultado) + "\n"
                elif cuadruplo.operador == "return":
                    self.salida += "  {0};".format(cuadruplo.resultado) + "\n"
                elif cuadruplo.operador != "=":
                    self.salida += "  {0} = {1} {2} {3};".format(cuadruplo.resultado,cuadruplo.arg1,cuadruplo.operador,cuadruplo.arg2) + "\n"
                else:
                    self.salida += "  {0} = {1} {2};".format(cuadruplo.resultado,cuadruplo.arg1,cuadruplo.arg2) + "\n"
            self.salida += "}\n"

    def traducir(self,instruccion):
        self.salida = 'package main;'+' \n'+ 'import(\"fmt\");'
        self.recolectar(instruccion)
        if self.is_math:
            self.salida += "\nimport(\"math\");"   
        self.salida += "\nvar stack [30101999]float64;  \nvar heap [30101999]float64;  \nvar P,H float64;\n"
        self.salida = self.salida +  str(self.imprimir_temporales())
        self.imprimir3D()

    def imprimir_temporales(self):
        temporales = 'var '
        for indiceaux in range(0,self.indice_temporal):
            if self.indice_temporal > 0 and indiceaux < (self.indice_temporal -1):
                temporales += 't'+str(indiceaux)+', '
            else: 
                temporales += 't' + str(indiceaux) +' '
        temporales = temporales +  'float64; \n'
        return temporales

#metodo recoletar 
    def recolectar(self, instruccion):
            self.etiquetas["main"] = []
            for instr in instruccion:
                if isinstance(instr, Declaracion): self.recolectar_declaracion(instr,self.ts)
                elif isinstance(instr,Funcion): self.recolectar_funcion(instr,self.ts)
                elif isinstance(instr,Printval): self.procesar_impresion(instr,self.ts)
                elif isinstance(instr,If): self.procesar_if(instr,self.ts)
                elif isinstance(instr,While): self.procesar_while(instr,self.ts)
                elif isinstance(instr,For): self.procesar_for(instr,self.ts) 
                elif isinstance(instr,SentenciaContinue): self.procesar_continue(instruccion,self.ts)
                elif isinstance(instr,llamada): self.procesar_llamada(instr,self.ts)
                elif isinstance(instr,DeclaracionArreglos): self.procesar_arreglo(instr,self.ts) 
#instrucciones

#declaracion
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
            nuevo_cuadruplo = TS.Cuadruplo(temp,last_temp,"", "=")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)

#impresion falta impresion arreglos
    def procesar_impresion(self,instruccion, ts):
        valor = instruccion.val
        if(instruccion.tipo == ['print'] ):
            for val in valor:
                op1 = self.procesar_operacion(val,ts)
                if isinstance(val,OperacionVariable):
                    if self.is_string:
                        nuevo_cuadruploError = TS.Cuadruplo("generarprint();","","","metodo")
                        self.cuadruplos.agregar(nuevo_cuadruploError)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                        self.generarImpresion()
                    else:
                        if self.is_arreglo:
                            nuevo_cuadruploError = TS.Cuadruplo("generar_imparreglo();","","","metodo")
                            self.cuadruplos.agregar(nuevo_cuadruploError)
                            self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                            self.generar_impresionArreglo()
                            self.is_arreglo = False
                        else:
                            nuevo_cuadruploError = TS.Cuadruplo(" ",op1,"%"+"f","print")
                            self.cuadruplos.agregar(nuevo_cuadruploError)
                            self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                    
                elif isinstance(val,OperacionCadena) or isinstance(val,OperacionCaracter):
                    stack = self.generarstack()
                    nuevo_cuadruploError = TS.Cuadruplo(stack,op1,"","=")
                    self.cuadruplos.agregar(nuevo_cuadruploError)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                    nuevo_cuadruploError = TS.Cuadruplo("generarprint();","","","metodo")
                    self.cuadruplos.agregar(nuevo_cuadruploError)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                    self.generarImpresion()
                elif isinstance(val,OperacionNumero):
                    if isinstance(op1,int):
                        nuevo_cuadruploError = TS.Cuadruplo(" ","int({0})".format(op1),"%"+"d","print")
                        self.cuadruplos.agregar(nuevo_cuadruploError)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                    elif isinstance(op1,float):
                        nuevo_cuadruploError = TS.Cuadruplo(" ",op1,"%"+"f","print")
                        self.cuadruplos.agregar(nuevo_cuadruploError)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                else:
                    if self.imp_cadena:
                        nuevo_cuadruploError = TS.Cuadruplo("generarprint();","","","metodo")
                        self.cuadruplos.agregar(nuevo_cuadruploError)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                        self.generarImpresion()
                        self.imp_cadena = False
                    else: 
                        nuevo_cuadruploError = TS.Cuadruplo(" ",op1,"%"+"f","print")
                        self.cuadruplos.agregar(nuevo_cuadruploError)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
        elif  instruccion.tipo == ['println']:
            for val in valor:
                op1 = self.procesar_operacion(val,ts)
                if isinstance(val,OperacionVariable):
                    if self.is_string:
                        nuevo_cuadruploError = TS.Cuadruplo("generarprint();","","","metodo")
                        self.cuadruplos.agregar(nuevo_cuadruploError)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                        self.generarImpresion()
                    else:
                        if self.is_arreglo:
                            nuevo_cuadruploError = TS.Cuadruplo("generar_imparreglo();","","","metodo")
                            self.cuadruplos.agregar(nuevo_cuadruploError)
                            self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                            self.generar_impresionArreglo()
                            self.is_arreglo = False
                        else:
                            nuevo_cuadruploError = TS.Cuadruplo(" ",op1,"%"+"f","print")
                            self.cuadruplos.agregar(nuevo_cuadruploError)
                            self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                    
                elif isinstance(val,OperacionCadena) or isinstance(val,OperacionCaracter):
                    stack = self.generarstack()
                    nuevo_cuadruploError = TS.Cuadruplo(stack,op1,"","=")
                    self.cuadruplos.agregar(nuevo_cuadruploError)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                    nuevo_cuadruploError = TS.Cuadruplo("generarprint();","","","metodo")
                    self.cuadruplos.agregar(nuevo_cuadruploError)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                    self.generarImpresion()
                elif isinstance(val,OperacionNumero):
                    if isinstance(op1,int):
                        nuevo_cuadruploError = TS.Cuadruplo(" ","int({0})".format(op1),"%"+"d","print")
                        self.cuadruplos.agregar(nuevo_cuadruploError)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                    elif isinstance(op1,float):
                        nuevo_cuadruploError = TS.Cuadruplo(" ",op1,"%"+"f","print")
                        self.cuadruplos.agregar(nuevo_cuadruploError)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                else:
                    if self.imp_cadena:
                        nuevo_cuadruploError = TS.Cuadruplo("generarprint();","","","metodo")
                        self.cuadruplos.agregar(nuevo_cuadruploError)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
                        self.generarImpresion()
                        self.imp_cadena = False
                    else: 
                        nuevo_cuadruploError = TS.Cuadruplo(" ",op1,"%"+"f","print")
                        self.cuadruplos.agregar(nuevo_cuadruploError)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadruploError)
            nuevo_cuadruploError = TS.Cuadruplo(" ",10,"%"+"c","print")
            self.cuadruplos.agregar(nuevo_cuadruploError)
            self.etiquetas[self.etiqueta].append(nuevo_cuadruploError) 
        else: 
            print('error')

#metodo para imprimir
    def generarImpresion(self):
        self.etiquetas["generarprint"] = []
        temp = self.generar_temporal()
        nuevo_cuadruplo = TS.Cuadruplo(temp,"stack[int(P)]","","=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas["generarprint"].append(nuevo_cuadruplo)
        etiqueta = self.generar_etiqueta()
        nuevo_cuadruplo = TS.Cuadruplo(etiqueta,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas["generarprint"].append(nuevo_cuadruplo)
        temp2 = self.generar_temporal()
        nuevo_cuadruplo = TS.Cuadruplo(temp2,"heap[int({0})]".format(temp),"","=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas["generarprint"].append(nuevo_cuadruplo)
        self.generar_if()
        etiquetaif= self.generar_etiqueta()
        nuevo_cuadruploelif = TS.Cuadruplo(etiquetaif,"{0} == -1".format(temp2),"","if")
        self.cuadruplos.agregar(nuevo_cuadruploelif)
        self.etiquetas["generarprint"].append(nuevo_cuadruploelif)
        nuevo_cuadruploError = TS.Cuadruplo(" ","int({})".format(temp2),"%"+"c","print")
        self.cuadruplos.agregar(nuevo_cuadruploError)
        self.etiquetas["generarprint"].append(nuevo_cuadruploError)
        nuevo_cuadruplo = TS.Cuadruplo(temp,temp,"1","+")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas["generarprint"].append(nuevo_cuadruplo)
        nuevo_cuadruplogoto = TS.Cuadruplo(etiqueta,"","","goto")
        self.cuadruplos.agregar(nuevo_cuadruplogoto)
        self.etiquetas["generarprint"].append(nuevo_cuadruplogoto)
        nuevo_cuadruplo = TS.Cuadruplo(etiquetaif,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas["generarprint"].append(nuevo_cuadruplo)
        nuevo_cuadruplo = TS.Cuadruplo("return","","","return")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas["generarprint"].append(nuevo_cuadruplo)

#metodo para imprimir arreglos falta

    def generar_impresionArreglo(self):
        self.etiquetas["generar_imparreglo"] = []
        'a'

#if 
    def procesar_if(self,instruccion,ts):
        s_if = instruccion.s_if
        s_else = instruccion.s_else
        s_elif = instruccion.s_elif
        
        #entra al if
        nueva_etiqueta = self.generar_etiqueta()
        self.is_condicion = True
        last_temp = self.procesar_operacion(s_if.condicion, ts)
        
        self.is_condicion = False
        if last_temp.operacion != '||' or last_temp.operacion != '&&':
            if isinstance(last_temp.opIzq,OperacionBinaria) or isinstance(last_temp.opIzq,OperacionUnaria) and isinstance(last_temp.opDer,OperacionBinaria) or isinstance(last_temp.opDer,OperacionUnaria):
                nueva_etiqueta = self.generar_ifs(last_temp,nueva_etiqueta,ts)
            else:
                op1 = self.procesar_operacion(last_temp.opIzq, ts)
                op2 = self.procesar_operacion(last_temp.opDer, ts)
                nuevo_cuadruplo = TS.Cuadruplo(nueva_etiqueta,"{0} {1} {2}".format(op1,last_temp.operacion,op2),"","if")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
            
        #generamos else if
        self.contadoraux = 0
        self.contadorultimo = 0
        contador = []
        if s_elif:
            for s_if2 in s_elif:
                self.is_condicion = True
                last_temp = self.procesar_operacion(s_if2.condicion,ts)
                self.is_condicion = False
                nueva_etiquetaelif = self.generar_etiqueta()
                if last_temp.operacion != '||' or last_temp.operacion != '&&':
                    if isinstance(last_temp.opIzq,OperacionBinaria) or isinstance(last_temp.opIzq,OperacionUnaria) and isinstance(last_temp.opDer,OperacionBinaria) or isinstance(last_temp.opDer,OperacionUnaria):
                        nueva_etiquetaelif = self.generar_ifs(last_temp,nueva_etiquetaelif,ts)
                    else:
                        op1 = self.procesar_operacion(last_temp.opIzq, ts)
                        op2 = self.procesar_operacion(last_temp.opDer, ts)
                        nuevo_cuadruplo = TS.Cuadruplo(nueva_etiquetaelif,"{0} {1} {2}".format(op1,last_temp.operacion,op2),"","if")
                        self.cuadruplos.agregar(nuevo_cuadruplo)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                contador.append(nueva_etiquetaelif)
        #generamos else
        self.contadoraux = 0
        self.contadorultimo = 0
        if s_else:
            self.procesar_sentencias(s_else.sentencias,ts)
        #generamos etiqueta de salida
        nueva_etiqueta2 = self.generar_etiqueta()
        nuevo_cuadruplogoto = TS.Cuadruplo(nueva_etiqueta2,"","","goto")
        self.cuadruplos.agregar(nuevo_cuadruplogoto)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
        nuevo_cuadruploeti = TS.Cuadruplo(nueva_etiqueta,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruploeti)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)
        self.procesar_sentencias(s_if.sentencias,ts)
        if not self.iscontinue and not self.isbreak:
            nuevo_cuadruplogoto2 = TS.Cuadruplo(nueva_etiqueta2,"","","goto")
            self.cuadruplos.agregar(nuevo_cuadruplogoto2)
            self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto2)
            self.iscontinue = False
            self.isbreak = False

        if s_elif:
            con =0
            for s_if2 in s_elif:
                nuevo_cuadruploeti = TS.Cuadruplo(contador[con],"","","etiqueta")
                self.cuadruplos.agregar(nuevo_cuadruploeti)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)
                self.procesar_sentencias(s_if2.sentencias,ts)
                if not self.iscontinue and not self.isbreak:
                    nuevo_cuadruplogoto2 = TS.Cuadruplo(nueva_etiqueta2,"","","goto")
                    self.cuadruplos.agregar(nuevo_cuadruplogoto2)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto2)
                    self.iscontinue = False
                    self.isbreak = False
                    con += 1
        nuevo_cuadruplosali = TS.Cuadruplo(nueva_etiqueta2,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruplosali)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplosali)

#metodo para generar && y ||
    def generar_ifs(self,operacion,etiqueta,ts):
        last_temp = operacion
        if self.activo == False:
            self.verificarifs(last_temp,ts)
            self.activo = True
        if last_temp.operacion == '||':
                nueva_etiqueta = self.generar_etiqueta()
                self.is_condicion = True
                op1 = self.procesar_operacion(last_temp.opIzq, ts)
                self.is_condicion = False
                if op1.operacion == '||' or op1.operacion == '&&':
                    nueva_etiqueta = self.generar_ifs(op1,nueva_etiqueta,ts)
                if op1.operacion != '||' and op1.operacion != '&&' :
                    op1aux = self.procesar_operacion(op1.opIzq, ts)
                    op2aux = self.procesar_operacion(op1.opDer, ts)
                    nuevo_cuadruplo = TS.Cuadruplo(nueva_etiqueta,"{0} {1} {2}".format(op1aux,op1.operacion,op2aux),"","if")
                    self.cuadruplos.agregar(nuevo_cuadruplo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                    self.contaux+=1

                self.is_condicion = True
                op2 = self.procesar_operacion(last_temp.opDer, ts)
                self.is_condicion = False
                if op2.operacion == '||' or op2.operacion == '&&' :
                    nueva_etiqueta = self.generar_ifs(op2,nueva_etiqueta,ts)
                if op2.operacion != '||' and op2.operacion != '&&' : 
                    op1aux = self.procesar_operacion(op2.opIzq, ts)
                    op2aux = self.procesar_operacion(op2.opDer, ts)
                    nuevo_cuadruplo = TS.Cuadruplo(nueva_etiqueta,"{0} {1} {2}".format(op1aux,op2.operacion,op2aux),"","if")
                    self.cuadruplos.agregar(nuevo_cuadruplo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                    self.contaux+=1
        elif last_temp.operacion == '&&':
                nueva_etiqueta = etiqueta
                self.is_condicion = True
                op1 = self.procesar_operacion(last_temp.opIzq, ts)
                self.is_condicion = False
                if op1.operacion == '||' or op1.operacion == '&&':
                    nueva_etiqueta = self.generar_ifs(op1,nueva_etiqueta,ts)
                if op1.operacion != '||' and op1.operacion != '&&':
                    op1aux = self.procesar_operacion(op1.opIzq, ts)
                    op2aux = self.procesar_operacion(op1.opDer, ts)
                    nuevo_cuadruplo = TS.Cuadruplo(nueva_etiqueta,"{0} {1} {2}".format(op1aux,op1.operacion,op2aux),"","if")
                    self.cuadruplos.agregar(nuevo_cuadruplo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                    nuevo_cuadruploeti = TS.Cuadruplo(nueva_etiqueta,"","","etiqueta")
                    self.cuadruplos.agregar(nuevo_cuadruploeti)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)
                    self.contaux+=1
                nueva_etiqueta = self.generar_etiqueta()
                self.is_condicion = True
                op2 = self.procesar_operacion(last_temp.opDer, ts)
                self.is_condicion = False
                if op2.operacion == '||' or op2.operacion == '&&' :
                    self.ultimo = True
                    nueva_etiqueta = self.generar_ifs(op2,nueva_etiqueta,ts)
                if op2.operacion != '||' and op2.operacion != '&&' : 
                    op1aux = self.procesar_operacion(op2.opIzq, ts)
                    op2aux = self.procesar_operacion(op2.opDer, ts)
                    nuevo_cuadruplo = TS.Cuadruplo(nueva_etiqueta,"{0} {1} {2}".format(op1aux,op2.operacion,op2aux),"","if")
                    self.cuadruplos.agregar(nuevo_cuadruplo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                    
                    print(self.contaux, "<",self.contadorultimo)
                    if self.contaux < self.contadorultimo:
                        nuevo_cuadruploeti = TS.Cuadruplo(nueva_etiqueta,"","","etiqueta")
                        self.cuadruplos.agregar(nuevo_cuadruploeti)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)
                        self.contaux+=1
        
        return nueva_etiqueta
        
    def verificarifs(self,operacion,ts):
        last_temp = operacion
        self.contadorultimo +=1

        if last_temp.operacion == '&&':
                self.is_condicion = True
                op1 = self.procesar_operacion(last_temp.opIzq, ts)
                self.is_condicion = False
                if op1.operacion == '||' or op1.operacion == '&&':
                       self.verificarifs(op1,ts)
                self.is_condicion = True
                op2 = self.procesar_operacion(last_temp.opDer, ts)
                self.is_condicion = False
                if op2.operacion == '||' or op2.operacion == '&&' :
                    self.ultimo = True
                    self.verificarifs(op2,ts)

#while
    def procesar_while(self,instruccion,ts):
        nueva_etiquetablucle = self.generar_etiqueta()
        self.continueaux= nueva_etiquetablucle
        nuevo_cuadruploblucle = TS.Cuadruplo(nueva_etiquetablucle,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruploblucle)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruploblucle)
        nueva_etiqueta = self.generar_etiqueta()
        etiquetasalida = self.generar_etiqueta()
        self.breakaux = etiquetasalida
        self.is_condicion = True
        last_temp = self.procesar_operacion(instruccion.condicion, ts)
        self.is_condicion = False
        op1 = self.procesar_operacion(last_temp.opIzq,ts)
        op2 = self.procesar_operacion(last_temp.opDer,ts)
        nuevo_cuadruplo = TS.Cuadruplo(nueva_etiqueta,"{0}{1}{2}".format(op1,last_temp.operacion,op2),"","if")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        
        nuevo_cuadruplogoto = TS.Cuadruplo(etiquetasalida,"","","goto")
        self.cuadruplos.agregar(nuevo_cuadruplogoto)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
        nuevo_cuadruploeti = TS.Cuadruplo(nueva_etiqueta,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruploeti)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)
        self.procesar_sentencias(instruccion.sentencias,ts)
        nuevo_cuadruplogoto = TS.Cuadruplo(nueva_etiquetablucle,"","","goto")
        self.cuadruplos.agregar(nuevo_cuadruplogoto)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
        nuevo_cuadruploeti = TS.Cuadruplo(etiquetasalida,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruploeti)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)  
        
#for faltan las simples
    def procesar_for(self,instruccion,ts):
        condiciones = instruccion.condicional
        if isinstance(instruccion.condicional, condicionalSimple):
            'simple'
        elif isinstance(instruccion.condicional, condicionalRango):
            'rango'
            local = TS.TablaSimbolos()
            local.setPadre(ts)
            stak = self.generarstack()
            simbolo = TS.Simbolo(instruccion.id,stak , "for", "for", instruccion.linea, 0)
            ts.agregar(simbolo)
            self.agregar_token(instruccion.id,stak,instruccion.linea)
            nuevo_cuadruplo = TS.Cuadruplo(stak,0,"", "=")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
    #generamos el temporal
            if isinstance(instruccion.condicional, condicionalSimple):
                'falta'
            elif isinstance(instruccion.condicional,condicionalRango):
                temp = self.generar_temporal()
                valaux = stak.split(sep =" ")
                nuevo_cuadrupo = TS.Cuadruplo(temp,valaux[5],"","=")
                self.cuadruplos.agregar(nuevo_cuadrupo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
        #generamos la etiqueta recursiva
                nueva_etiquetablucle = self.generar_etiqueta()
                self.continueaux= nueva_etiquetablucle
                nuevo_cuadruploblucle = TS.Cuadruplo(nueva_etiquetablucle,"","","etiqueta")
                self.cuadruplos.agregar(nuevo_cuadruploblucle)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploblucle)
        #operamos los rangos
                rangoizq = self.procesar_operacion(condiciones.rangoizq,ts)
                rangoder = self.procesar_operacion(condiciones.rangoder,ts)
        #generamos los ifs condicionales
                nueva_etiqueta = self.generar_etiqueta()
                nuevo_cuadruplo = TS.Cuadruplo(nueva_etiqueta,"{0}>={1}".format(temp,rangoizq),"","if")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                nuevo_cuadruploeti = TS.Cuadruplo(nueva_etiqueta,"","","etiqueta")
                self.cuadruplos.agregar(nuevo_cuadruploeti)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)
                nueva_etiqueta2 = self.generar_etiqueta()
                nuevo_cuadruplo = TS.Cuadruplo(nueva_etiqueta2,"{0}<{1}".format(temp,rangoder),"","if")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        #if salida
                nueva_etiquetasalida = self.generar_etiqueta()
                self.breakaux = nueva_etiquetasalida
                nuevo_cuadruplo = TS.Cuadruplo(nueva_etiquetasalida,"{0}>{1}".format(temp,rangoder),"","if")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        #generamos etiqueta de salida
                nuevo_cuadruplo = TS.Cuadruplo(stak,temp +"+ 1","", "=")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                self.cuadruplos.agregar(nuevo_cuadrupo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                nuevo_cuadruplogoto = TS.Cuadruplo(nueva_etiquetablucle,"","","goto")
                self.cuadruplos.agregar(nuevo_cuadruplogoto)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
        #generamos etiquetas del ciclo
                nuevo_cuadruploeti = TS.Cuadruplo(nueva_etiqueta2,"","","etiqueta")
                self.cuadruplos.agregar(nuevo_cuadruploeti)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)
        #generamos etiqueta de salida
                self.procesar_sentencias(instruccion.sentencias,local)
                nuevo_cuadruplo = TS.Cuadruplo(stak,temp +"+ 1","", "=")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                self.cuadruplos.agregar(nuevo_cuadrupo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                
                nuevo_cuadruploeti = TS.Cuadruplo(nueva_etiquetasalida,"","","etiqueta")
                self.cuadruplos.agregar(nuevo_cuadruploeti)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)

#sentencia continue
    def procesar_continue(self,sentencia, ts):
        if self.continueaux != "":
            nuevo_cuadruplogoto = TS.Cuadruplo(self.continueaux,"","","goto")
            self.cuadruplos.agregar(nuevo_cuadruplogoto)
            self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
            self.continueaux = ""
            self.iscontinue = True

#sentencia break
    def procesar_break(self,sentencia,ts):
        if self.breakaux != "":
            nuevo_cuadruplogoto = TS.Cuadruplo(self.breakaux,"","","goto")
            self.cuadruplos.agregar(nuevo_cuadruplogoto)
            self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
            self.breakaux = ""
            self.isbreak = True
#sentencias 
    def procesar_sentencias(self,sentencias,ts,llamada = False):
        local = None
        if llamada:
            local = ts;
        else:
            local = TS.TablaSimbolos()
            local.setPadre(ts)
        
        for sentencia in sentencias:
            if isinstance(sentencia, Declaracion): self.recolectar_declaracion(sentencia,local)
            elif isinstance(sentencia,Printval): self.procesar_impresion(sentencia,local)
            elif isinstance(sentencia,If): self.procesar_if(sentencia,local)
            elif isinstance(sentencia,While): self.procesar_while(sentencia,local)
            elif isinstance(sentencia,For): self.procesar_for(sentencia,local)
            elif isinstance(sentencia,SentenciaContinue): self.procesar_continue(sentencia,local)
            elif isinstance(sentencia,SentenciaBreak): self.procesar_break(sentencia,local)
            elif isinstance(sentencia,SentenciaReturn): self.procesar_return(sentencia,local)
            elif isinstance(sentencia,DeclaracionArreglos): self.procesar_arreglo(sentencia,self.ts) 

#funciones
    def recolectar_funcion(self,instruccion,ts):
        self.generar_funcion(instruccion,ts)

#llamada
    def procesar_llamada(self,instruccion,ts):
        tablalocal = TS.TablaSimbolos()
        tablalocal.setPadre(ts)
        cont = 0
        indice_inicia = ""
        parametros = instruccion.parametros
        if parametros  != None:
            for parametro in parametros:
                last_temp = self.procesar_operacion(parametro,ts)
                stack = self.generarstack()
                nuevo_cuadruplogoto = TS.Cuadruplo(stack,last_temp,"","=")
                self.cuadruplos.agregar(nuevo_cuadruplogoto)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
                if cont == 0 : 
                    indice_inicia = stack
                    cont += 1
        if indice_inicia != "":
            aux = indice_inicia.split(sep = " ")
            nuevo_cuadruplogoto = TS.Cuadruplo("P",aux[2],"","=")
            self.cuadruplos.agregar(nuevo_cuadruplogoto)
            self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)   
        nuevo_cuadruplogoto = TS.Cuadruplo(instruccion.idfuncion+"();","","","metodo")
        self.cuadruplos.agregar(nuevo_cuadruplogoto)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
        if self.ope_return != "":
            op1 = self.procesar_operacion(self.ope_return,tablalocal)
            return op1

#metodo para generar funciones  normales 
    def generar_funcion(self,instruccion,ts):
        old_etiqueta = self.etiqueta
        self.etiqueta = instruccion.idFuncion 
        self.etiquetas[self.etiqueta] = []
        cont = 0
        if len(instruccion.parametros) > 0 :
            valaux = []
            for parame in instruccion.parametros:
                temp = self.generar_temporal()
                if cont == 0:
                    nuevo_cuadruplogoto = TS.Cuadruplo(temp,"stack[int(P)]","","=")
                    self.cuadruplos.agregar(nuevo_cuadruplogoto)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
                    cont += 1
                else : 
                    nuevo_cuadruplogoto = TS.Cuadruplo("P","P","1","+")
                    self.cuadruplos.agregar(nuevo_cuadruplogoto)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
                    nuevo_cuadruplogoto = TS.Cuadruplo(temp,"stack[int(P)]","","=")
                    self.cuadruplos.agregar(nuevo_cuadruplogoto)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
                valaux.append(temp)
            conta= 0
            for parame in instruccion.parametros:
                temp2 = self.generarstack()
                simbolo = TS.Simbolo(parame.idparametro,temp2 , parame.tipo, id, parame.linea, parame.columna)
                ts.agregar(simbolo)
                self.agregar_token(parame.idparametro,valaux[conta],parame.linea)
                nuevo_cuadruplo = TS.Cuadruplo(temp2,valaux[conta],"", "=")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                conta +=1

        self.procesar_sentencias(instruccion.sentencias,ts,True)
        self.etiqueta = old_etiqueta

#sentencia return revisa cuando es recursiva 
    def procesar_return(self, sentencia,ts):
        self.ope_return = sentencia.operacion
        nuevo_cuadruplo = TS.Cuadruplo("return","","","return")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        
#arregos 

    def procesar_arreglo(self,instruccion, ts):
        valaux = []
        for valor in instruccion.lista:
            if  isinstance(valor,OperacionArreglo): 
                op1 = self.procesar_operacion(valor,ts)
                valaux.append(op1)

        temp = self.generar_temporal()
        nuevo_cuadruplo = TS.Cuadruplo(temp,"","H","=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        heap = self.generar_heap()
        nuevo_cuadruplo = TS.Cuadruplo(heap,len(instruccion.lista),"","=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        nuevo_cuadruplo = TS.Cuadruplo("H","H","1","+")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        cont = 0
        for valor in instruccion.lista:
            if not isinstance(valor,OperacionArreglo): 
                op1 = self.procesar_operacion(valor,ts)
                heap = self.generar_heap()
                nuevo_cuadruplo = TS.Cuadruplo(heap,op1,"","=")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                nuevo_cuadruplo = TS.Cuadruplo("H","H","1","+")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
            else:
                heap = self.generar_heap()
                nuevo_cuadruplo = TS.Cuadruplo(heap,valaux[cont],"","=")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                nuevo_cuadruplo = TS.Cuadruplo("H","H","1","+")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                cont+=1
            
        stack = self.generarstack()
        nuevo_cuadruplo = TS.Cuadruplo(stack,temp,"","=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        Simbolo = TS.Simbolo(instruccion.id,stack,TIPO_ESTRUCTURAS.ARREGLO,self.etiqueta,instruccion.linea,instruccion.columna)
        ts.agregar(Simbolo)
    
    def verificar_arreglo(self,operacion):
        for val in operacion:
            if isinstance(val,OperacionArreglo ):
                return True
        return False
            
    def procesar_oparreglo(self,operacion,ts):
        
        valaux = []
        for valor in operacion.lstoperacion:
            if  isinstance(valor,OperacionArreglo): 
                op1 = self.procesar_operacion(valor,ts)
                valaux.append(op1)
        temp = self.generar_temporal()
        nuevo_cuadruplo = TS.Cuadruplo(temp,"","H","=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        heap = self.generar_heap()
        nuevo_cuadruplo = TS.Cuadruplo(heap,len(operacion.lstoperacion),"","=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        nuevo_cuadruplo = TS.Cuadruplo("H","H","1","+")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        cont = 0
        for valor in operacion.lstoperacion:
            if not isinstance(valor,OperacionArreglo): 
                op1 = self.procesar_operacion(valor,ts)
                heap = self.generar_heap()
                nuevo_cuadruplo = TS.Cuadruplo(heap,op1,"","=")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                nuevo_cuadruplo = TS.Cuadruplo("H","H","1","+")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
            else:
                heap = self.generar_heap()
                nuevo_cuadruplo = TS.Cuadruplo(heap,valaux[cont],"","=")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                nuevo_cuadruplo = TS.Cuadruplo("H","H","1","+")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                cont+=1
            
        return temp

#operaciones y valores
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
        elif isinstance(operacion,OperacionUnaria):
            return self.procesar_operacionUnaria(operacion,ts)
        elif isinstance(operacion,llamada):
            return self.procesar_llamada(operacion,ts)
        elif isinstance(operacion,OperacionArreglo): 
            return self.procesar_oparreglo(operacion,ts)
        elif isinstance(operacion,OperacionUPPER):
            'a'
        elif isinstance(operacion,OperacionLOWER):
            'a'
        elif isinstance(operacion,OperacionLenght):
            'a'

    def procesar_operacionUPPER(operacion,ts):
            ''

    def procesar_operacionBinaria(self,operacion,ts):
        if operacion.operacion != '/' and operacion.operacion != '^' and operacion.operacion != '%' and operacion.operacion != '*':
            if self.is_condicion:
                return operacion
            else:
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
            elif operacion.operacion == '%':
                self.is_math = True
                op1 = self.procesar_operacion(operacion.opIzq, ts)
                op2 = self.procesar_operacion(operacion.opDer, ts)
                operador = operacion.operacion
                temp = self.generar_temporal()
                nuevo_cuadruplo = TS.Cuadruplo(temp,"math.Mod({0},{1})".format(op1,op2),"","")
                self.cuadruplos.agregar(nuevo_cuadruplo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                return temp
            elif operacion.operacion == '*':
                if (isinstance(operacion.opIzq, OperacionCadena) or isinstance(operacion.opDer, OperacionCadena)):
                    self.imp_cadena = True
                    local = TS.TablaSimbolos()
                    op1 = self.procesar_operacion(operacion.opIzq, ts)
                    op2 = self.procesar_operacion(operacion.opDer, ts)
                    operador = operacion.operacion
                    #parametro1
                    temp = self.generarstack()
                    simbolo = TS.Simbolo(op1,temp , Tipo.STRING, '', '','')
                    local.agregar(simbolo)
                    self.agregar_token(op1,temp,'')
                    nuevo_cuadruplo = TS.Cuadruplo(temp,op1,"", "=")
                    self.cuadruplos.agregar(nuevo_cuadruplo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                    #parametro2
                    temp = self.generarstack()
                    simbolo = TS.Simbolo(op2,temp , Tipo.STRING, '', '','')
                    local.agregar(simbolo)
                    self.agregar_token(op2,temp,'')
                    nuevo_cuadruplo = TS.Cuadruplo(temp,op2,"", "=")
                    self.cuadruplos.agregar(nuevo_cuadruplo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                    fun = self.generarmulti
                    multi = self.generar_funcionmulti()
                    nuevo_cuadruplo = TS.Cuadruplo(multi,"","", "metodo")
                    self.cuadruplos.agregar(nuevo_cuadruplo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                    tempfin = self.generar_recCadena(local,fun)
                    stack = self.generarstack()
                    nuevo_cuadruplo = TS.Cuadruplo(stack,tempfin,"", "=")
                    self.cuadruplos.agregar(nuevo_cuadruplo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                    return tempfin
                    
                else: 
                    op1 = self.procesar_operacion(operacion.opIzq, ts)
                    op2 = self.procesar_operacion(operacion.opDer, ts)
                    operador = operacion.operacion
                    temp = self.generar_temporal()
                    nuevo_cuadruplo = TS.Cuadruplo(temp,op1,op2,operador)
                    self.cuadruplos.agregar(nuevo_cuadruplo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                    return temp
            elif operacion.operacion == '^':
                if (isinstance(operacion.opIzq, OperacionCadena) or isinstance(operacion.opDer, OperacionCadena)):
                    self.imp_cadena = True
                    op1 = self.procesar_operacion(operacion.opIzq,ts)
                    op2 = self.procesar_operacion(operacion.opDer,ts)
                    stack1 = self.generarstack()
                    stack2 = self.generarstack()
                    nuevo_cuadruplo = TS.Cuadruplo(stack1,op1,'',"=")
                    self.cuadruplos.agregar(nuevo_cuadruplo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                    nuevo_cuadruplo = TS.Cuadruplo(stack2,op2,'',"=")
                    self.cuadruplos.agregar(nuevo_cuadruplo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                    nuevo_cuadruplo = TS.Cuadruplo("generar_elevacion();",'','',"metodo")
                    self.cuadruplos.agregar(nuevo_cuadruplo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
                    if self.tempreturn == "":
                        self.tempreturn = self.generar_potenciaCad()
                        if "[" in self.tempreturn:
                            valaux = self.tempreturn.split(sep =" ")
                            nuevo_cuadrupo = TS.Cuadruplo(valaux[0],valaux[2],"","=")
                            self.cuadruplos.agregar(nuevo_cuadrupo)
                            self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                            temp = self.generar_temporal()
                            nuevo_cuadrupo = TS.Cuadruplo(temp,valaux[5],"","=")
                            self.cuadruplos.agregar(nuevo_cuadrupo)
                            self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                            self.is_string = True
                            return temp
                    else:
                        if "[" in self.tempreturn:
                            valaux = self.tempreturn.split(sep =" ")
                            nuevo_cuadrupo = TS.Cuadruplo(valaux[0],valaux[2],"","=")
                            self.cuadruplos.agregar(nuevo_cuadrupo)
                            self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                            temp = self.generar_temporal()
                            nuevo_cuadrupo = TS.Cuadruplo(temp,valaux[5],"","=")
                            self.cuadruplos.agregar(nuevo_cuadrupo)
                            self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                            self.is_string = True
                            return temp
                    
                else:
                    return self.generar_potencia(operacion.opIzq,operacion.opDer,ts)           
            return None

    def generar_potenciaCad(self):
        old = self.etiqueta
        self.etiqueta = "generar_elevacion"
        self.etiquetas[self.etiqueta] = []
        #parametros
        tempcad= self.generar_temporal()
        nuevo_cuadruplo = TS.Cuadruplo("P","P",'1',"-")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        nuevo_cuadruplo = TS.Cuadruplo(tempcad,"stack[int(P)]",'',"=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        nuevo_cuadruplo = TS.Cuadruplo("P","P",'1',"+")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        tempelev= self.generar_temporal()
        nuevo_cuadruplo = TS.Cuadruplo(tempelev,"stack[int(P)]",'',"=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        #return 
        temp = self.generar_temporal()
        nuevo_cuadruplo = TS.Cuadruplo(temp,"H",'',"=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        ret = self.generarstack()
        nuevo_cuadruplo = TS.Cuadruplo(ret,temp,'',"=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        #incremental elv
        tempincreelev = self.generar_temporal()
        nuevo_cuadruplo = TS.Cuadruplo(tempincreelev,"0",'',"=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        #ciclo de elevacion
        etiquetacicloelev = self.generar_etiqueta()
        nuevo_cuadruplo = TS.Cuadruplo(etiquetacicloelev,"",'',"etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        tempaux = self.generar_temporal()
        nuevo_cuadruplo = TS.Cuadruplo(tempaux,tempcad,'0',"+")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        #primer if
        etiquetaif1 = self.generar_etiqueta()
        nuevo_cuadruplo = TS.Cuadruplo(etiquetaif1,"{0} < {1}".format(tempincreelev,tempelev),'',"if")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        #salida
        etiquetasalida1 = self.generar_etiqueta()
        nuevo_cuadruplo = TS.Cuadruplo(etiquetasalida1,"",'',"goto")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        #ciclo1
        nuevo_cuadruplo = TS.Cuadruplo(etiquetaif1,"",'',"etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        #cliclos para cadenas
        etiqueta = self.generar_etiqueta()
        nuevo_cuadruplo = TS.Cuadruplo(etiqueta,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        temp2 = self.generar_temporal()
        nuevo_cuadruplo = TS.Cuadruplo(temp2,"heap[int({0})]".format(tempaux),"","=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        self.generar_if()
        etiquetaif= self.generar_etiqueta()
        nuevo_cuadruploelif = TS.Cuadruplo(etiquetaif,"{0} == -1".format(temp2),"","if")
        self.cuadruplos.agregar(nuevo_cuadruploelif)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruploelif)
        heapaux = self.generar_heap()
        nuevo_cuadruplo = TS.Cuadruplo(heapaux,temp2,"","=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        nuevo_cuadruplo = TS.Cuadruplo(tempaux,tempaux,"1","+")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        nuevo_cuadruplo = TS.Cuadruplo("H",'H','1',"+")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        nuevo_cuadruplogoto = TS.Cuadruplo(etiqueta,"","","goto")
        self.cuadruplos.agregar(nuevo_cuadruplogoto)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
        nuevo_cuadruplo = TS.Cuadruplo(etiquetaif,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        #fin cliclo de cadena
        nuevo_cuadruplo = TS.Cuadruplo(tempincreelev,tempincreelev,"1","+")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        nuevo_cuadruplogoto = TS.Cuadruplo(etiquetacicloelev,"","","goto")
        self.cuadruplos.agregar(nuevo_cuadruplogoto)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
        #salida
        nuevo_cuadruplo = TS.Cuadruplo(etiquetasalida1,"",'',"etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        heapfin = self.generar_heap()
        nuevo_cuadruplo = TS.Cuadruplo(heapfin,'-1','',"=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        nuevo_cuadruplo = TS.Cuadruplo("H",'H','1',"+")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        nuevo_cuadruplo = TS.Cuadruplo("return","",'',"return")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        #fin
        self.etiqueta = old
        return ret

    def procesar_operacionUnaria(self,operacion,ts):
        op1 = self.procesar_operacion(operacion.op1, ts)
        operador = operacion.operacion
        if operador == OPERACION_NUMERICA.RESTA:
            temp = self.generar_temporal()
            nuevo_cuadruplo = TS.Cuadruplo(temp,"",op1,"-")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
            return temp
        return None

    def generar_recCadena(self, tablalocal,fun):
        etiquetafunc = "generar_multi{0}".format(fun)
        self.etiquetas[etiquetafunc]=[]
        tempfin = self.generar_temporal()
        nuevo_cuadruplo = TS.Cuadruplo(tempfin,"H","","=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[etiquetafunc].append(nuevo_cuadruplo)
        for simbolo in tablalocal.simbolos:
            temp = self.generar_temporal()
            valor = tablalocal.get(simbolo,tablalocal).valor
            valoraux = valor.split(sep = " ")
            nuevo_cuadruplo = TS.Cuadruplo("P",valoraux[2],"", "=")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[etiquetafunc].append(nuevo_cuadruplo)
            nuevo_cuadruplo = TS.Cuadruplo(temp,valoraux[5],"", "=")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[etiquetafunc].append(nuevo_cuadruplo)
            etiqueta = self.generar_etiqueta()
            nuevo_cuadruplo = TS.Cuadruplo(etiqueta,"","","etiqueta")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[etiquetafunc].append(nuevo_cuadruplo)
            temp2 = self.generar_temporal()
            nuevo_cuadruplo = TS.Cuadruplo(temp2,"heap[int({0})]".format(temp),"","=")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[etiquetafunc].append(nuevo_cuadruplo)
            self.generar_if()
            etiquetaif= self.generar_etiqueta()
            nuevo_cuadruploelif = TS.Cuadruplo(etiquetaif,"{0} == -1".format(temp2),"","if")
            self.cuadruplos.agregar(nuevo_cuadruploelif)
            self.etiquetas[etiquetafunc].append(nuevo_cuadruploelif)
            heapaux = self.generar_heap()
            nuevo_cuadruplo = TS.Cuadruplo(heapaux,temp2,"","=")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[etiquetafunc].append(nuevo_cuadruplo)
            nuevo_cuadruplo = TS.Cuadruplo("H","H","1","+")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[etiquetafunc].append(nuevo_cuadruplo)
            nuevo_cuadruplo = TS.Cuadruplo(temp,temp,"1","+")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[etiquetafunc].append(nuevo_cuadruplo)
            nuevo_cuadruplogoto = TS.Cuadruplo(etiqueta,"","","goto")
            self.cuadruplos.agregar(nuevo_cuadruplogoto)
            self.etiquetas[etiquetafunc].append(nuevo_cuadruplogoto)
            nuevo_cuadruplo = TS.Cuadruplo(etiquetaif,"","","etiqueta")
            self.cuadruplos.agregar(nuevo_cuadruplo)
            self.etiquetas[etiquetafunc].append(nuevo_cuadruplo)
        heapaux = self.generar_heap()
        nuevo_cuadruplo = TS.Cuadruplo(heapaux,-1,"","=")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[etiquetafunc].append(nuevo_cuadruplo)
        nuevo_cuadruplo = TS.Cuadruplo("H","H","1","+")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[etiquetafunc].append(nuevo_cuadruplo)
        nuevo_cuadruplo = TS.Cuadruplo("return","","","return")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[etiquetafunc].append(nuevo_cuadruplo)
        return tempfin

    def generar_potencia(self,operador1,operador2,ts):
        op1 = self.procesar_operacion(operador1,ts)
        op2 = self.procesar_operacion(operador2,ts)
        
        temp = self.generar_temporal()
        nuevo_cuadruplop1 = TS.Cuadruplo(temp,0,"","=")
        self.cuadruplos.agregar(nuevo_cuadruplop1)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplop1)
        tempfin = self.generar_temporal()
        nuevo_cuadruplop1 = TS.Cuadruplo(tempfin,1,"","=")
        self.cuadruplos.agregar(nuevo_cuadruplop1)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplop1)
        nueva_etiquetablucle = self.generar_etiqueta()
        nuevo_cuadruploblucle = TS.Cuadruplo(nueva_etiquetablucle,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruploblucle)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruploblucle)
        
        #=0
        nueva_etiqueta1 = self.generar_etiqueta()
        nuevo_cuadruplo = TS.Cuadruplo(nueva_etiqueta1,"{0} == 0".format(op2),"","if")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        
        #=1
        nueva_etiqueta2 = self.generar_etiqueta()
        nuevo_cuadruplo = TS.Cuadruplo(nueva_etiqueta2,"{0} == 1".format(op2),"","if")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        
        #=2
        nueva_etiqueta3 = self.generar_etiqueta()
        nuevo_cuadruplo = TS.Cuadruplo(nueva_etiqueta3,"{0} == 2".format(op2),"","if")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        
        #>2
        nueva_etiqueta4 = self.generar_etiqueta()
        nuevo_cuadruplo = TS.Cuadruplo(nueva_etiqueta4,"{0} < {1}".format(temp,op2),"","if")
        self.cuadruplos.agregar(nuevo_cuadruplo)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplo)
        #goto etiqueta salida
        etiquetasalida= self.generar_etiqueta()
        nuevo_cuadruplogoto = TS.Cuadruplo(etiquetasalida,"","","goto")
        self.cuadruplos.agregar(nuevo_cuadruplogoto)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
        #etiqeutas salidas
        #etiqueta igual 0
        nuevo_cuadruploeti = TS.Cuadruplo(nueva_etiqueta1,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruploeti)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)
        nuevo_cuadruplop1 = TS.Cuadruplo(tempfin,1,"","=")
        self.cuadruplos.agregar(nuevo_cuadruplop1)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplop1)
        nuevo_cuadruplogoto = TS.Cuadruplo(etiquetasalida,"","","goto")
        self.cuadruplos.agregar(nuevo_cuadruplogoto)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
        #etiqueta igual 1
        nuevo_cuadruploeti = TS.Cuadruplo(nueva_etiqueta2,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruploeti)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)

        nuevo_cuadruplop1 = TS.Cuadruplo(tempfin,op1,"","=")
        self.cuadruplos.agregar(nuevo_cuadruplop1)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplop1)
        nuevo_cuadruplogoto = TS.Cuadruplo(etiquetasalida,"","","goto")
        self.cuadruplos.agregar(nuevo_cuadruplogoto)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
        
        #etiqueta igual 2
        nuevo_cuadruploeti = TS.Cuadruplo(nueva_etiqueta3,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruploeti)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)

        nuevo_cuadruplop1 = TS.Cuadruplo(tempfin,op1,op1,"*")
        self.cuadruplos.agregar(nuevo_cuadruplop1)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplop1)
        nuevo_cuadruplogoto = TS.Cuadruplo(etiquetasalida,"","","goto")
        self.cuadruplos.agregar(nuevo_cuadruplogoto)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
        #etiqeuta mayor 2
        nuevo_cuadruploeti = TS.Cuadruplo(nueva_etiqueta4,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruploeti)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)
        nuevo_cuadruplop1 = TS.Cuadruplo(tempfin,tempfin,op1,"*")
        self.cuadruplos.agregar(nuevo_cuadruplop1)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplop1)
        nuevo_cuadruplop1 = TS.Cuadruplo(temp,temp,"1","+")
        self.cuadruplos.agregar(nuevo_cuadruplop1)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplop1)
        nuevo_cuadruplogoto = TS.Cuadruplo(nueva_etiquetablucle,"","","goto")
        self.cuadruplos.agregar(nuevo_cuadruplogoto)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruplogoto)
        #salida
        nuevo_cuadruploeti = TS.Cuadruplo(etiquetasalida,"","","etiqueta")
        self.cuadruplos.agregar(nuevo_cuadruploeti)
        self.etiquetas[self.etiqueta].append(nuevo_cuadruploeti)
        return tempfin

    def procesar_valor(self,expresion,ts):
        if isinstance(expresion,OperacionVariable):
            if ts.existepadre(expresion.id,ts):     
                valor = ts.get(expresion.id,ts)
                print(expresion.id)
                if valor.tipo == Tipo.STRING:
                    if "[" in valor.valor:
                        valaux = valor.valor.split(sep =" ")
                        nuevo_cuadrupo = TS.Cuadruplo(valaux[0],valaux[2],"","=")
                        self.cuadruplos.agregar(nuevo_cuadrupo)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                        temp = self.generar_temporal()
                        nuevo_cuadrupo = TS.Cuadruplo(temp,valaux[5],"","=")
                        self.cuadruplos.agregar(nuevo_cuadrupo)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                        self.is_string = True
                        return temp
                    return valor.valor
                elif valor.tipo == TIPO_ESTRUCTURAS.ARREGLO:
                    self.is_arreglo = True
                    if "[" in valor.valor:
                        valaux = valor.valor.split(sep =" ")
                        nuevo_cuadrupo = TS.Cuadruplo(valaux[0],valaux[2],"","=")
                        self.cuadruplos.agregar(nuevo_cuadrupo)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                        temp = self.generar_temporal()
                        nuevo_cuadrupo = TS.Cuadruplo(temp,valaux[5],"","=")
                        self.cuadruplos.agregar(nuevo_cuadrupo)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                        return temp
                    return valor.valor
                else:
                    if "[" in valor.valor:
                        valaux = valor.valor.split(sep =" ")
                        nuevo_cuadrupo = TS.Cuadruplo(valaux[0],valaux[2],"","=")
                        self.cuadruplos.agregar(nuevo_cuadrupo)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                        temp = self.generar_temporal()
                        nuevo_cuadrupo = TS.Cuadruplo(temp,valaux[5],"","=")
                        self.cuadruplos.agregar(nuevo_cuadrupo)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                        return temp
                    return valor.valor
        else:
            if isinstance(expresion,OperacionCadena):
                cadena = expresion.val
                temp = self.generar_temporal()
                nuevo_cuadrupo = TS.Cuadruplo(temp,"H","","=")
                self.cuadruplos.agregar(nuevo_cuadrupo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                for car in cadena.replace("\"",""): 
                    indiceheap = self.generar_heap()
                    nuevo_cuadrupo = TS.Cuadruplo(indiceheap,str(ord(car)),"","=")
                    self.cuadruplos.agregar(nuevo_cuadrupo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                    nuevo_cuadrupoe = TS.Cuadruplo("H","H","1","+")
                    self.cuadruplos.agregar(nuevo_cuadrupoe)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadrupoe)
                nuevo_cuadrupo = TS.Cuadruplo(indiceheap,-1,"","=")
                self.cuadruplos.agregar(nuevo_cuadrupo)
                self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                nuevo_cuadrupoe = TS.Cuadruplo("H","H","1","+")
                self.cuadruplos.agregar(nuevo_cuadrupoe)
                self.etiquetas[self.etiqueta].append(nuevo_cuadrupoe)
                return temp
            elif isinstance(expresion,OperacionBooleana):
                if expresion.val.lower() == 'false':
                    temp = self.generar_temporal()
                    nuevo_cuadrupo = TS.Cuadruplo(temp,0,"","=")
                    self.cuadruplos.agregar(nuevo_cuadrupo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                    return temp
                else:
                    temp = self.generar_temporal()
                    nuevo_cuadrupo = TS.Cuadruplo(temp,1,"","=")
                    self.cuadruplos.agregar(nuevo_cuadrupo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                    return temp
            elif isinstance(expresion,OperacionCaracter):
                    cadena = expresion.val
                    temp = self.generar_temporal()
                    nuevo_cuadrupo = TS.Cuadruplo(temp,"H","","=")
                    self.cuadruplos.agregar(nuevo_cuadrupo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                    for car in cadena.replace("\'",""): 
                        indiceheap = self.generar_heap()
                        nuevo_cuadrupo = TS.Cuadruplo(indiceheap,str(ord(car)),"","=")
                        self.cuadruplos.agregar(nuevo_cuadrupo)
                        self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                    nuevo_cuadrupo = TS.Cuadruplo(indiceheap,-1,"","=")
                    self.cuadruplos.agregar(nuevo_cuadrupo)
                    self.etiquetas[self.etiqueta].append(nuevo_cuadrupo)
                    return temp
            else:     
                return expresion.val


#contadores

    def generar_funcionmulti(self):
        salida = "generar_multi{0}();".format(self.generarmulti)
        self.generarmulti += 1
        return salida

    def generar_temporal(self):
        salida = "t{0}".format(self.indice_temporal)
        self.indice_temporal += 1
        return salida

    def generarstack(self):
        salida = "P = {0} ;".format(self.indice_stack)
        salida += "\n  stack[int(P)]"
        self.indice_stack += 1
        return salida

    def generar_etiqueta(self):
        salida = "L{0}".format(self.indice_etiquetas)
        self.indice_etiquetas += 1
        return salida

    def generar_if(self):
        salida = "if{0}".format(self.indice_if)
        self.indice_if += 1
        return salida

    def generar_heap(self):
        salida = "heap[int(H)]"

        self.indice_heap += 1
        return salida