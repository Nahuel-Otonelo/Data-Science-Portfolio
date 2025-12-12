
# Examen Técnico - Nahuel Otonelo

Este repositorio contiene la solución al examen técnico , implementando un pipeline de datos de criptomonedas usando Docker, Python, PostgreSQL, Pandas y Scikit-learn.

##  Stack Tecnológico

* **Contenerización:** Docker y Docker Compose
* **Lenguaje de Scripting:** Python 3.10+
* **Base de Datos:** PostgreSQL 16
* **Análisis de Datos:** Pandas, Matplotlib, Seaborn, Scikit-learn, Jupyter
* **Librerías de Python:** `requests`, `psycopg2-binary`, `pandas`, `sqlalchemy`, `matplotlib`, `seaborn`, `scikit-learn`, `holidays`, `numpy`
* **Programador de Tareas:** `cron` (ejecutándose dentro de un contenedor Docker)

---

## 1. Configuración del Entorno (Pipeline de Docker)

### Requisitos Previos

* Docker Desktop (corriendo en modo WSL2)
* Git (para clonar y pushear)

### Pasos para la Configuración

1.  **Clonar el Repositorio:**
    ```bash
    git clone [https://github.com/Nahuel-Otonelo/Data-Science-Portfolio](https://github.com/Nahuel-Otonelo/Data-Science-Portfolio)
    cd MLE_Exam 
    ```

2.  **Crear el Archivo `.env`:**
    Este proyecto lee secretos (la API key y la Zona Horaria) desde un archivo `.env`. Copia el archivo `.env.example` y renómbralo a `.env`:
    ```bash
    # (En Windows)
    copy .env.example .env
    ```
    Luego, **edita el archivo `.env`** y añade tu clave real de CoinGecko y tu zona horaria (sin comillas):
    ```
    COINGECKO_API_KEY=CG-tu-clave-real-aqui
    TZ=America/Argentina/Buenos_Aires
    ```

3.  **Crear Carpetas Locales:**
    Los volúmenes de Docker necesitan que existan las carpetas `data` y `logs` en la raíz del proyecto.
    ```bash
    mkdir data
    mkdir logs
    ```

---

## 2. Ejecutar el Pipeline de Datos (Docker)

El `docker-compose.yml` está configurado para levantar todo el entorno de ingesta (la BD y la App de `cron`).

1.  **Levantar los Contenedores:**
    Este comando construirá la imagen de la `app` (instalando Python, `cron` y las librerías de `requirements.txt`) y levantará el servicio de `db` (PostgreSQL 16) y el servicio `app` (que inicia `cron`).
    ```bash
    docker-compose up --build -d
    ```

2.  **Verificar que todo corre:**
    ```bash
    docker ps
    ```
    Deberías ver dos contenedores corriendo: `mutt_db_postgres` (healthy) y `mutt_app_python`.

---

## 3. Tarea 1: Ingesta de Datos (Scripting)

El script principal es `task_1_script.py`, que tiene múltiples modos de operación.

### Tarea 1.1: Descarga de un solo día (Manual)

Puedes ejecutar el script manualmente para un día específico:
```bash
docker-compose exec app python task_1_script.py --coin "bitcoin" --date "2025-10-30"
```

### Tarea 1.2: `cron` (Automatización)

* **Implementación:** El `cron` está **implementado y funcionando** dentro del contenedor `app`.
* **Lógica:** El `entrypoint.sh` del contenedor `app` lee las variables de entorno (`COINGECKO_API_KEY` y `TZ`) y las usa para generar un archivo `crontab` válido. Luego, inicia el servicio `cron`.
* **Configuración:** Está configurado (versión de "producción") para ejecutarse **todos los días a las 3 AM** y guardar los logs en `logs/cron.log`.

### Tarea 1.3: Reprocesamiento Masivo

El script acepta un rango de fechas para la Tarea 1.3.

---

## 4. Tarea 2: Carga de Base de Datos (SQL & Python)

### Tarea 2.1: Crear el Esquema (Tablas)

El archivo `schema.sql` contiene los comandos `CREATE TABLE` para las dos tablas (`coin_raw_data` y `coin_monthly_summary`).

* **Cómo ejecutarlo (Desde el GUI):**
    1.  Conéctate a la base de datos usando un GUI (ver "Conexión al GUI" abajo).
    2.  Abre `schema.sql`, selecciona el código y ejecútalo.
* **Cómo ejecutarlo (Desde la Terminal):**
    ```bash
    type schema.sql | docker-compose exec -T db psql -U user -d crypto_db
    ```

### Tarea 2.2: Cargar Datos en la BD (Pipeline Completo)

El script `task_1_script.py` fue actualizado con la bandera (flag) opcional `--store-db`. Al usarla, el script (además de guardar el `.json`) se conectará a la BD (usando la conexión "interna" `app` -> `db`) e insertará/actualizará los datos usando `INSERT ... ON CONFLICT` ("Upsert").

