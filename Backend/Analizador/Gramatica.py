from Error import *
from Instruccion import *
from Expresion import *
import ply.yacc as yacc
import ply.lex as lex
import re

lst_error = []


def agregarError(tipo, descripcion, linea, columna):
    global lst_error
    new_error = TokenError(tipo,descripcion,linea,columna)
    new_error = ''
    lst_error.append(new_error)



reservadas = {
    'nothing': 'NOTHING',
    'Int64': 'INT64',
    'Float64': 'FLOAT64', 
    'Bool': 'BOOL',
    'char': 'CHAR',
    'string': 'STRING',
    'uppercase': 'UPPERCASE',
    'println': 'PRINTLN',
    'lowercase': 'LOWERCASE',
    'print': 'PRINT',
    'function': 'FUNCTION',
    'end': 'END',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'in': 'IN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'return': 'RETURN',
    'struct': 'STRUCTR',
    'mutable': 'MUTABLE',
    'true': 'TRUE',
    'false': 'FALSE',
    'parse':'PARSE',
    'length':'LENGTH',
    'trunc':'TRUNC',
    'global':'GLOBAL',
    'local': 'LOCALR' 
}

tokens = [
    # noreservadas
    'MAS',
    'MENOS',
    'MULTIPLICACION',
    'DIVISION',
    'POTENCIA',
    'MODULO',
    'MAYOR',
    'MENOR',
    'IGUAL',
    'MAYORIGUAL',
    'MENORIGUAL',
    'IGUALIGUAL',
    'DIFERENTE',
    'DOBLEPUNTO',
    'PUNTOYCOMA',
    'PARIZQ',
    'PARDER',
    'CORIZQ',
    'CORDER',
    'COMA',
    'PUNTO',
    'AND',
    'OR',
    'NOT',
    # Datos
    'DECIMAL',
    'ENTERO',
    'CADENA',
    'ID',
    'CARACTER',
    'DOSPUNTOS',
] + list(reservadas.values())

t_PUNTOYCOMA = r';'
t_DOSPUNTOS = r':'
t_MAS = r'\+'
t_MULTIPLICACION = r'\*'
t_MENOS = r'-'
t_DIVISION = r'/'
t_POTENCIA = r'\^'
t_MODULO = r'%'
t_MAYOR = r'>'
t_MENOR = r'<'
t_MAYORIGUAL = r'>='
t_MENORIGUAL = r'<='
t_IGUALIGUAL = r'=='
t_DIFERENTE = r'!='
t_DOBLEPUNTO = r'::'
t_PARIZQ = r'\('
t_PARDER = r'\)'
t_CORDER = r'\]'
t_CORIZQ = r'\['
t_COMA = r'\,'
t_PUNTO = r'\.'
t_OR = r'\|\|'
t_NOT = r'\!'
t_AND = r'&&'
t_IGUAL = r'='
t_ignore = " \t\r"

def t_DECIMAL(t):
    r'\d+\.\d+'
    try:
        t.value = float(t.value)
    except ValueError:
        print("Error: %d ", t.value)
        t.value = 0
    return t


