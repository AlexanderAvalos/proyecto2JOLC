class TokenError:
    def __init__(self,tipo,descripcion,line,columna):
        self.tipo = tipo
        self.descripcion = descripcion
        self.line = line
        self.columna = columna 