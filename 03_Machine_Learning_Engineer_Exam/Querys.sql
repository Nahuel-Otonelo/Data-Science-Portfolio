-- --- Tarea 3.1: Precio promedio por moneda y por mes ---
-- Esta consulta calcula el precio promedio (AVG)
-- agrupando por moneda (coin_id) y por el inicio del mes.
-- Usamos ROUND(..., 2) para redondear el promedio a 2 decimales.

SELECT 
    coin_id, 
    DATE_TRUNC('month', data_date) AS month_bucket, 
    ROUND(AVG(price_usd), 2) AS avg_price
FROM 
    coin_raw_data
GROUP BY 
    coin_id, 
    month_bucket
ORDER BY 
    coin_id, 
    month_bucket;

-- --- Tarea 3.2: Aumento promedio después de caídas de >3 días ---
-- Esta es una consulta compleja que usa CTEs (Common Table Expressions)
-- y Funciones de Ventana (Window Functions) para encontrar las rachas de caídas.

WITH 
-- Paso 1: Calcular el cambio de precio diario y marcar las caídas
daily_changes AS (
    SELECT 
        coin_id,
        data_date,
        price_usd,
        -- Usamos LAG() para obtener el precio del día anterior
        LAG(price_usd, 1) OVER (PARTITION BY coin_id ORDER BY data_date) AS prev_day_price
    FROM 
        coin_raw_data
),
drop_flags AS (
    SELECT 
        *,
        -- Marcamos '1' si el precio cayó, '0' si subió o se mantuvo
        CASE 
            WHEN price_usd < prev_day_price THEN 1
            ELSE 0
        END AS is_price_drop
    FROM 
        daily_changes
),
-- Paso 2: Agrupar las caídas consecutivas (Técnica "Gaps and Islands")
drop_groups AS (
    SELECT 
        *,
        -- Creamos un "ID de grupo" para cada racha de caídas
        SUM(CASE WHEN is_price_drop = 0 THEN 1 ELSE 0 END) 
            OVER (PARTITION BY coin_id ORDER BY data_date) AS drop_group_id
    FROM 
        drop_flags
),
-- Paso 3: Contar la duración de cada racha de caídas
drop_streaks AS (
    SELECT 
        *,
        -- Contamos cuántos días hay en esta racha
        COUNT(*) OVER (PARTITION BY coin_id, drop_group_id) AS drop_length
    FROM 
        drop_groups
    WHERE 
        is_price_drop = 1 -- Solo nos importan los días que SÍ cayeron
),
-- Paso 4: Encontrar el final de las rachas de >3 días
end_of_long_streaks AS (
    SELECT 
        *,
        -- Obtenemos el precio del día SIGUIENTE (la "recuperación")
        LEAD(price_usd, 1) OVER (PARTITION BY coin_id ORDER BY data_date) AS next_day_price,
        -- Numeramos los días de la racha en orden descendente
        ROW_NUMBER() OVER (PARTITION BY coin_id, drop_group_id ORDER BY data_date DESC) as rn_desc
    FROM 
        drop_streaks
    WHERE 
        drop_length > 3 -- Solo rachas de más de 3 días
),
-- Paso 5: Calcular el aumento de la recuperación
recovery_gains AS (
    SELECT
        coin_id,
        price_usd AS price_at_bottom,
        next_day_price AS price_after_recovery,
        (next_day_price - price_usd) AS price_increase
    FROM
        end_of_long_streaks
    WHERE
        rn_desc = 1 -- Nos quedamos solo con el ÚLTIMO día de la racha (el "fondo")
        AND next_day_price IS NOT NULL
        AND next_day_price > price_usd -- Solo contamos si el precio SÍ aumentó
),
-- Paso 6: Calcular el promedio de esos aumentos
avg_recovery_by_coin AS (
    SELECT 
        coin_id,
        AVG(price_increase) AS avg_price_increase
    FROM 
        recovery_gains
    GROUP BY 
        coin_id
),
-- Paso 7: Obtener el Market Cap "Actual" (el más reciente)
current_market_cap AS (
    SELECT 
        DISTINCT ON (coin_id) -- Tomar solo la primera fila por moneda
        coin_id,
        -- (->>) es el operador de JSONB para extraer texto
        (full_json_response -> 'market_data' -> 'market_cap' ->> 'usd')::DECIMAL AS latest_market_cap_usd
    FROM 
        coin_raw_data
    ORDER BY 
        coin_id, data_date DESC -- Ordenar por fecha descendente para que la "primera" sea la más nueva
)
-- Paso 8: Unir (JOIN) los resultados
SELECT 
    arc.coin_id,
    ROUND(arc.avg_price_increase, 2) AS avg_recovery_gain_usd,
    cmc.latest_market_cap_usd
FROM 
    avg_recovery_by_coin AS arc
JOIN 
    current_market_cap AS cmc ON arc.coin_id = cmc.coin_id;
