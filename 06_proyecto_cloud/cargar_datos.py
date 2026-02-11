import pandas as pd
from google.cloud import bigquery
import os

print("Librerías cargadas correctamente.")

#  Para que el script siempre encuentre la llave
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/key.json"

# 1. Configuración de IDs (Ajusta los nombres si es necesario)
project_id = "mlops-learning-2026"
dataset_id = "entrenamiento_nube"
table_name = "Social_Network_Ads" # El nombre que quieras para la tabla

# El table_id es simplemente la unión de los tres con puntos
table_id = f"{project_id}.{dataset_id}.{table_name}"

# 2. Inicializar el cliente (usará tu variable de entorno exportada)
client = bigquery.Client()
print(f"Conectado al proyecto: {client.project}")


# 1. Cargar el archivo CSV
file_path = "Social_Network_Ads.csv"  # <--- CAMBIA ESTO por el nombre de tu archivo
df = pd.read_csv(file_path)

print(f"Archivo leído: {len(df)} filas encontradas.")

# 2. Configurar la carga hacia BigQuery
# Si la tabla no existe, BigQuery la creará automáticamente
job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_TRUNCATE", # Esto sobrescribe la tabla si ya existe
)

print("Iniciando la carga a BigQuery...")

# 3. Mandar los datos
job = client.load_table_from_dataframe(
    df, table_id, job_config=job_config
)

# Esperar a que termine la carga
job.result() 

print(f"¡Éxito! Se cargaron {len(df)} filas en la tabla {table_id}.")
