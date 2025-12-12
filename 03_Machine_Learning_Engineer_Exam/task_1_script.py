import sys
import os
import json
import logging
import argparse
import time 
from datetime import datetime, timedelta 
import requests 
import psycopg2 
from psycopg2 import sql 

def setup_logging():
    """
    Configura el logging para que escriba tanto en la consola
    como en un archivo (logs/app.log).
    """
    os.makedirs('logs', exist_ok=True)
    log_file_path = 'logs/app.log'
    log_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.setLevel(logging.INFO) 

    # 1. Handler para el archivo
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    # 2. Handler para la consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

def get_db_connection():
    """
    Se conecta a la base de datos PostgreSQL usando las variables de entorno.
    """
    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            dbname=os.environ.get('DB_NAME')
        )
        logging.info("Conexión a la base de datos PostgreSQL exitosa.")
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Error al conectar con la base de datos: {e}")
        return None
    except Exception as e:
        logging.error(f"Error inesperado en get_db_connection: {e}")
        return None

def upsert_raw_data(conn, coin_id, date_iso, price_usd, full_json_data):
    """
    Inserta o actualiza (Upsert) los datos crudos en la tabla coin_raw_data.
    """
    query = sql.SQL("""
        INSERT INTO coin_raw_data (coin_id, data_date, price_usd, full_json_response)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (coin_id, data_date) DO UPDATE SET
            price_usd = EXCLUDED.price_usd,
            full_json_response = EXCLUDED.full_json_response;
    """)
    
    try:
        with conn.cursor() as cur:
            json_string = json.dumps(full_json_data)
            cur.execute(query, (coin_id, date_iso, price_usd, json_string))
        conn.commit()
        logging.info(f"Datos 'raw' para {coin_id} en {date_iso} guardados en la BD.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error en upsert_raw_data: {e}")
        raise # Volver a lanzar el error para que la función principal lo vea

def update_monthly_summary(conn, coin_id, date_iso, price_usd):
    """
    Calcula y actualiza (Upsert) el resumen mensual en la tabla coin_monthly_summary.
    """
    month_bucket = datetime.strptime(date_iso, '%Y-%m-%d').strftime('%Y-%m-01')
    
    query = sql.SQL("""
        INSERT INTO coin_monthly_summary (coin_id, month_bucket, min_price_usd, max_price_usd)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (coin_id, month_bucket) DO UPDATE SET
            min_price_usd = LEAST(coin_monthly_summary.min_price_usd, EXCLUDED.min_price_usd),
            max_price_usd = GREATEST(coin_monthly_summary.max_price_usd, EXCLUDED.max_price_usd);
    """)
    
    try:
        with conn.cursor() as cur:
            cur.execute(query, (coin_id, month_bucket, price_usd, price_usd))
        conn.commit()
        logging.info(f"Resumen mensual para {coin_id} en {month_bucket} actualizado.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error en update_monthly_summary: {e}")
        raise # Volver a lanzar el error

def fetch_crypto_data(api_key, coin_id, date_iso, store_db=False): 
    """
    Llama a la API de CoinGecko y (opcionalmente) guarda en la BD.
    Devuelve True si tiene éxito, False si falla.
    """
    # 1. Validar y formatear la fecha
    try:
        logging.info(f"Fecha recibida (ISO): {date_iso}")
        date_obj = datetime.strptime(date_iso, '%Y-%m-%d')
        date_api_format = date_obj.strftime('%d-%m-%Y')
        logging.info(f"Fecha formateada (API): {date_api_format}")
    except ValueError:
        logging.error(f"Formato de fecha incorrecto: '{date_iso}'.")
        return False

    # 2. Construir la URL y parámetros
    base_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/history"
    params = {
        'date': date_api_format,
        'x_cg_demo_api_key': api_key
    }

    # 3. Llamar a la API
    # Usamos un 'try...except' general aquí para la llamada a la API
    try:
        logging.info(f"Llamando a la API para {coin_id} en la fecha {date_api_format}...")
        response = requests.get(base_url, params=params)
        response.raise_for_status() 
        logging.info("¡Éxito! Respuesta recibida de la API.")
        data = response.json()

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"Error HTTP: {http_err} - {response.text}")
        return False
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Error de Conexión/Request: {req_err}")
        return False
    except Exception as e:
        logging.exception(f"Ocurrió un error inesperado al llamar a la API: {e}")
        return False

    # 4. Guardar los datos en un archivo (como antes)
    try:
        os.makedirs('data', exist_ok=True)
        output_filename = f"data/{coin_id}-{date_iso}.json"
        logging.info(f"Guardando datos en {output_filename}...")
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info(f"Datos guardados exitosamente en {output_filename}.")
    
    except Exception as e:
        logging.exception(f"Error al escribir el archivo: {e}")
        # No devolvemos 'False' aquí, porque el guardado en BD
        # aún podría funcionar.

    # 5. Guardar en la Base de Datos (si se pidió)
    if store_db:
        logging.info("Flag --store-db detectada. Guardando en Base de Datos...")
        conn = None
        try:
            price_usd = data.get('market_data', {}).get('current_price', {}).get('usd')
            
            if price_usd is None:
                logging.warning(f"No se encontró 'price_usd' en la respuesta JSON para {date_iso}. Saltando guardado en BD.")
                return False 

            conn = get_db_connection()
            if conn:
                # Usamos un 'try...finally' para asegurarnos de cerrar la conexión
                try:
                    # Ejecutar la Tarea 2.2 (Parte 1: Upsert Raw)
                    upsert_raw_data(conn, coin_id, date_iso, price_usd, data)
                    
                    # Ejecutar la Tarea 2.2 (Parte 2: Upsert Summary)
                    update_monthly_summary(conn, coin_id, date_iso, price_usd)
                    
                    logging.info(f"Datos para {date_iso} guardados exitosamente en la BD.")
                
                except Exception as db_e:
                    logging.error(f"Error durante la transacción de BD para {date_iso}: {db_e}")
                    return False # Si la BD falla, marcamos el día como fallido
                finally:
                    if conn:
                        conn.close()
                        logging.debug("Conexión a la BD cerrada.")
            else:
                logging.error("No se pudo establecer conexión con la BD. Saltando guardado.")
                return False

        except Exception as e:
            logging.exception(f"Error inesperado al guardar en la BD: {e}")
            return False
                
    return True

