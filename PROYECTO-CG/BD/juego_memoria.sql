IF DB_ID('juego_memoria') IS NOT NULL
BEGIN
    DROP DATABASE juego_memoria;
END
GO
CREATE DATABASE juego_memoria;
GO
USE juego_memoria;
GO
-- las tablas todavía no están creadas 
-- Tabla de Usuarios
CREATE TABLE Usuarios (
    idusuario INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(20) UNIQUE,
    clave NVARCHAR(50)
);

-- Tabla de Niveles
CREATE TABLE Niveles (
    idnivel INT IDENTITY(1,1) PRIMARY KEY,
    descripcion NVARCHAR(20)
);

-- Tabla de Partidas
CREATE TABLE Partidas (
    idpartida INT IDENTITY(1,1) PRIMARY KEY,
    idusuario INT,
    idnivel INT,
    tiempo TIME,
	fechapartida DATE,
	resultado BIT,
    FOREIGN KEY (idusuario) REFERENCES Usuarios(idusuario),
    FOREIGN KEY (idnivel) REFERENCES Niveles(idnivel)
);

-- Inserción de los niveles
INSERT INTO Niveles VALUES
('Nivel 1'),
('Nivel 2'),
('Nivel 3'),
('Nivel 4'),
('Nivel 5'),
('Nivel 6'),
('Nivel 7'),
('Nivel 8'),
('Nivel 9'),
('Nivel 10'),
('Nivel 11');

-- Consultas para visualización de datos
SELECT * FROM Usuarios
SELECT * FROM Partidas
SELECT * FROM Niveles

-- Eliminar usuario con id no apropiado
DELETE FROM Usuarios
WHERE idusuario = 2048;

-- Visualizar historial de partidas
SELECT tiempo,
	fechapartida,
	IIF(resultado = 1, 'GANADA', 'PERDIDA') AS resultado
FROM Partidas
WHERE idusuario = 1

-- Consulta para ver el top 10 de usuarios con mejor puntaje
SELECT TOP 10
	U.username,
	N.descripcion,
	P.tiempo,
	P.fechapartida
FROM Partidas P
INNER JOIN Usuarios U ON P.idusuario = U.idusuario
INNER JOIN Niveles N ON P.idnivel = N.idnivel
WHERE P.resultado = 1
ORDER BY P.tiempo ASC

-- script para restablecer el último valor del autoincremento en el ID 
DBCC CHECKIDENT ('Usuarios', RESEED, 2)