* **Ejemplo de Carga (365 días de 3 monedas):**
    *Este es el comando que usé para poblar la base de datos para el análisis de la Tarea 4.*
    ```bash
    # 1. Cargar Bitcoin
    docker-compose exec app python task_1_script.py --coin "bitcoin" --start-date "2024-11-04" --end-date "2025-11-03" --store-db
    
    # 2. Cargar Ethereum
    docker-compose exec app python task_1_script.py --coin "ethereum" --start-date "2024-11-04" --end-date "2025-11-03" --store-db
    
    # 3. Cargar Cardano
    docker-compose exec app python task_1_script.py --coin "cardano" --start-date "2024-11-04" --end-date "2025-11-03" --store-db
    ```

---

## 5. Conexión al GUI (DBeaver / VS Code)

La conexión externa a la base de datos está disponible.

La configuración final del `docker-compose.yml` usa `postgres:16` y expone el puerto `5433` (para evitar conflictos con el `5432` local).

**Parámetros de Conexión (para DBeaver o VS Code):**
* **Host:** `127.0.0.1` (o `localhost`)
* **Port:** **`5433`** (¡Importante!)
* **Database:** `crypto_db`
* **Username:** `user`
* **Password:** `pass123` (o la que hayas puesto en tu `docker-compose.yml`)

---

## 6. Tarea 3: Análisis SQL

Las consultas para esta tarea están en el archivo `analysis.sql`.

Estas consultas se pueden copiar y pegar directamente en un GUI (VS Code / DBeaver) y ejecutarlas.

* **Tarea 3.1:** Precio promedio por moneda y mes.
* **Tarea 3.2:** Aumento promedio después de caídas de >3 días, incluyendo el Market Cap (extraído de la columna `full_json_response`).

---

## 7. Tarea 4: Análisis de Datos (Pandas y Scikit-learn)

Este análisis se realiza **fuera de Docker**, en un entorno virtual de Python (`venv`) local, usando el archivo **`Ejercicio_4.ipynb`**.

### 7.1. Instalación (Local)

1.  Crear un entorno virtual:
    ```bash
    python -m venv venv
    ```
2.  Activar el entorno:
    ```bash
    .\venv\Scripts\Activate.ps1
    ```
3.  Instalar las librerías necesarias:
    **Para facilitar la reproducibilidad de este notebook local, se incluye el archivo `requirements-notebook.txt` (que también se subirá al repositorio).**
    ```bash
    pip install -r requirements-notebook.txt
    ```

### 7.2. Tarea 4.1: Gráficos

El notebook (`Ejercicio_4.ipynb`) se conecta a la base de datos (usando la conexión externa al **puerto 5433**) y carga los últimos 30 días de datos (del total de 365 cargados).

Se generan dos gráficos para cumplir con la consigna y, a la vez, demostrar un análisis más profundo:
1.  **Gráfico 1 (Subplots 3x1):** Muestra los **precios absolutos** (cumpliendo la consigna literal).
2.  **Gráfico 2 (Normalizado):** Muestra el **rendimiento** (estilo TradingView) para una mejor comparación visual.

Ambos gráficos se guardan como `.png` en la raíz del proyecto (`task_4_1_price_plot_subplots.png` y `task_4_1_price_plot_normalized.png`), listos para ser subidos a GitHub.

### 7.3. Tarea 4.2 y 4.3: Creación de Features

Para el resto del análisis, el notebook carga el set de datos **completo** (los 365 días / 1095 filas) desde la base de datos al DataFrame `df`.

Se crean las siguientes features:

* **Riesgo (Tarea 4.2.a):** Se implementó una lógica de "High/Medium/Low Risk" basada en la peor caída de 1 día *dentro del mismo mes calendario*.
* **Tendencia/Varianza (Tarea 4.2.b):** Se usó `.rolling(window=7)` para calcular la media móvil y la varianza de los 7 días.
* **Volumen (Tarea 4.3.c):** Se extrajo con éxito el `volume_usd` desde la **columna JSONB**, y se generaron features de tendencia/varianza/asimetría del volumen.
* **Lags (Tarea 4.3):** Se crearon 7 lags (días T-1 a T-7) del precio (`log_price`).
* **Tiempo (Tarea 4.3.b/d):** Se crearon features cíclicas (seno/coseno) para el día de la semana y el mes, y una feature `is_holiday` (para USA y China).

### 7.4. Tarea 4.4: Regresión (Modelo)

* **Limpieza de Datos:** El DataFrame `df` se limpió de `NaNs` (causados por los lags y las ventanas móviles), resultando en un `df_model` final.
* **División (Split):** El `df_model` se dividió en diccionarios (uno por moneda) y se usó `train_test_split` con `shuffle=False` para respetar el orden temporal (80% train, 20% test).
* **Selección de Features:** Se realizó un EDA manual (basado en el Heatmap de Correlación y la Importancia de Features del RandomForest) para reducir la multicolinealidad y el ruido.
* **Entrenamiento:** Se entrenaron y compararon cuatro modelos (`LinearRegression`, `Ridge`, `Lasso`, `RandomForestRegressor`) en el set de `bitcoin`.
* **Resultados:** La Regresión Lineal y Lasso (con un R² de ~0.75 en el *test set*) demostraron ser los mejores modelos para predecir el precio del día siguiente, superando al RandomForest.