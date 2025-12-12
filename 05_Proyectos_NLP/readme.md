
# 📰 Proyecto 1: Clasificación de Texto con Naive Bayes (Dataset 20 Newsgroups)

Este proyecto es el primer desafío de la materia Procesamiento de Lenguaje Natural (PLN).

El notebook `Desafio_1.ipynb` explora la vectorización de texto (TF-IDF), la similaridad de documentos, la implementación de clasificadores (k-NN y Naive Bayes) y la optimización de hiperparámetros.

## 📊 Dataset

Se utilizó el dataset **20 Newsgroups**, cargado directamente desde `scikit-learn`. Este es un conjunto clásico para la clasificación de texto, compuesto por ~18,000 mensajes de foros distribuidos en 20 categorías temáticas (ej. `rec.autos`, `sci.med`, `talk.politics.misc`).

---


# 💬 Desafío 2: Embeddings de Palabras con Word2Vec (Martín Fierro)

Este proyecto es el segundo desafío de la materia, enfocado en la creación y análisis de embeddings de palabras personalizados.

El notebook `Desafio_2.ipynb` implementa la librería `Gensim` para entrenar un modelo **Word2Vec (Skip-gram)**, utilizando un corpus de texto en español.

## 📖 Dataset

Se utilizó un corpus personalizado compuesto por las dos obras de José Hernández: **"El Gaucho Martín Fierro"** y **"La Vuelta de Martín Fierro"**.

Los textos se obtuvieron del sitio `textos.info` en formato `.epub`, se convirtieron a `.txt` con una herramienta online y se limpiaron manualmente para retener únicamente los versos del poema.

## 🛠️ Desafíos y Metodología

### 1. Preprocesamiento del Corpus (El Desafío Clave)

La estrategia para solucionar el inconveniente de versos cortos, fue tratar el poema como un solo bloque de **"prosa"** continuo:

* Se **reemplazaron todos los saltos de línea (`\n`) por espacios**, creando un único string de texto.
* Se utilizó **`text_to_word_sequence` de Keras/TensorFlow** para tokenizar. Esta función se eligió porque:
    1.  Maneja correctamente caracteres especiales (como la `ü` en "vigüela"), a diferencia del filtro `.isalpha()` de NLTK. No reconoció vigüela pero si otras...
    2.  **No elimina las *stop words*** (como "el", "la", "que"), que son cruciales para que Word2Vec aprenda el contexto gramatical que nos faltaba. En una iteracion anterior de este trabajo, habia eliminado stop words y daba valores inconsistentes de similaridad.
* La lista gigante de tokens se dividió en **"fragmentos" (chunks)** de 100 palabras cada uno, que fueron los "documentos" que se pasaron a Gensim.

### 2. Entrenamiento de Word2Vec (Gensim)

Se ajustaron los hiperparámetros del modelo `Word2Vec` (Skip-gram) para un corpus denso pero pequeño. Establecemos:

