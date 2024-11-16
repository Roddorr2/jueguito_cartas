class Usuario:
    def __init__(self, idusuario, username, password):
        self.idusuario = idusuario
        self.username = username
        self.password = password
        
    def __str__(self):
        return f"Usuario: {self.username}, Clave: {self.password}"
    
    def __repr__(self):
        return f"Usuario(idusuario={self.idusuario}, username='{self.username}', password='{self.password}')"

    def show_user(self):
        return f"{self.username}"