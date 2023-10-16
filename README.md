# GPSTracker-backend

Repositorio que contiene el backend del sistema de botón antipánico.

## Instalación

Requiere Python >=3.10.

- Clonar repositorio, rama de desarrollo
- Requiere una base de datos PostgreSQL >=11
- copiar backend/local_settings.example.py en local_settings.py y definir variables (base de datos, tokens, etc.)
- (por única vez) crear entorno virtual con `python3 -m venv env`
- activar entorno virtual con `source env/bin/activate`
- (por única vez)  instalar dependencias con `pip install -r requirements.txt`
- (por única vez)  correr migraciones con `python manage.py migrate`
- correr servidor con `python manage.py runserver`

## Autores
- Erik Hromek

## License

[MIT](https://choosealicense.com/licenses/mit/)
