# Modelo ResNet-18 (Clasificación Bioacústica)

Este directorio contiene los archivos y resultados correspondientes al entrenamiento y validación de la arquitectura **ResNet-18**, utilizada como modelo base (*baseline*) para la clasificación de 14 categorías bioacústicas (13 especies de aves y una clase de ruido ambiental).

## Arquitectura y Estrategia de Entrenamiento

* **Modelo Base:** ResNet-18 (Pesos iniciales pre-entrenados en ImageNet).
* **Estrategia:** *Fine-Tuning* completo. Todos los bloques residuales fueron descongelados y ajustados para adaptar los filtros geométricos de la red a los bordes frecuenciales de los espectrogramas.
* **Capa Clasificadora Personalizada:** Se sustituyó la capa final (`fc`) por un bloque secuencial para mitigar el sobreajuste:
  * Capa `Dropout(p=0.4)`
  * Capa `Linear` adaptada a 14 salidas.

## Parámetros Técnicos

* **Entradas:** Espectrogramas Mel de 256x256 píxeles.
* **Cantidad de Parámetros:** ~11.1 millones (entrenables en su totalidad).
* **Épocas Óptimas de Entrenamiento:** 20 épocas continuas.
* **Optimizador:** Adam, aplicando una reducción en la tasa de aprendizaje inicial para sostener la estabilidad durante la readaptación profunda.

## Archivos Relevantes en el Proyecto
* `modelo_resnet18_aves_20_LR4.pth`: Archivo físico que contiene los pesos finales del entrenamiento con el mejor desempeño medido.
* `historial_curvas_resnet18_20_LR4.csv`: Registro métrico época por época de las trayectorias de *Loss* y *Accuracy*.
