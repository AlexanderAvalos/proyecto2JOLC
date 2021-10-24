import sys
sys.path.insert(1, './Analizador')
import Gramatica as g
import TablaSimbolo as TS
import Traductor as tradu

from flask import Flask,request 
from flask_cors import CORS 


app = Flask(__name__)
CORS(app)

@app.route('/serv', methods = ['POST'])
def inicio():
    data = request.json
    input = data['valor']
    Instruccion = g.parse(input)
    ts_global = TS.TablaSimbolos()
    funciona = tradu.Traducir(Instruccion,ts_global)
    funciona.traducir(Instruccion)
    salida = funciona.salida
    return salida

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)