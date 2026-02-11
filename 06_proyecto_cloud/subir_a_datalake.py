import os
from google.cloud import storage

# 1. Configuración de seguridad (Usa tu llave de la carpeta secrets)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/key.json"

def subir_a_gcs(nombre_bucket, archivo_local, nombre_destino):
    """Sube un archivo al bucket de Google Cloud Storage."""
    client = storage.Client()
    bucket = client.bucket(nombre_bucket)
    blob = bucket.blob(nombre_destino)

    print(f"Subiendo {archivo_local} a gs://{nombre_bucket}/{nombre_destino}...")
    blob.upload_from_filename(archivo_local)
    print("¡Carga exitosa al Data Lake!")

# --- EJECUCIÓN ---
# El archivo original de tu proyecto
ARCHIVO_CSV = "Social_Network_Ads.csv" 
# Tu bucket recién creado
BUCKET_NAME = "data-lake-mlops-learning-2026" 
# Lo guardamos en una subcarpeta 'raw' para seguir buenas prácticas de MLOps
RUTA_DESTINO = "raw/Social_Network_Ads.csv"

if __name__ == "__main__":
    subir_a_gcs(BUCKET_NAME, ARCHIVO_CSV, RUTA_DESTINO)