# 🚀 Guía Rápida: Conexión del IDE Antigravity (Windows) al Kernel de Ubuntu (WSL)

Este instructivo detalla el proceso para usar la interfaz gráfica de Antigravity en Windows, mientras la ejecución real (el Kernel de Python y el acceso a la GPU) se realiza en tu entorno de Ubuntu en WSL.

---

## 1. Verificación Inicial y Ejecución del IDE

Antes de iniciar, debes asegurarte de estar en la carpeta de tu proyecto (`/mnt/c/Users/nahue/Documents/Ceia/NLP/`).

### A. Iniciar Antigravity (La Interfaz Gráfica)

Cada vez que reinicies el sistema, debes lanzar la interfaz de Antigravity desde la terminal de Ubuntu.

1.  **Abre la Terminal de Ubuntu (WSL).**
2.  **Navega a la carpeta principal:**
    ```bash
    cd /mnt/c/Users/nahue/Documents/Ceia/NLP/
    ```
3.  **Lanza la aplicación Antigravity:**
    *(Usando la ruta completa que encontramos)*
    ```bash
    "/mnt/c/Users/nahue/AppData/Local/Programs/Antigravity/Antigravity.exe" .
    ```
    *Esto abrirá la ventana gráfica de Antigravity en tu escritorio de Windows.*

---

## 2. Iniciar el Servidor del Kernel (El Motor de Ubuntu)

Mientras Antigravity está abierto, necesitas iniciar el servicio de Jupyter que actuará como puente.

1.  **Manteniendo abierta la terminal anterior**, ejecuta el siguiente comando para iniciar el servidor en el puerto 8889:
    ```bash
    jupyter notebook --no-browser --port=8889
    ```
2.  **Copia la URL con el Token:**
    La terminal mostrará una URL similar a esta. Debes copiarla completa:
    ```
    http://localhost:8889/tree?token=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    ```

---

## 3. Conexión del IDE al Servidor 🔗

Ahora le indicamos a Antigravity que use el "motor" que acabas de encender.

1.  En la interfaz de **Antigravity** (en Windows), abre tu archivo `.ipynb`.
2.  Busca la opción para **Seleccionar Kernel** o **Cambiar Kernel**.
3.  Selecciona la opción **"Connect to Existing Server"** (Conectar a servidor existente), **"Add Remote Kernel"** o similar.
4.  **Pega la URL completa** (incluyendo el token) que copiaste en el Paso 2.
5.  Haz clic en **Conectar**.

El kernel de tu Notebook ahora estará ejecutándose con la instalación de Python y librerías de tu entorno Ubuntu/WSL.

---

## 🌟 Paso Opcional: Simplificar la Conexión (Contraseña Fija)

Para evitar copiar el token largo cada vez, puedes configurar una contraseña fija para el servidor Jupyter:

1.  **Genera el archivo de configuración** (solo la primera vez):
    ```bash
    jupyter notebook --generate-config
    ```
2.  **Establece una contraseña:**
    ```bash
    jupyter notebook password
    ```
    *(Ingresa tu nueva contraseña cuando se te solicite).*

A partir de ahora, solo tendrás que conectar a `http://localhost:8889/` y Antigravity te pedirá la contraseña.