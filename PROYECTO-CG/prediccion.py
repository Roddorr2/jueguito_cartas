import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns

class Prediccion:
    def __init__(self, archivo_csv):
        # Cargar los datos desde el archivo CSV
        self.data = pd.read_csv(archivo_csv)
        self.model = LinearRegression()
        
        # Extraer el nombre del usuario desde el archivo CSV
        self.username = self.data['Username'].iloc[0]
    
    def entrenar_y_predecir(self):
        # Preprocesar los datos
        self.data['Nivel'] = self.data['Nivel'].apply(lambda x: int(x.split()[-1]))  # Extraer el número del nivel
        
        # Definir las características (X) y el objetivo (y)
        X = self.data[['Nivel']]  # El nivel es la característica
        y = self.data['Clics']  # El número de clics es la variable objetivo
        
        # Dividir los datos en conjuntos de entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        
        # Evaluar el modelo
        mse = mean_squared_error(y_test, y_pred)
        print(f"Error cuadrático medio (MSE): {mse}")
        
        self.graficar_predicciones(X_test, y_test, y_pred)
        
        # Predicción para todos los niveles disponibles en los datos
        self.predicciones = self.model.predict(X)
        self.mostrar_predicciones()

    def graficar_predicciones(self, X_test, y_test, y_pred):
        # Graficar los resultados reales vs predicciones
        plt.figure(figsize=(10, 6))
        plt.scatter(X_test, y_test, color='blue', label='Datos reales')
        plt.plot(X_test, y_pred, color='red', label='Predicciones', linewidth=2)
        plt.xlabel('Nivel')
        plt.ylabel('Clics')
        plt.title('Predicción de Clics en función del Nivel')
        plt.legend()
        plt.show()
        
    def mostrar_predicciones(self):
        print(f"\nPredicciones para el usuario: {self.username}")
        for nivel, clics in zip(self.data['Nivel'], self.predicciones):
            print(f"Nivel {nivel}: {clics:.2f} clics")
        
        print("\nEstadísticas Descriptivas:")
        print(self.data['Clics'].describe())

        # Nivel con más clics
        max_clics = self.data.loc[self.data['Clics'].idxmax()]
        print(f"\nNivel con más clics: {max_clics['Nivel']} con {max_clics['Clics']} clics")
        
        # Nivel con menos clics
        min_clics = self.data.loc[self.data['Clics'].idxmin()]
        print(f"Nivel con menos clics: {min_clics['Nivel']} con {min_clics['Clics']} clics")
