# Preprocesamiento de audio para clasificación

## Qué hace `data_preprocessing.ipynb`

El notebook toma un dataset de audio etiquetado por carpetas, lo normaliza para entrenamiento y genera un dataset derivado listo para uso en modelos que requieren audio mono a 16 kHz.

Flujo principal:
1. Lee audios `.wav` desde un dataset origen organizado por split y clase.
2. Re-muestrea cada audio a `16_000 Hz`, fuerza canal mono y limita amplitud a `[-1, 1]`.
3. Conserva el split de entrenamiento original.
4. Divide el split de validación original en `validation` y `test` (50/50 por clase, con semilla fija).
5. Re-exporta audios con nombres de segmento estandarizados.
6. Genera archivos CSV de metadata para todo el dataset y por split.

## Datos que necesita

Estructura de entrada esperada (genérica):

```text
<dataset_origen>/
  <split_entrenamiento>/
    <clase_1>/*.wav
    <clase_2>/*.wav
    ...0
  <split_validacion>/
    <clase_1>/*.wav
    <clase_2>/*.wav
    ...
```

Requisitos de contenido:
- Archivos de audio en formato `.wav`.
- Subcarpetas por clase dentro de cada split.
- Mismas clases representables entre splits.

## Estructura que crea con los datos

Salida esperada (genérica):

```text
<dataset_derivado>/
  audio/
    train/
      seg_000000.wav
      ...
    validation/
      seg_XXXXXX.wav
      ...
    test/
      seg_XXXXXX.wav
      ...
  metadata/
    all_segments.csv
    train.csv
    validation.csv
    test.csv
    class_mapping.csv
```

Contenido de metadata:
- `all_segments.csv`: todos los segmentos exportados.
- `train.csv`, `validation.csv`, `test.csv`: subconjuntos por split.
- `class_mapping.csv`: mapeo `class_id <-> class_name`.

## Qué hace `yamnet_transf.ipynb`

Este notebook implementa transferencia de aprendizaje con YAMNet para clasificación de clips completos.

Flujo principal:
1. Carga YAMNet preentrenado desde TensorFlow Hub.
2. Lee la metadata del dataset derivado (splits y mapeo de clases).
3. Para cada clip, extrae embeddings temporales de YAMNet y los concatena en un único vector por clip.
4. Verifica consistencia de dimensiones entre clips.
5. Construye datasets de TensorFlow para entrenamiento y evaluación.
6. Entrena un clasificador denso (MLP) sobre embeddings concatenados.
7. Evalúa con métricas de clasificación y grafica evolución de `loss/accuracy`.
8. Guarda el modelo entrenado en disco.

## Datos que necesita (`yamnet_transf.ipynb`)

Estructura de entrada esperada (genérica):

```text
<dataset_derivado>/
  audio/
    train/*.wav
    validation/*.wav
    test/*.wav
  metadata/
    train.csv
    validation.csv
    test.csv
    class_mapping.csv
```

Requisitos de contenido:
- Audios mono a `16_000 Hz` (el notebook valida esta condición).
- CSVs con rutas de archivos (`filepath`) y etiquetas (`class_id`, `label`).
- Conectividad para descargar YAMNet desde TensorFlow Hub en la primera carga.

## Estructura que crea con los datos (`yamnet_transf.ipynb`)

Salida principal (genérica):

```text
<directorio_proyecto>/
  models/
    best_temporal_classifier.keras
```

Notas:
- Los gráficos de entrenamiento se muestran en el notebook.
- El reporte de clasificación se imprime en salida estándar.

## Qué hace `modelo_inferencia.ipynb`

Este notebook ejecuta inferencia sobre archivos de audio usando YAMNet + el clasificador entrenado.

Flujo principal:
1. Carga YAMNet desde TensorFlow Hub.
2. Carga el clasificador entrenado guardado en disco.
3. Carga el mapeo de clases para traducir `class_id` a etiqueta.
4. Lee un archivo de audio, lo convierte a mono `16_000 Hz` y construye un clip fijo de 6 s.
5. Extrae embeddings temporales con YAMNet, los concatena y ajusta dimensión si hace falta.
6. Ejecuta predicción, calcula probabilidades (`softmax`) y devuelve ranking de clases.

## Datos que necesita (`modelo_inferencia.ipynb`)

Entradas esperadas (genéricas):

```text
<directorio_proyecto>/
  models/
    best_temporal_classifier.keras
    class_mapping.csv
  <audio_a_inferir>.wav
```

Requisitos de contenido:
- Archivo de modelo entrenado en formato `.keras`.
- Archivo de mapeo de clases con columnas de identificador y etiqueta.
- Audio de entrada legible por `librosa` (se remuestrea a `16_000 Hz` y mono).
- Conectividad para descargar YAMNet desde TensorFlow Hub en la primera carga.

## Estructura que crea con los datos (`modelo_inferencia.ipynb`)

No genera una carpeta de salida obligatoria.

Salida en notebook:
- Clase predicha (`class_id` y etiqueta).
- Tabla de probabilidades por clase, ordenada de mayor a menor.