* `min_count=3`
* `window=5` (para capturar el contexto de la prosa)
* `vector_size=10

---

# 🤖 Desafío 3: Modelos de Lenguaje a Nivel de Caracteres (RNN, LSTM, GRU)

Este proyecto es el tercer desafío de la materia, centrado en la generación de texto utilizando modelos secuenciales profundos en PyTorch.

El notebook `desafio_3.ipynb` implementa y compara tres arquitecturas de redes neuronales recurrentes: **RNN**, **LSTM** y **GRU**, entrenadas para predecir el siguiente caracter en una secuencia.

## 📖 Dataset

Como corpus, se utilizo el  **"Robinson Crusoe"** de Daniel Defoe, descargado de textos.info.

## 🛠️ Desafíos y Metodología

### 1. Implementación en PyTorch

Se definieron tres clases de modelos (`RNNModel`, `LSTMModel`, `GRUModel`), todas compartiendo una estructura similar pero variando en la capa recurrente:
*   **Embedding**: One-hot encoding de los caracteres.
*   **Capa Recurrente**: RNN, LSTM o GRU.
*   **Dropout**: Se incorporó una capa de `Dropout(0.1)` para regularización


### 2. Entrenamiento

Se creó una función de entrenamiento reutilizable `train_and_evaluate` que incluye:
*   **Early Stopping**: Basado en la perplejidad del conjunto de validación (paciencia de 5 epochs).
*   **Checkpointing**: Guardado automático del mejor modelo.
*   **Visualización**: Gráficos de la evolución de la perplejidad.

### 3. Generación de Texto (Beam Search)

Se implementó un algoritmo de **Stochastic Beam Search** para generar texto, permitiendo controlar la aleatoriedad mediante un parámetro de **temperatura**.

--- 

# 🌐 Desafío 4: Traductor Inglés-Español con LSTM (Seq2Seq)

Este proyecto es el cuarto desafío de la materia, enfocado en la construcción de un modelo de traducción automática  utilizando una arquitectura **Encoder-Decoder**.

El notebook `desafio_4.ipynb` implementa un modelo **Seq2Seq con capas LSTM** en Keras/TensorFlow, optimizado para manejar un volumen considerable de datos sin saturar los recursos de memoria.

## 📖 Dataset

Se utilizó el dataset del **Tatoeba Project** (par inglés-español), que consiste en miles de oraciones traducidas.
Para este desafío, se logró escalar el entrenamiento a **25,000 pares de oraciones** (frente a las 6,000 originales), gracias a las optimizaciones de memoria implementadas.

## 🛠️ Desafíos y Metodología

### 1. Optimización de Memoria (El Cambio Crítico)

El principal obstáculo técnico fue el consumo de RAM al intentar escalar el dataset. El enfoque original utilizaba *Categorical Crossentropy*, lo que obligaba a convertir las secuencias de salida a matrices *One-Hot* gigantescas ($N_{samples} \times L_{sequence} \times V_{vocab}$).

**Solución:** Se migró a **`sparse_categorical_crossentropy`**. Esto permitió trabajar directamente con los índices enteros de los tokens, reduciendo drásticamente el uso de memoria y permitiendo cuadruplicar el tamaño del dataset de entrenamiento.

### 2. Arquitectura del Modelo (Encoder-Decoder)

Se diseñó una arquitectura Seq2Seq clásica pero robusta:
*   **Embeddings Pre-entrenados**: Se utilizaron vectores **GloVe** (Twitter 27B, 50d) para inicializar la capa de embedding del encoder, aprovechando conocimiento semántico previo.
*   **Encoder**: Una capa LSTM que procesa la secuencia de entrada y pasa sus estados internos ($h$, $c$) al decoder.
*   **Decoder**: Una capa LSTM que genera la traducción paso a paso, condicionada por los estados del encoder y la palabra generada anteriormente.
*   **Regularización**: Se incorporó **Dropout (0.2)** en las celdas LSTM para mitigar el sobreajuste, crucial dado que las oraciones son cortas y repetitivas.
### 3. Entrenamiento Inteligente
En lugar de un entrenamiento fijo, se implementó una estrategia dinámica:
*   **Early Stopping**: Monitoreo de la `val_loss` con paciencia de 3 épocas para detener el entrenamiento cuando el modelo deja de aprender.
*   **Model Checkpoint**: Guardado automático de los **mejores pesos** (`translator_model_best.weights.h5`), asegurando que el modelo final sea el óptimo y no simplemente el último.

## 📊 Resultados e Inferencia

Se construyó una **infraestructura de inferencia separada** que reutiliza los pesos entrenados pero desacopla el encoder y el decoder. Esto permite realizar la traducción paso a paso (*step-by-step decoding*), inyectando la predicción actual como entrada para el siguiente paso temporal hasta encontrar el token de fin de oración `<eos>`.

**🚀 Modelo Pre-entrenado Disponible**
El repositorio incluye el archivo `translator_model_best.weights.h5` (~76MB) con los pesos del modelo ya entrenado.
*   **No es necesario re-entrenar:** El notebook detecta automáticamente si este archivo existe. Si es así, carga los pesos y salta directamente a la sección de inferencia, permitiendo probar las traducciones de inmediato.
*   **Resultados:** El modelo es capaz de generar traducciones coherentes para oraciones dentro del dominio del dataset de entrenamiento.