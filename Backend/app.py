import sys
sys.path.insert(1, './Analizador')
import Gramatica as g
import TablaSimbolo as TS
import Traductor as tradu

from flask import Flask,request 
from flask_cors import CORS 
traduc = []

app = Flask(__name__)
CORS(app)

@app.route('/serv', methods = ['POST'])
def inicio():
    data = request.json
    input = data['valor']
    Instruccion = g.parse(input)
    ts_global = TS.TablaSimbolos()
    funciona = tradu.Traducir(Instruccion,ts_global)
    traduc.append(funciona)
    funciona.traducir(Instruccion)
    salida = funciona.salida
   
    return salida


@app.route('/serv/simbolo',methods = ['GET'])
def TablaSimbolo():
    aux = ""
    if len(traduc) > 0:
        for val in traduc:
            aux = val.graficar()
        traduc.remove(val);
        print(aux)
    return aux 

@app.route('/serv/error', methods = ['GET'])
def tablaError():
    aux = ""
    if len(traduc) > 0:
        for val in traduc:
            aux = val.graficarErrores()
        traduc.remove(val);
    else:
        print("error al crear grafica")   
    print(aux)
    return aux

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)