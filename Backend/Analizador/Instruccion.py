import Expresion as exp
from TablaSimbolo import Tipo

class Instruccion:
    'Clase definida para usar como interfaz'

#isntrucciones basicas
class Declaracion(Instruccion):
    def __init__(self,ambiente,id, valor,tipo, linea,columna):
        self.ambiente = ambiente
        self.id = id
        self.valor = valor 
        self.columna = columna
        self.tipo = self.verificarTipo(tipo)
        self.linea = linea
        super().__init__()

    def verificarTipo(self,tipo):
        tipo = str(tipo).lower()
        if len(tipo) > 0:
            if  tipo == 'int64':
                return Tipo.ENTERO 
            elif tipo == 'float64': 
                return Tipo.DECIMAL
            elif tipo == 'string': 
                 return Tipo.STRING
            elif tipo == 'bool':
                return Tipo.BOOL
            elif tipo == 'char' :
                return Tipo.CHAR
            elif tipo == None :
                return Tipo.NULO

#structs
class StructsMutable(Instruccion):
    def __init__(self, objeto, listaAtributos, linea, columna):
        self.objeto = objeto
        self.listaAtributos = listaAtributos
        self.linea = linea
        self.columna = columna
        super().__init__()

class StructsIn(Instruccion):
    def __init__(self, objeto, listaAtributos, linea, columna):
        self.objeto = objeto
        self.listaAtributos = listaAtributos
        self.linea = linea
        self.columna = columna
        super().__init__()

class StructAtributos(Instruccion):
    def __init__(self, id, tipo,linea, columna):
        self.id = id
        self.tipo = tipo
        self.linea = linea
        self.columna = columna
        super().__init__()

class DeclaracionStruct(Instruccion):
    def __init__(self,id, tipo, idstruct, atributos,linea,columna):
        self.id = id
        self.tipo = tipo
        self.idstruct = idstruct
        self.atributos = atributos
        self.linea = linea 
        self.columna = columna
        super().__init__()

class OperacionStruct(Instruccion):
    def __init__(self,idstruct, lstid,linea,columna) :
        self.idstruct = idstruct
        self.lstid = lstid
        self.linea = linea 
        self.columna = columna
        super().__init__()

class AsginacionStruc(Instruccion):
    def __init__(self,id,lstid,operacion,linea,columna):
        self.idstruct = id
        self.lstid = lstid
        self.operacion = operacion
        self.linea = linea 
        self.columna = columna
        super().__init__()
    
       
#arreglos
class DeclaracionArreglos(Instruccion):
    def __init__(self,id,listavalores,linea, columna):
        self.id = id
        self.lista = listavalores
        self.linea = linea
        self.columna = columna
        super().__init__()

class listaindicies(Instruccion):
    def __init__(self,operacion,linea, columna ):
        self.linea = linea
        self.columna = columna
        self.operacion = operacion
        super().__init__()

class OperacionArreglo(Instruccion):
    def __init__(self,lstoperacion,linea, columna ):
        self.lstoperacion = lstoperacion
        self.linea = linea
        self.columna = columna
        super().__init__()


class OperacionArregloget(Instruccion):
    def __init__(self,id,listaposicion,linea, columna ):
        self.id = id
        self.listaposicion = listaposicion
        self.linea = linea
        self.columna = columna
        super().__init__()

class AsignacionArreglo(Instruccion):
    def __init__(self,idarreglo, listaposicion, operacion, linea ,columna):
        self.id = idarreglo
        self.listaposicion = listaposicion
        self.linea = linea
        self.columna = columna
        self.operacion = operacion
        super().__init__()
    
#funciones
class Funcion(Instruccion):
    def __init__(self,idFuncion,parametros, sentencias,linea):
        self.idFuncion = idFuncion
        self.parametros = parametros
        self.sentencias = sentencias 
        self.linea = linea 
        super().__init__()

class Parametros(Instruccion):
    def __init__(self, idparametro, tipo, linea,columna):
        self.idparametro = idparametro
        self.tipo = tipo
        self.linea = linea 
        self.columna = columna
        super().__init__()
    


#sentencias 
#if
class If(Instruccion):
    def __init__(self, s_if, s_elif, s_else, linea):
        self.s_if = s_if
        self.s_elif = s_elif
        self.s_else = s_else
        self.linea = linea
        super().__init__()

class SentenciaIf(Instruccion):
    def __init__(self,condicion, sentencias, linea):
        self.condicion = condicion
        self.sentencias = sentencias
        self.linea = linea
        super().__init__()

