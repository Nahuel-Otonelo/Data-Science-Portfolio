# Clasificación de Aves con SqueezeNet

Se implementa un pipeline de clasificación de aves a partir de espectrogramas de audio usando **transfer learning** sobre **SqueezeNet 1.1**.

El flujo principal está en el notebook:

- `clasificacion_aves_SqueezeNet.ipynb`

## Objetivo

Clasificar especies de aves a partir de imágenes de espectrogramas, donde:

- eje `x`: tiempo
- eje `y`: frecuencia

## Dataset usado en este proyecto

Estructura esperada por el notebook:

- `Dataset_Imagenes_Robustas/Training`
- `Dataset_Imagenes_Robustas/Validation`

Actualmente, el proyecto utiliza `Training` y `Validation` mediante `ImageFolder`.

## Configuración base (notebook)

- Backbone: `torchvision.models.squeezenet1_1` con pesos `SqueezeNet1_1_Weights.DEFAULT`
- Tamaño de entrada: `224x224`
- Batch size: `64`
- Optimizador: `SGD`
- Learning rates: `lr_features = 1e-5`, `lr_classifier = 1e-4`
- Dispositivo: `MPS`/`CUDA`/`CPU` según disponibilidad

## Estrategia de entrenamiento (2 etapas)

Se implementa una búsqueda progresiva de capas descongeladas.

### Etapa 1: screening rápido

Se entrenan 4 configuraciones durante 8 épocas:

- `classifier_only` (mode `0`)
- `unfreeze_last_4` (mode `4`)
- `unfreeze_last_8` (mode `8`)
- `unfreeze_all` (mode `"all"`)

Output principal:

- `experiments_squeezenet/phase_1_screening/phase_1_results_ranked.pth`

### Etapa 2: refinamiento

Se toman los 2 mejores modos de la etapa 1 y se entrenan 20 épocas.

- Se guarda `classification report` cada 5 épocas (`5, 10, 15, 20`)

Output principal:

- `experiments_squeezenet/phase_2_refinement/phase_2_results_ranked.pth`
- `experiments_squeezenet/two_phase_final_summary.pth`

## Resultados guardados

Cada experimento guarda un `*_summary.pth` con:

- `best_val_acc`, `best_epoch`
- `train_losses`, `val_losses`
- `train_accs`, `val_accs`
- `classification_reports`
- `best_model_state_dict`
- `total_params`, `trainable_params`

Además, se guardan reportes por época en `.txt`:

- `classification_report_epoch_8.txt` (etapa 1)
- `classification_report_epoch_5/10/15/20.txt` (etapa 2)

## Ranking obtenido

### Etapa 1

- `unfreeze_all`: `best_val_acc = 0.6844` (época 8)
- `unfreeze_last_8`: `best_val_acc = 0.6805` (época 8)
- `unfreeze_last_4`: `best_val_acc = 0.6355` (época 8)
- `classifier_only`: `best_val_acc = 0.5499` (época 8)

Top-2 seleccionados para etapa 2: `["all", 8]`.

### Etapa 2

- `unfreeze_all`: `best_val_acc = 0.8432` (época 18)
- `unfreeze_last_8`: `best_val_acc = 0.8107` (época 20)

## Evaluación y análisis

En el notebook se incluye una sección para:

- cargar todos los `*_summary.pth`
- construir una tabla comparativa de métricas
- visualizar curvas (`loss`, `accuracy`) por época
- imprimir `classification_report` por época

También se generó:

- `experiments_squeezenet/phase_2_refinement/unfreeze_all/unfreeze_all_metrics.csv`

con las columnas:

- `epoch, loss, accuracy, val_loss, val_accuracy`
