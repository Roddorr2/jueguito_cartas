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
	clics INT,
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
	IIF(resultado = 1, 'GANADA', 'PERDIDA') AS resultado,
	clics
FROM Partidas
WHERE idusuario = 1

-- Consulta para ver el top 10 de usuarios con mejor puntaje
SELECT U.username,
	N.descripcion,
	P.tiempo,
	P.fechapartida,
	P.clics
FROM Partidas P
INNER JOIN Usuarios U ON P.idusuario = U.idusuario
INNER JOIN Niveles N ON P.idnivel = N.idnivel
WHERE P.resultado = 1 AND P.idnivel > 1
ORDER BY P.clics  ASC;
-- Consulta para seleccionar los datos username, tiempo, clics según los once niveles disponibles
WITH MejorPartidaPorNivel AS (
    SELECT
        CONCAT('Nivel ', CAST(N.idnivel AS VARCHAR)) AS Nivel,
        U.username,
        P.clics,
        P.tiempo,
        ROW_NUMBER() OVER (
            PARTITION BY N.idnivel
            ORDER BY P.clics ASC, P.tiempo ASC
        ) AS rn
    FROM Partidas P
    INNER JOIN Usuarios U ON P.idusuario = U.idusuario
    INNER JOIN Niveles N ON P.idnivel = N.idnivel
    WHERE P.idusuario = 9 
      AND P.resultado = 1
)
SELECT 
    Nivel,
    Username,
    Clics,
    CONVERT(VARCHAR, Tiempo, 108) AS Tiempo
FROM MejorPartidaPorNivel
WHERE rn = 1
ORDER BY CAST(SUBSTRING(Nivel, 7, LEN(Nivel)) AS INT);

-- script para restablecer el último valor del autoincremento en el ID 
DBCC CHECKIDENT ('Usuarios', RESEED, 6);
