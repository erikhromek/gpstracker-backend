FROM python:3.12-alpine

RUN apk update && \
    apk add --no-cache --virtual .build-deps \
    gettext

RUN mkdir -p /opt/gpstracker-backend
WORKDIR /opt/gpstracker-backend

RUN apk add -U tzdata
ENV TZ=America/Buenos_Aires
RUN cp /usr/share/zoneinfo/America/Buenos_Aires /etc/localtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Allows docker to cache installed dependencies between builds
COPY requirements.txt /opt/gpstracker-backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Mounts the application code to the image
COPY . /opt/gpstracker-backend

EXPOSE 8000

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

CMD ["gunicorn", "--config", "gunicorn_config.py", "app.wsgi:application"]