#while
class While(Instruccion):
    def __init__(self, condicion, sentencias, linea):
        self.condicion = condicion
        self.sentencias = sentencias
        self.linea = linea
        super().__init__()

#for
class For(Instruccion):
    def __init__(self,id, condicional, sentencias, linea):
        self.id = id
        self.condicional = condicional
        self.sentencias = sentencias
        self.linea = linea 
        super().__init__()

class condicionalSimple(Instruccion):
    def __init__(self,operacion,linea):
        self.operacion = operacion
        self.linea = linea
        super().__init__()

class condicionalRango(Instruccion):
    def __init__(self, rangoizq, rangoder, linea ):
        self.rangoizq = rangoizq
        self.rangoder = rangoder 
        self.liena = linea 
        super().__init__()

#SeReeturn
class SentenciaReturn(Instruccion):
    def __init__(self,operacion,linea):
        self.operacion = operacion
        self.linea = linea 
        super().__init__()
#sencontinue
class SentenciaContinue(Instruccion):
    def __init__(self,line):
        self.line = line
        super().__init__()
#break
class SentenciaBreak(Instruccion):
    def __init__(self,line):
        self.line = line
        super().__init__()

#llamada 
class llamada(Instruccion): 
    def __init__(self, idfuncion, parametros, linea):
        self.idfuncion = idfuncion
        self.parametros = parametros
        self.linea = linea 
        super().__init__()
#impresion
class Printval(Instruccion):
    def __init__(self,tipo,val,line):
        self.tipo = tipo
        self.val = val 
        self.line = line
        super().__init__()      


#operaciones aparte 
class OperacionBinaria(Instruccion):
    def __init__(self,opIzq,opDer,operacion,line,columna):
        self.opIzq = opIzq
        self.opDer = opDer
        self.operacion = operacion
        self.line = line
        self.columna = columna
        super().__init__()

class OperacionUnaria(Instruccion):
    def __init__(self,op1,operacion,line,columna):
        self.op1 = op1
        self.operacion = self.verficarUni(operacion)
        self.line = line
        self.columna = columna
        super().__init__()

    def verficarUni(self,operacion):
        if operacion == '!':
            return exp.OPERACION_LOGICA.NOT
        elif  operacion == '-':
            return exp.OPERACION_NUMERICA.RESTA

#locales
class OperacionLOWER(Instruccion):
    def __init__(self, operador,line,columna):
        self.operador = operador
        self.line = line
        self.columna = columna
        super().__init__()

class OperacionUPPER(Instruccion):
    def __init__(self, operador,line,columna):
        self.operador = operador
        self.line = line
        self.columna = columna
        super().__init__()

class OperacionLenght(Instruccion):
    def __init__(self, operador,line,columna):
        self.operador = operador
        self.line = line
        self.columna = columna
        super().__init__()

class OperacionParse(Instruccion):
    def __init__(self, tipo, valor, linea):
        self.tipo = self.verficartipo(tipo)
        self.valor = valor
        self.linea = linea
        super().__init__()

    def verficartipo(self,tipo):
        if tipo.lower() == "int64":
            return Tipo.ENTERO
        elif tipo.lower() == "float64":
            return Tipo.DECIMAL
        else:
            print("tipo invalido")
            return Tipo.INVALIDO

class OperacionTrunc(Instruccion):
    def __init__(self, valor, linea):
        self.valor = valor
        self.linea = linea
        super().__init__()


class OperacionString(Instruccion):
    def __init__(self,valor,linea):
        self.valor = valor
        self.linea = linea
        super().__init__()
        
#valores
class OperacionNumero(Instruccion):
    def __init__(self,val, line, columna) :
        self.val = val
        self.line = line 
        self.columna = columna
        super().__init__()

class OperacionVariable(Instruccion):
    def __init__(self,id,linea,columna):
        self.id = id
        self.linea = linea 
        self.columna = columna
        super().__init__()

class OperacionCaracter(Instruccion):
    def __init__(self, val, linea,columna):
        self.val= val
        self.linea = linea 
        self.columna = columna
        super().__init__()

class OperacionCadena(Instruccion):
    def __init__(self,val,linea,columna):
        self.val = val
        self.linea = linea 
        self.columna = columna
        super().__init__()

class OperacionBooleana(Instruccion):
    def __init__(self, val, linea , columna):
        self.val = val
        self.linea = linea 
        self.columna = columna
        super().__init__()

class OperacionNULO():
    def __init__(self, val, linea , columna):
        self.val = val
        self.linea = linea 
        self.columna = columna
        super().__init__()