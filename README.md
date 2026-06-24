# Identificación de Especies de Aves mediante Análisis de Espectrogramas

## Sobre el Proyecto
Este proyecto aborda la clasificación automatizada de cantos de aves mediante técnicas de aprendizaje profundo (*Deep Learning*). El desafío nativo de procesamiento de señales bioacústicas se formula metodológicamente como una tarea de Visión por Computadora (*Computer Vision*). 

Para ello, las señales acústicas unidimensionales son generadas como representaciones de tiempo-frecuencia bidimensionales estáticas (Espectrogramas Mel). A partir de esta transformación biológica, se implementan y evalúan rigurosamente múltiples arquitecturas de Redes Neuronales Convolucionales (ResNet-18, MobileNetV3-small, SqueezeNet y YAMNet) para contrastar el nivel de exactitud general, el impacto paramétrico del modelo en las métricas de clasificación, y la pertinencia formal del aprendizaje por transferencia (*Transfer Learning*) sobre este ecosistema.

## Origen de los Datos (Dataset)
La base experimental empleada deriva del conjunto de datos estructurado por Loris Jeantet y Emmanuel Dufourq (2023). Estos autores recopilaron y delimitaron grabaciones acústicas de máxima calificación (Categoría A) provenientes originariamente del catálogo colaborativo mundial **Xeno-canto**.

Para los propósitos específicos de nuestra investigación, se ejecutó un filtrado minucioso de sus metadatos con el fin de asilar un dataset controlado y equilibrado, consolidando el corpus de evaluación final con 13 especies aviares correspondientes al orden Passeriformes. De manera adicional, se implementó una decimocuarta clase analítica sintética de control negativo denominada `Sin_Pajaro`, constituida exclusivamente por ondas de ruido ambiental estático o viento empírico.

🔗 **Enlace Oficial al Repositorio de Descarga (Zenodo):** [Manually labeled Bird song dataset of 22 species from Xeno-canto](https://zenodo.org/records/7828148)

## Estructura Sistemática del Repositorio
El trabajo de código se segmenta de forma modular en las siguientes cuatro vertientes operativas:

* **`EDA_y_generacion_espectrogramas/`**
  Contiene los cuadernos de Análisis Exploratorio de Datos (EDA) y la ingeniería de características original. Implementa la ingesta de las ondas sonoras con la librería `librosa`, normaliza los encuadres silvícolas en la ventana uniforme y predeterminada de 6.0 segundos (utilizando mitigación algorítmica de sesgos vía re-enmarque aleatorio / *Jittering temporal*), y finalmente realiza la consolidación local de las matrices o imágenes PNG.

* **`Modelo_Resnet_18/`** 
  Constituye el entorno de reentrenamiento absoluto para el modelo base ResNet-18. Dada su enorme complejidad como matriz limitante (Baseline), el análisis aquí reportó la precisión (*Accuracy*) máxima durante la fase teórica principal a través de un esquema de *Fine-Tuning* general.

* **`MovilNetV3small/`**
  Directorio que evalúa estrictamente el despliegue del modelo ultraligero *MobileNetV3*. Se orienta en medir las limitantes o rendimientos conservados en un sistema que disminuyó sustancialmente su arquitectura y cantidad de capas de procesamiento.

* **`YAMNet/`**
  Integra los scripts de desarrollo correspondientes a YAMNet. En contraposición a las primeras metodologías fotográficas, este último modelo funciona matemáticamente en su propio paradigma, ejecutando una recolección puramente estática de los tensores de audio sin calibrarse a una meta externa.
