# Modelo ML para detección de patrones de clic
# Concepto aún sin implementar
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

datos_clics = pd.DataFrame({
    'x': [100, 120, 130, 400, 420, 430, 700, 710, 720],
    'y': [200, 210, 215, 500, 510, 520, 800, 810, 815],
    'tiempo': [1.2, 1.5, 1.7, 2.0, 2.1, 2.3, 0.8, 0.9, 1.0]
})

scaler = StandardScaler()
datos_normalizados = scaler.fit_transform(datos_clics)

kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(datos_normalizados)

datos_clics['cluster'] = kmeans.labels_
print(datos_clics)
