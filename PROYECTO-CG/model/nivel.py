class Nivel:
    def __init__(self, idnivel, descripcion):
        self.idnivel = idnivel
        self.descripcion = descripcion
        
    def __str__(self):
        return f"Nivel {self.idnivel}: {self.descripcion}"
    
    def __repr__(self):
        return f"Nivel({self.idnivel}, '{self.descripcion}')"