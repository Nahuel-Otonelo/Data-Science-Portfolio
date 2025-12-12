#!/bin/sh
# 1. Crear el archivo de cron en /etc/cron.d/
#    Usamos 'printenv' para "volcar" TODAS las variables
#    que docker-compose le pasó (KEY y TZ) al archivo.
#    'cron' lee este archivo al arrancar.
printenv > /etc/environment

# 2. Escribir las TAREAS (¡Versión Producción a las 3 AM!)
#    '0 3 * * *' = minuto 0, hora 3, cada día.
echo "0 3 * * * root cd /app && /usr/local/bin/python /app/task_1_script.py --date \"\$(date -d \"yesterday\" +\%Y-\%m-\%d)\" --coin \"bitcoin\" >> /app/logs/cron.log 2>&1" > /etc/cron.d/my-cron-task
echo "2 3 * * * root cd /app && /usr/local/bin/python /app/task_1_script.py --date \"\$(date -d \"yesterday\" +\%Y-\%m-\%d)\" --coin \"ethereum\" >> /app/logs/cron.log 2>&1" >> /etc/cron.d/my-cron-task
echo "4 3 * * * root cd /app && /usr/local/bin/python /app/task_1_script.py --date \"\$(date -d \"yesterday\" +\%Y-\%m-\%d)\" --coin \"cardano\" >> /app/logs/cron.log 2>&1" >> /etc/cron.d/my-cron-task
echo "" >> /etc/cron.d/my-cron-task

# 3. Dar permisos
chmod 0644 /etc/cron.d/my-cron-task

# 4. Iniciar cron
exec cron -f