# --- ¡FUNCIÓN CORREGIDA! ---
def process_date_range(api_key, coin_id, start_date_iso, end_date_iso, store_db=False):
    """
    (TAREA 1.3) Itera sobre un rango de fechas y llama a fetch_crypto_data para cada día.
    """
    logging.info(f"--- Iniciando procesamiento masivo para '{coin_id}' ---")
    logging.info(f"Rango: {start_date_iso} a {end_date_iso}")
    
    try:
        start_date = datetime.strptime(start_date_iso, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_iso, '%Y-%m-%d')
    except ValueError:
        logging.error("Formato de fecha incorrecto para el rango. Use AAAA-MM-DD.")
        return

    if start_date > end_date:
        logging.error("La fecha de inicio no puede ser posterior a la fecha de fin.")
        return

    total_days = (end_date - start_date).days + 1
    current_date = start_date
    day_count = 1
    success_count = 0

    logging.info(f"Total de días a procesar: {total_days}")

    while current_date <= end_date:
        date_iso = current_date.strftime('%Y-%m-%d')
        logging.info(f"--- (Día {day_count}/{total_days}) Procesando: {date_iso} ---")
        
        # --- ¡AQUÍ ESTÁ EL ARREGLO! ---
        # El 'try...except' debe envolver la llamada a la función
        # para que el bucle continúe si un día falla.
        try:
            if fetch_crypto_data(api_key, coin_id, date_iso, store_db):
                success_count += 1
            else:
                logging.warning(f"Falló el procesamiento para el día {date_iso}.")
                
        except Exception as e:
            # Loguear si un día específico falla, pero continuar con el resto
            logging.error(f"Fallo grave al procesar el día {date_iso}: {e}")
        
        # Estas líneas DEBEN estar FUERA del 'try...except'
        # para asegurar que el bucle avance.
        current_date += timedelta(days=1)
        day_count += 1
        
        # Pausa amigable con la API
        if current_date <= end_date: # No dormir después del último día
             time.sleep(2) 

    logging.info("--- Procesamiento masivo finalizado ---")
    logging.info(f"Días procesados exitosamente: {success_count}/{total_days}")


def main():
    """
    Función principal del script.
    """
    setup_logging()
    logging.info("--- Inicio del script ---")

    # 1. Leer la API key (igual que antes)
    api_key = os.environ.get('COINGECKO_API_KEY')
    if not api_key:
        try:
            with open('.env') as f:
                for line in f:
                    if line.startswith('COINGECKO_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip("'\"")
                        logging.info("API key cargada desde archivo .env local.")
                        os.environ['COINGECKO_API_KEY'] = api_key
                        break
        except FileNotFoundError:
            pass 
    if not api_key:
        logging.error("Variable de entorno 'COINGECKO_API_KEY' no encontrada.")
        sys.exit(1) 

    # 2. Configurar los argumentos
    parser = argparse.ArgumentParser(
        description="Descarga datos históricos de CoinGecko API."
    )
    parser.add_argument(
        "--coin",
        required=True,
        help="El ID de la moneda (ej: bitcoin, ethereum)"
    )
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--date",
        help="(Modo 1) Un solo día para descargar (formato: AAAA-MM-DD)"
    )
    mode_group.add_argument(
        "--start-date",
        help="(Modo 2) Fecha de inicio para el rango (formato: AAAA-MM-DD)"
    )
    
    parser.add_argument(
        "--end-date",
        help="(Modo 2) Fecha de fin para el rango (formato: AAAA-MM-DD)"
    )
    
    parser.add_argument(
        "--store-db",
        action="store_true", 
        help="(Opcional) Guardar los datos descargados en la base de datos PostgreSQL."
    )
    
    args = parser.parse_args()
    
    # 3. Lógica de ejecución
    try:
        if args.date:
            # Modo 1: Tarea 1.1 (Un solo día, usado por cron)
            if args.start_date or args.end_date:
                logging.error("Error: No se puede usar --date junto con --start-date o --end-date.")
                parser.print_help()
                sys.exit(1)
            
            logging.info("Ejecutando en modo de un solo día (cron).")
            fetch_crypto_data(api_key, args.coin, args.date, args.store_db)
            
        elif args.start_date and args.end_date:
            # Modo 2: Tarea 1.3 (Rango de días)
            logging.info("Ejecutando en modo de rango (bulk).")
            process_date_range(api_key, args.coin, args.start_date, args.end_date, args.store_db)
            
        elif args.start_date and not args.end_date:
            # Error
            logging.error("Error: --start-date debe usarse junto con --end-date.")
            parser.print_help()
            sys.exit(1)
            
        else:
            logging.error("Argumentos inválidos.")
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        logging.exception(f"Error general no capturado en main: {e}")
    
    logging.info("--- Fin del script ---")


if __name__ == "__main__":
    main()