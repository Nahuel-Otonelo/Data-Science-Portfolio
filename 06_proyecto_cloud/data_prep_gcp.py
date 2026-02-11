import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os
from google.cloud import storage
import io

# --- CONFIGURACIÓN ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/key.json"
BUCKET_NAME = 'data-lake-mlops-learning-2026'
FILE_NAME = 'raw/Social_Network_Ads.csv'

def load_data_from_gcs():
    """Descarga el CSV desde el bucket directamente a la memoria RAM."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(FILE_NAME)
    
    # download_as_text() es un método que trae el contenido del archivo como un string gigante
    content = blob.download_as_text()
    
    # io.StringIO actúa como un "archivo virtual" para que Pandas lo pueda leer
    return pd.read_csv(io.StringIO(content))

def save_csv_to_gcs(df, folder, filename):
    """Sube un DataFrame como CSV al bucket sin guardarlo en el disco local."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    path = f"{folder}/{filename}"
    blob = bucket.blob(path)
    
    # upload_from_string() toma el texto del CSV y lo envía por red al bucket
    blob.upload_from_string(df.to_csv(index=False), 'text/csv')
    print(f"-> Archivo guardado: gs://{BUCKET_NAME}/{path}")

def save_scaler_to_gcs(scaler, filename):
    """Sube el objeto scaler (binario) al bucket usando un buffer de bytes."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    path = f"artifacts/{filename}"
    blob = bucket.blob(path)
    
    # io.BytesIO() crea un espacio en RAM para datos binarios (no texto)
    buffer = io.BytesIO()
    joblib.dump(scaler, buffer)
    buffer.seek(0) # Volvemos al inicio del buffer antes de subirlo
    
    blob.upload_from_file(buffer, content_type='application/octet-stream')
    print(f"-> Artefacto guardado: gs://{BUCKET_NAME}/{path}")

def prepare_data():
    # 1. Ingesta desde Capa Bronze
    df = load_data_from_gcs()
    
    # 2. Limpieza básica
    df = df.drop('User ID', axis=1, errors='ignore')
    df['Gender'] = df['Gender'].map({'Male': 1, 'Female': 0})
    
    X = df[['Gender', 'Age', 'EstimatedSalary']]
    y = df['Purchased'].astype(int)

    # 3. Split (Semilla 42 para reproducibilidad)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 4. Escalado (Solo variables numéricas continuas)
    COLUMNS_TO_SCALE = ['Age', 'EstimatedSalary']
    scaler = StandardScaler()
    
    # fit_transform aprende la media y desviación en train; transform las aplica a test
    X_train.loc[:, COLUMNS_TO_SCALE] = scaler.fit_transform(X_train[COLUMNS_TO_SCALE])
    X_test.loc[:, COLUMNS_TO_SCALE] = scaler.transform(X_test[COLUMNS_TO_SCALE])
    
    # 5. Guardar Artefactos y Capa Silver
    save_scaler_to_gcs(scaler, 'scaler.joblib')
    
    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)
    
    save_csv_to_gcs(train_df, 'processed', 'train_scaled.csv')
    save_csv_to_gcs(test_df, 'processed', 'test_scaled.csv')
    
    print("\n✅ Preprocesamiento en la nube finalizado.")

if __name__ == "__main__":
    prepare_data()