# GPSTracker-backend

Repositorio que contiene el backend del sistema de botón antipánico.

## Instalación

Requiere Python >=3.10.
Las siguientes instrucciones son para un sistema del tipo GNU/Linux (Ubuntu, Debian, Fedora, etc.):

- Clonar repositorio, rama de desarrollo
- Requiere una base de datos PostgreSQL >=11
- copiar backend/local_settings.example.py en local_settings.py y definir variables (base de datos, tokens, etc.)
- (por única vez) crear entorno virtual con `python3 -m venv env`
- activar entorno virtual con `source env/bin/activate`
- (por única vez)  instalar dependencias con `pip install -r requirements.txt`
- (por única vez)  correr migraciones con `python manage.py migrate`
- correr servidor con `python manage.py runserver`

Para crear una base de datos contenedorizada (requiere Docker instalado):

```
docker run -d \
	--name gpstracker-postgres -p 5432:5432 \
	-e POSTGRES_PASSWORD={YOUR_PASSWORD} \
	-e PGDATA=/var/lib/postgresql/data/pgdata \
	-v /{YOUR_HOME_FOLDER}/gpstracker-backend/postgresql/data:/var/lib/postgresql/data \
	postgres
```

Reemplazar {YOUR_PASSWORD} por una contraseña de base de datos y {YOUR_HOME_FOLDER} con la dirección del _Home_ del usuario.

## Autores
- Erik Hromek

## License

[MIT](https://choosealicense.com/licenses/mit/)
