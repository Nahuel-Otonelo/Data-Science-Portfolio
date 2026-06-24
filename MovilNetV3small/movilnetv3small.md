MobileNetV3 Small
Entrenamiento y Evaluación

Este notebook contiene la implementación y experimentación de un modelo basado en MobileNetV3 Small para una tarea de clasificación sobre espectrogramas.

Descripción

Se utiliza un modelo preentrenado en ImageNet y se adapta al problema reemplazando la capa final para ajustarse al número de clases objetivo. Se evaluaron dos enfoques:

Fine-tuning parcial: congelando capas iniciales y entrenando solo las últimas (train_depth variable).
Entrenamiento completo: permitiendo que todas las capas del modelo se actualicen.

Configuración del modelo
Arquitectura: MobileNetV3 Small
Loss: CrossEntropyLoss con ponderación por desbalance de clases
Optimización: AdamW
Learning rate: 1e-4
Scheduler: StepLR


Experimentos

Se probaron distintas profundidades de fine-tuning:

train_depth = 3
train_depth = 5
train_depth = 7

En estos casos, solo los últimos bloques convolucionales eran entrenables.

Resultados
Fine-tuning parcial: desempeño bajo (F1 < 0.25)
Entrenamiento completo: mejora significativa (F1 ~ 0.91)

Esto sugiere que las features preentrenadas en ImageNet no son directamente transferibles al dominio de espectrogramas, requiriendo una adaptación completa del modelo.

Contenido del notebook
Carga y preprocesamiento de datos
Definición del modelo
Entrenamiento
Registro de métricas (train_loss, val_loss, val_acc)
Visualización de resultados
Uso

Ejecutar el notebook de forma secuencial. Asegurarse de tener instaladas las dependencias: