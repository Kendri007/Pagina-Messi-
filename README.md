# Pagina-Messi
Pagina de Messi hecha por Kendri Medina, Gazi Saraiddyn y Dylan Ramirez

Aplicación web dinámica basada en Flask que convierte la maquetación estática en un sistema interactivo con SQLite.

## Requisitos
- Python 3.10 o superior
- pip

## Instalación
1. Crear y activar un entorno virtual.
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar la aplicación:
   ```bash
   python app.py
   ```

## Estructura
- app.py: aplicación Flask principal
- wsgi.py: punto de entrada para servidores WSGI
- messi_app.db: base de datos SQLite con datos de prueba
- uploads/: archivos subidos por los usuarios

## Características
- Formularios interactivos con almacenamiento en SQLite
- Operaciones CRUD básicas
- Seguridad contra nombres de archivo inválidos y subida de archivos
- Manejo de errores y mensajes flash
