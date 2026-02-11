"""
Módulo para cargar datos desde Google Cloud Storage (GCS) hacia Google BigQuery.

Este script automatiza el proceso de transferencia de archivos CSV almacenados
en un bucket de GCS a una tabla específica en BigQuery, utilizando la 
detección automática de esquema y sobrescribiendo los datos existentes.
"""

import os
from google.cloud import bigquery

# 1. Autenticación
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/key.json"

def cargar_gcs_a_bigquery():
    """
    Carga un archivo CSV desde un URI de GCS a una tabla de BigQuery.
    
    Utiliza load_table_from_uri para realizar la carga de forma eficiente,
    configurando la autodetección de esquema y el truncado de la tabla destino.
    """
    client = bigquery.Client()

    # Configuración de IDs
    project_id = 'mlops-learning-2026'
    dataset_id = 'dataset_social_ads'
    table_id = 'tabla_social_ads'
    
    # La ruta ahora es un URI de Google Cloud Storage
    uri = "gs://data-lake-mlops-learning-2026/raw/Social_Network_Ads.csv"
    
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)

    # Configuración del Job de carga
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # Ignoramos el encabezado si ya existe
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE  # Sobreescribe la tabla si ya existe
    )

    print(f"-> Iniciando carga desde {uri}...")

    # El cambio principal: usamos load_table_from_uri
    load_job = client.load_table_from_uri(
        uri, 
        table_ref, 
        job_config=job_config
    )

    load_job.result()  # Espera a que termine el proceso

    destination_table = client.get_table(table_ref)
    print(f"-> Carga finalizada. La tabla tiene {destination_table.num_rows} filas.")

if __name__ == "__main__":
    cargar_gcs_a_bigquery()