def t_ENTERO(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Valor del integer erroneo %d", t.value)
        t.value = 0
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reservadas.get(t.value.lower(), 'ID')
    return t


def t_CADENA(t):
    r'\".*?\"'
    t.value = t.value[1:-1]
    return t


def t_CARACTER(t):
    r'\'.?\''
    t.value = t.value[1:-1]
    return t


def t_COMENTARIOSIMPLE(t):
    r'\#.*\n'
    t.lexer.lineno += 1


def t_COMENTARIOMULTIPLE(t):
    r'\#\=(.|\n)*?\=\#'
    t.lexer.lineno += t.value.count('\n')


def t_NUEVALINEA(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    agregarError('Lexico', "caracter \'{0}'\ ilegal".format(t.value[0]), t.lexer.lineno+1, buscar_columna(t))
    t.lexer.skip(1)

lexer = lex.lex()


precedence = (
    ('left', 'COMA'),
    ('right', 'NOT'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'IGUALIGUAL', 'DIFERENTE'),
    ('left', 'MENOR', 'MENORIGUAL', 'MAYOR', 'MAYORIGUAL'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULTIPLICACION', 'DIVISION', 'MODULO'),
    ('left', 'POTENCIA'),
    ('right','UMENOS' )
)
#inicio
def p_init(p):
    'init : instrucciones'
    p[0] = p[1]

def p_instrucciones(p):
    'instrucciones : instrucciones instruccion'
    p[1].append(p[2])
    p[0] = p[1]


def p_instrucciones2(p):
    'instrucciones : instruccion'
    array = []
    array.append(p[1])
    p[0] = array
    
def p_instruccion(p):
    ''' instruccion : asignacion
                    | structs
                    | arreglos
                    | funcion
                    | sentencia
                    | callfuncion
                    | impresion
                    | error PUNTOYCOMA
                    | error END
                    
    '''
    p[0] = p[1]


#asignacion simple
def p_asignacion(p):
    'asignacion : ID IGUAL operacion DOBLEPUNTO tipo PUNTOYCOMA'
    p[0] = Declaracion(None,p[1],p[3],p[5],p.lineno(1),buscar_columna(p.slice[1]))

def p_asignacion2(p):
    'asignacion : ID IGUAL operacion PUNTOYCOMA'
    p[0] = Declaracion(None,p[1],p[3],None,p.lineno(1),buscar_columna(p.slice[1]))

def p_asignacion3(p):
    'asignacion : GLOBAL ID IGUAL operacion PUNTOYCOMA'
    p[0] = Declaracion(p[1],p[2],p[4],None,p.lineno(2),buscar_columna(p.slice[1]))

def p_asignacion4(p):
    'asignacion : GLOBAL ID IGUAL operacion DOBLEPUNTO tipo PUNTOYCOMA'
    p[0] = Declaracion(p[1],p[2],p[4],p[6],p.lineno(2),buscar_columna(p.slice[1]))

def p_asignacion5(p):
    'asignacion : LOCALR ID IGUAL operacion PUNTOYCOMA'
    p[0] = Declaracion(p[1],p[2],p[4],None,p.lineno(2),buscar_columna(p.slice[1]))

def p_asignacion6(p):
    'asignacion : LOCALR ID IGUAL operacion DOBLEPUNTO tipo PUNTOYCOMA'
    p[0] = Declaracion(p[1],p[2],p[4],p[6],p.lineno(2),buscar_columna(p.slice[1]))

# delcaracion struct
def p_structMutable(p):
    'structs : MUTABLE STRUCTR ID listaAtributos END PUNTOYCOMA'
    p[0] = StructsIn(p[3], p[4], p.lineno(1), buscar_columna(p.slice[1]))

def p_structInmutable(p):
    'structs : STRUCTR ID listaAtributos END PUNTOYCOMA'
    p[0] = StructsIn(p[2], p[3], p.lineno(1), buscar_columna(p.slice[1]))

def p_listaatributos(p):
    'listaAtributos : listaAtributos lista'
    p[1].append(p[2])
    p[0] = p[1]

def p_listaAtributos(p):
    'listaAtributos : lista '
    p[0]= [p[1]]

def p_lista(p):
    'lista : ID DOBLEPUNTO tipo PUNTOYCOMA'
    p[0] = StructAtributos(p[1],p[3],p.lineno(1), buscar_columna(p.slice[1]))

def p_lista2(p):
    'lista : ID PUNTOYCOMA'
    p[0] = StructAtributos(p[1],None,p.lineno(1), buscar_columna(p.slice[1]))


#struct leer
def p_operacionStruct(p):
    'operacion : ID operacionstructs'
    p[0] = OperacionStruct(p[1],p[2],p.lineno(1), buscar_columna(p.slice[1]))


def p_operacionStruct2(p):
    'operacionstructs : operacionstructs operacionstruct'
    p[1].append(p[2])
    p[0] = p[1]
def p_operacionstruct3(p):
    'operacionstructs : operacionstruct'
    p[0] = [p[1]]

def p_operacionstruct4(p):
    'operacionstruct : PUNTO ID'
    p[0] = p[2]

#asignacion struct
def p_asignacionstruct(p):
    'asignacion : ID operacionstructs IGUAL operacion PUNTOYCOMA'
    p[0] = AsginacionStruc(p[1],p[2],p[4],p.lineno(1),buscar_columna(p.slice[1]))

#arreglos 
def p_declaracionarreglos(p):
    'arreglos : ID IGUAL CORIZQ valores CORDER PUNTOYCOMA'
    p[0] = DeclaracionArreglos(p[1],p[4],p.lineno(1), buscar_columna(p.slice[1]))


def p_operacionarreglos(p):
    'operacion : CORIZQ  valores CORDER'
    p[0] = OperacionArreglo(p[2],p.lineno(1), buscar_columna(p.slice[1]))

def p_operacionarreglo(p):
    'operacion : ID listaposiciones'
    p[0] = OperacionArregloget(p[1],p[2],p.lineno(1), buscar_columna(p.slice[1]))

def p_asignacionArreglo(p):
    'asignacion : ID listaposiciones IGUAL operacion PUNTOYCOMA'
    p[0] = AsignacionArreglo(p[1],p[2],p[4],p.lineno(1), buscar_columna(p.slice[1]))

def p_listaposiciones(p):
    'listaposiciones : listaposiciones listaposicion'
    p[1].append(p[2])
    p[0] = p[1]

def p_listaposiciones2(p):
    'listaposiciones : listaposicion'
    p[0]= [p[1]]

def p_listaposicion(p):
    'listaposicion : CORIZQ operacion CORDER'
    p[0] = listaindicies(p[2],p.lineno(1), buscar_columna(p.slice[1]))

#funcion
def p_funciones(p):
    'funcion : FUNCTION ID PARIZQ parametros PARDER instrucciones END PUNTOYCOMA'
    p[0] = Funcion(p[2],p[4],p[6],p.lineno(1))

def p_funciones2(p):
    'funcion :  FUNCTION ID PARIZQ PARDER instrucciones END PUNTOYCOMA'
    p[0] = Funcion(p[2], None,p[5], p.lineno(1))

def p_parametros(p):
    'parametros : parametros COMA parametro'
    p[1].append(p[3])
    p[0] = p[1]

def p_parametros2(p):
    'parametros : parametro'
    p[0]= [p[1]]

def p_pamaretrosimple(p):
    'parametro : ID DOBLEPUNTO tipo '
    p[0] = Parametros(p[1],p[3],p.lineno(1),buscar_columna(p.slice[1]))

def p_parametrossimple2(p):
    'parametro : ID '
    p[0] = Parametros(p[1], None, p.lineno(1),buscar_columna(p.slice[1]))

#sentencias 
def p_sentencia(p):
    '''sentencia : if
                 | while
                 | for
                 | return 
                 | continue
                 | break
    '''
    p[0] = p[1]

#sentencia if
def p_if(p):
    'if : IF operacion instrucciones END PUNTOYCOMA'
    s_if = SentenciaIf(p[2],p[3],p.lineno(1))
    p[0] = If(s_if, None, None, p.lineno(1))

def p_ifelse(p):
    'if : IF operacion instrucciones ELSE instrucciones END PUNTOYCOMA'
    s_if = SentenciaIf(p[2],p[3],p.lineno(1))
    s_else = SentenciaIf(None, p[5],p.lineno(4))
    p[0] = If(s_if, None, s_else, p.lineno(1))

def p_elseif2(p): 
    'if : IF operacion instrucciones elseifaux END PUNTOYCOMA'
    s_if = SentenciaIf(p[2],p[3],p.lineno(1))
    s_elif = p[4]
    p[0] = If(s_if, s_elif, None, p.lineno(1))

def p_elseif1(p):
    'elseifaux : elseifaux aux'
    p[1].append(p[2])
    p[0] = p[1]

def p_elseif3(p):
    'elseifaux : aux'
    p[0] = [p[1]]

def p_elif2(p):
    'aux : ELSE IF operacion instrucciones'
    p[0] = SentenciaIf(p[2],p[3],p.lineno(1))

def p_ifelseifelse(p):
    'if : IF operacion instrucciones elseifaux ELSE instrucciones END PUNTOYCOMA'
    s_if = SentenciaIf(p[2],p[3],p.lineno(1))
    s_elif = p[4]
    s_else = SentenciaIf(None, p[6], p.lineno(5))
    p[0] = If(s_if,s_elif,s_else, p.lineno(1))

#while 
def p_while(p):
    'while : WHILE operacion instrucciones END PUNTOYCOMA'
    p[0] = While(p[2], p[3], p.lineno(1))


#for
def p_for(p):
    'for : FOR ID IN condicional instrucciones END PUNTOYCOMA'
    p[0] = For(p[2], p[4], p[5], p.lineno(1))

def p_condicional1(p):
    'condicional : operacion'
    p[0] = condicionalSimple(p[1], p.lineno(1))

def p_condicional2(p):
    'condicional : operacion DOSPUNTOS operacion'
    p[0] = condicionalRango(p[1],p[3], p.lineno(1))

#return 
def p_return(p):
    'return : RETURN operacion PUNTOYCOMA'
    p[0] = SentenciaReturn(p[2],p.lineno(1))

#continue
def p_continue(p):
    'continue : CONTINUE PUNTOYCOMA'
    p[0] = SentenciaContinue(p.lineno(1))

#break
def p_break(p):
    'break : BREAK PUNTOYCOMA'
    p[0] = SentenciaBreak(p.lineno(1))

#llamada de funciones 
def p_llamada(p):
    'callfuncion : ID PARIZQ PARDER PUNTOYCOMA'
    p[0] = llamada(p[1], None, p.lineno(1))

def p_llamada2(p):
    'callfuncion : ID PARIZQ valores PARDER PUNTOYCOMA'
    p[0] = llamada(p[1], p[3], p.lineno(1))

#impresion
def p_impresionSimple(p):
    '''impresion : PRINT PARIZQ valores PARDER PUNTOYCOMA
                 | PRINTLN PARIZQ valores PARDER PUNTOYCOMA
    '''
    p[0] = Printval([p[1]], p[3], p.lineno(3))

#valores y operaciones 
#operaciones simples 
def p_operacionLogicas(p):
    '''operacion   : operacion AND              operacion
                   | operacion OR               operacion
    '''
    p[0] = OperacionBinaria(p[1],p[3],p[2],p.lineno(1),buscar_columna(p.slice[2]))  

def p_operacionRelacional(p):
    '''operacion    : operacion IGUALIGUAL      operacion 
                    | operacion DIFERENTE       operacion
                    | operacion MAYOR           operacion 
                    | operacion MENOR           operacion
                    | operacion MENORIGUAL      operacion
                    | operacion MAYORIGUAL      operacion
    '''
   
    p[0] = OperacionBinaria(p[1],p[3],p[2],p.lineno(1),buscar_columna(p.slice[2]))  

def p_operacionAritmeticas(p):
    '''operacion    : operacion MAS             operacion
                    | operacion MENOS           operacion
                    | operacion MULTIPLICACION  operacion
                    | operacion DIVISION        operacion
                    | operacion MODULO          operacion
                    | operacion POTENCIA        operacion
    '''
    p[0] = OperacionBinaria(p[1],p[3],p[2],p.lineno(1),buscar_columna(p.slice[2]))  

def p_operacionUnarias(p):
    '''operacion   : MENOS  operacion %prec UMENOS
                   | NOT    operacion %prec UMENOS 
    '''
    p[0] = OperacionUnaria(p[2],p[1],p.lineno(1),buscar_columna(p.slice[1])) 

def p_operacionParentesis(p):
    'operacion : PARIZQ operacion PARDER'
    p[0] = p[2]

def p_operacionLlamada3(p):
    'operacion : ID PARIZQ valores PARDER '
    p[0] = llamada(p[1], p[3], p.lineno(1))

def p_operacionLlamada4(p):
    'operacion : ID PARIZQ  PARDER '
    p[0] = llamada(p[1], None, p.lineno(1))
#funciones locales
def p_operacionLocal(p):
    'operacion : local'
    p[0] = p[1]

def p_operacionLocalparse(p):
    'local     : PARSE PARIZQ tipo COMA CADENA PARDER '
    p[0] = OperacionParse(p[3],p[5],p.lineno(1))

def p_operacionLocaltrunc(p):
    'local     : TRUNC PARIZQ  DECIMAL PARDER  '
    p[0] = OperacionTrunc(p[3],p.lineno(1))

def p_operacionLocalLenght(p):
    'local    : LENGTH PARIZQ operacion PARDER '
    p[0] = OperacionLenght(p[3],p.lineno(1),buscar_columna(p.slice[1]))

def p_operacionLocalUpper(p):
    'local    : UPPERCASE PARIZQ operacion PARDER '
    p[0] = OperacionUPPER(p[3],p.lineno(1),buscar_columna(p.slice[1]))

def p_operacionLocalLower(p):
    'local    : LOWERCASE PARIZQ operacion PARDER '
    p[0] = OperacionLOWER(p[3],p.lineno(1),buscar_columna(p.slice[1]))

def p_operacionLocalstring(p):
    'local     : STRING PARIZQ operacion PARDER  '
    p[0] = OperacionString(p[3],p.lineno(1))


def p_operacionValor(p):
    'operacion : valor'
    p[0] = p[1]

#valores

def p_valores(p):
    'valores : valores COMA operacion' 
    p[1].append(p[3])
    p[0] = p[1]

def p_valores2(p):
    'valores : operacion'
    p[0] = [p[1]]

#tipos y valores 
def p_tipo(p):
    '''tipo     :   INT64
                |   FLOAT64
                |   BOOL
                |   CHAR
                |   ID
                |   STRING
    '''
    p[0] = p[1]

def p_valorInt(p):
    'valor : ENTERO'
    p[0] = OperacionNumero(p[1], p.lineno(1), buscar_columna(p.slice[1])) 


def p_valorID(p):
    'valor : ID'
    p[0]= OperacionVariable(p[1], p.lineno(1), buscar_columna(p.slice[1]))


def p_valorFloat(p):
    'valor : DECIMAL'
    p[0]= OperacionNumero(p[1], p.lineno(1), buscar_columna(p.slice[1]))


def p_valorString(p):
    'valor : CADENA'
    p[0]= OperacionCadena("\""+p[1]+"\"", p.lineno(1), buscar_columna(p.slice[1]))


def p_valorChar(p):
    'valor : CARACTER'
    p[0]= OperacionCaracter("\'"+p[1]+"\'", p.lineno(1), buscar_columna(p.slice[1]))


def p_valorFalse(p):
    'valor : TRUE'
    p[0]= OperacionBooleana(p[1], p.lineno(1), buscar_columna(p.slice[1]))


def p_valorTrue(p):
    'valor : FALSE'
    p[0]= OperacionBooleana(p[1], p.lineno(1), buscar_columna(p.slice[1]))

def p_valorNulo(p):
    'valor : NOTHING'
    p[0] = OperacionNULO(p[1],p.lineno(1), buscar_columna(p.slice[1]))

def p_error(p):
    agregarError('sintantico',  "Sintaxis no reconocida \"{0}\"".format(p.value) ,p.lineno+1, buscar_columna(p))
    print('Error sintactico')


input = ""
parser = yacc.yacc(write_tables = True)

def parse(inpu):
    global input
    global lst_error
    lst_error = []
    lexer = lex.lex(reflags= re.IGNORECASE)
    lexer.lineno = 0
    return parser.parse(inpu, lexer=lexer)

def buscar_columna(token):
    line_start = input.rfind('\n', 0, token.lexpos)+1
    return (token.lexpos - line_start)+1
