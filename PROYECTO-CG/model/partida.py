class Partida:
    def __init__(self, idpartida, idusuario, idnivel, tiempo, fechapartida, resultado):
        self.idpartida = idpartida
        self.idusuario = idusuario
        self.idnivel = idnivel
        self.tiempo = tiempo
        self.fechapartida = fechapartida
        self.resultado = resultado
        
    def __str__(self):
        return f"Partida: {self.idpartida}, Usuario: {self.idusuario}, Nivel: {self.idnivel}, Tiempo: {self.tiempo}, Fecha: {self.fechapartida}, Resultado: {self.resultado}"
    
    def __repr__(self):
        return f"Partida(idpartida={self.idpartida}, idusuario={self.idusuario}, idnivel={self.idnivel}, tiempo={self.tiempo}, fechapartida='{self.fechapartida}', resultado='{self.resultado}')"
    
    