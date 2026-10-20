# Cómo ejecutar el proyecto

El proyecto utiliza **Streamlit** para la interfaz y **uv** para gestionar las dependencias.

## Requisitos

- Python
- [uv](https://docs.astral.sh/uv/)

## Instalación y ejecución

1. Abrir una terminal en la carpeta raíz del proyecto.
2. Instalar las dependencias:

   ```bash
   uv sync
   ```

3. Ejecutar la aplicación:

   ```bash
   uv run streamlit run home.py
   ```

4. Abrir en el navegador la dirección que muestra la terminal, normalmente:

   `http://localhost:8501`

