# Inteligencia Artificial y Bioacústica: Pipeline de Preprocesamiento End-to-End (V7)

Este repositorio documenta el **Análisis Exploratorio de Datos (EDA)** y la construcción integral del *Pipeline* de Ingeniería de Datos para la pre-clasificación de características acústicas (*Feature Extraction*) orientado a arquitecturas competitivas de **Deep Learning** (CNNs 2D y Modelos 1D).

El objetivo de este sistema es extraer, purgar, robustecer y homogeneizar vocalizaciones de aves obtenidas desde cero a partir de grabaciones de campo masivas e imperfectas, garantizando el suministro de datos milimétricamente inalterados para el entrenamiento neuronal.

---

## 1. Naturaleza del Dataset "Salvaje"
El proyecto procesa datos en bruto extraídos colaborativamente a través de **Xeno-canto**, conformados por tres pilares:

1. **`Metadatos Estructurales (.csv)`**: Contexto posicional, fecha, región y calidad biológica.
2. **`Audios Crudos (.mp3)`**: Archivos altamente comprimidos capturados en la intemperie (con viento, lluvia y contaminación acústica urbana u otros animales de fondo).
3. **`Archivos de Anotación (.svl)`**: Archivos XML de la aplicación *Sonic Visualiser*, brindados por expertos. Proveen las *Bounding Boxes* maestras (Ground Truth). La primera capa de nuestra IA involucró un minado de este XML para extraer rangos frecuenciales y el segundo exacto de inicio y fin de cada trino a un mega-dataframe cruzado (`df_master`).

---

## 2. Evolución Arquitectónica del Pipeline (Versión 1 a Versión 7)
Tratar datos desestructurados requiere iteraciones sistémicas para blindar a las redes neuronales frente al exceso ruido físico de las selvas sudamericanas. Este es el recuento histórico de la arquitectura:

### Versión 1 y 2: Parseo y Minería (XML a Tensores)
Establecimos la base de datos Pandas extrayendo con éxito las localizaciones marcadas por los expertos, pasando de un entorno puramente acústico a una tabla matemática accionable donde cada ave representa un recorte temporal (ej: de 4.1s a 6.0s).

### Versión 3 y 4: Invarianza Geométrica 256x256 (El Ecosistema 2D)
A la hora de llevar los cantos de 1-D a espectrogramas perceptuales 2D, descubrimos que aplicar interpolación destructiva por algoritmos de *Computer Vision* (como `cv2.resize`) destruía la integridad frecuencial de alta frecuencia del ave.
* Forzamos el **remuestreo de los audios base a estrictamente `21845 Hz`**.
* Al cortar ventanas temporales de exactamente **6.0 Segundos** y computar la Transformada Rápida de Fourier, logramos generar limpiamente en el Eje X exactamente **256 píxeles de longitud**. Equilibrando los **Mels = 256**, extraemos nativa y paramétricamente matrices de dimensiones perfectas (`256 x 256`) sin necesidad de re-escalar forzosamente *a posteriori*.
* Se implementó el alisado analítico mediante ventana de **Hann**, garantizado internamente por *Librosa* eliminando la clásica "fuga espectral" de bordes duros de un recorte brusco en tiempo.

### Versión 5: La Defensa Inteligente `Sin_Pajaro` (Ruido Abiótico)
Las RNAs hiper-optimizarían buscando al "ave por default" ante cualquier grabación con ruido. Decidimos emparejar el dataset inyectando una Clase Negativa (Control Ambiental).
Dado que tomar tiempos vacíos al azar de la matriz podía terminar ingiriendo un canto no anotado por el ornitólogo (Falso Negativo), introdujimos un filtro de procesamiento de señales avanzado usando **`librosa.feature.spectral_flatness < 0.01`**. El algoritmo rechaza ventanas que tienen firmas acústicas tonales o estructuradas (cantos rítmicos), y admite exclusivamente ventanas con audios caóticos planos o estática pura, creando el dataset de falsos biológicos perfecto.

### Versión 6: Jittering Analítico y El Sistema de Tracking "DNI"
Se introdujeron dos defensas de altísimo calibre investigativo:
1. **Data Augmentation Traslacional (Random Jitter):** Las aves de cantos cortos estaban siendo matemáticamente ubicadas de forma exacta en el centro del eje temporal de la imagen, generándole un sesgo crónico de hiper-fijación especial a las neuronas. Desarrollamos un *Padding estocástico*: ahora el ave inicia en ventanas aleatorias del espectrograma, forzando y enseñando **invarianza traslacional** biológica al modelo de Deep Learning.
2. **Implementación "DNI de Fotos":** Compilamos el rastreo forense. Cada registro 2D y etiqueta fue atada inseparablemente a un `String` exacto detallando su MP3 de origen y el *timestamp* al milisegundo de donde se disparó, lo que permitió hacer depuraciones algorítmicas sin reconstruir todo desde cero.

### Versión 7: La Obra Maestra (Sincronía Bifásica y Curación Taxonómica)
Ante el desafío de testear la topología Visual (CNN 2D) contra un Modelo Auditivo (Red Convolucional 1D), descubrimos vulnerabilidades de sincronización y de pureza taxonómica:
* **Unificación Taxonómica Autónoma:** Al extirpar el "Quality Score" escondido por los ornitólogos en los SVL (indicadores extra como `,9` y `,10` después del linaje de la familia), obligamos computacionalmente al programa a fusionar y consolidar cada familia y clase ruidosa en contenedores homogéneos, asegurando que todos sobrepasen la cuota umbral de 100 cantos por *Label* sin fisuras artificiales.
* **El Quirófano Sincronizado:** Diseñamos el Bucle Final Unificado que, apoyándose en la librería de extracción de C (`librosa.load(offset=...`) supera contundentemente las variables locales *fuera de eje* y garantiza matemáticamente un 100.0% de homología y compatibilidad clonica temporal entre la exportación masiva de `.WAV`s crudos y `.PNGs` a píxel.

---

### Misión Cumplida
El output son múltiples jerarquías unificadas: desde matrices `.NPY` listas para su transposición con tensores, matrices depuradas, hasta clústers de visualización. Un preprocesador blindado, estandarizado, rastreable y perfecto tanto para arquitecturas de imagen como de tiempo continuo.
