from enum import Enum

class OPERACION_LOGICA(Enum):
    AND = 1
    OR = 2
    NOT = 3

class OPERACION_RELACIONAL(Enum):
    MAYOR = 1
    MAYORQUE = 2
    MENOR = 3
    MENORQUE = 4
    IGUAL = 5
    DIFERENTE = 6

class OPERACION_NUMERICA(Enum):
    SUMA = 1
    RESTA = 2
    MULTIPLICACION = 3
    DIVISION = 4
    MODULAR = 5
    POTENCIA = 6

class OPERACION_NATIVA(Enum):
    SEN = 1
    COS = 2
    TAN = 3
    LOGC = 4
    LOGD = 5
    UPPER = 6
    LOWER = 7
    LENGTH = 8
    SQRT = 9

class TIPO_ESTRUCTURAS(Enum):
    CONSTRUCTOR= 1
    FUNCION= 2
    ARREGLO = 3
    STRUCT = 4