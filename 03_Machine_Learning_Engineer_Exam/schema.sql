-- Borramos las tablas si ya existen, para que el script
-- se pueda ejecutar varias veces sin errores.
DROP TABLE IF EXISTS coin_monthly_summary;
DROP TABLE IF EXISTS coin_raw_data;


-- --- Tabla 1: Datos Crudos ---
-- Esta tabla almacena el JSON completo de la API para cada día.
CREATE TABLE coin_raw_data (
    -- Usamos VARCHAR(50) para el ID (ej: 'bitcoin', 'ethereum')
    coin_id VARCHAR(50) NOT NULL,
    
    -- Usamos DATE para la fecha (ej: '2025-10-31')
    data_date DATE NOT NULL,
    
    -- El enunciado pide explícitamente el precio en USD por separado
    -- Usamos DECIMAL(20, 10) para alta precisión
    price_usd DECIMAL(20, 10),
    
    -- El enunciado pide el JSON completo.
    -- JSONB es el tipo de dato binario de PostgreSQL,
    -- es más rápido para consultas que el tipo JSON (texto).
    full_json_response JSONB,
    
    -- Creamos una llave primaria compuesta.
    -- Esto garantiza que solo puede haber UNA entrada por moneda y por día.
    PRIMARY KEY (coin_id, data_date)
);


-- --- Tabla 2: Datos Agregados ---
-- Esta tabla almacenará el resumen mensual que pide el enunciado.
CREATE TABLE coin_monthly_summary (
    coin_id VARCHAR(50) NOT NULL,
    
    -- Guardamos el mes como una fecha (ej: '2025-10-01')
    -- Esto es más fácil de consultar que guardar año y mes por separado.
    month_bucket DATE NOT NULL,
    
    -- Guardamos el precio máximo y mínimo de ese mes
    max_price_usd DECIMAL(20, 10),
    min_price_usd DECIMAL(20, 10),
    
    -- Creamos una llave primaria compuesta
    PRIMARY KEY (coin_id, month_bucket)
);
