import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os
from google.cloud import storage
import io

# --- CONFIGURACIÓN CLOUD ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/key.json"
BUCKET_NAME = 'data-lake-mlops-learning-2026'
FILE_NAME = 'raw/Social_Network_Ads.csv'

def get_storage_client():
    return storage.Client()

def load_data():
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(FILE_NAME)
    
    # Bajamos el CSV a memoria
    content = blob.download_as_text()
    print(f"-> Leyendo desde GCS: gs://{BUCKET_NAME}/{FILE_NAME}")
    return pd.read_csv(io.StringIO(content))

def save_data(df, filename):
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    # Guardamos en la subcarpeta 'processed'
    ruta_destino = f'processed/{filename}'
    blob = bucket.blob(ruta_destino)
    
    # Subimos el dataframe como CSV
    blob.upload_from_string(df.to_csv(index=False), 'text/csv')
    print(f"-> Guardando datos procesados: gs://{BUCKET_NAME}/{ruta_destino}")

def save_artifact(obj, filename):
    """Guarda el scaler (.joblib) directamente en el bucket."""
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)
    ruta_destino = f'artifacts/{filename}'
    blob = bucket.blob(ruta_destino)
    
    # Usamos un buffer temporal para no guardar nada en el disco local de Ubuntu
    buffer = io.BytesIO()
    joblib.dump(obj, buffer)
    buffer.seek(0)
    
    blob.upload_from_file(buffer, content_type='application/octet-stream')
    print(f"-> Guardando artefacto: gs://{BUCKET_NAME}/{ruta_destino}")

def prepare_data():
    # 1. Cargar datos desde la Capa Bronze
    df = load_data()
    
    # 2. Preprocesamiento (Tu lógica exacta)
    df = df.drop('User ID', axis=1, errors='ignore')
    df['Gender'] = df['Gender'].apply(lambda x: True if x == 'Male' else False)
    y = df['Purchased'].astype(int)
    X = df[['Gender', 'Age', 'EstimatedSalary']]

    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 4. Escalado
    COLUMNS_TO_SCALE = ['Age', 'EstimatedSalary']
    scaler = StandardScaler()
    
    X_train.loc[:, COLUMNS_TO_SCALE] = scaler.fit_transform(X_train[COLUMNS_TO_SCALE])
    X_test.loc[:, COLUMNS_TO_SCALE] = scaler.transform(X_test[COLUMNS_TO_SCALE])
    
    # 5. Guardar Scaler (Artefacto para producción)
    save_artifact(scaler, 'scaler.joblib')
    
    # 6. Guardar CSVs procesados (Capa Silver)
    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)
    
    save_data(train_df, 'train_scaled.csv')
    save_data(test_df, 'test_scaled.csv')
    
    print("\n✅ Pipeline Cloud finalizado correctamente.")

if __name__ == "__main__":
    prepare_data()