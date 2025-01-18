given following 

=docker-compose-deploy.yml=

version: "3.9"

services:
  app:
    build:
      context: .
    restart: always
    volumes:
      - static-data:/vol/web
      - media-data:/vol/web/media
    environment:
      - DB_HOST=db
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASS=${DB_PASS}
      - SECRET_KEY=${DJANGO_SECRET_KEY}
      - ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS}
    depends_on:
      - db

  db:
    image: postgres:13-alpine
    restart: always
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASS}

  proxy:
    build:
      context: ./proxy
    restart: always
    depends_on:
      - app
    ports:
      - 80:8000
    volumes:
      - static-data:/vol/static
      - media-data:/vol/web/media

volumes:
  postgres-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ../data/deploy/db
  static-data:
  media-data:

=Dockerfile=

FROM python:3.9-alpine3.13
LABEL maintainer="londonappdeveloper.com"

ENV PYTHONUNBUFFERED 1

ARG UID=101
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./scripts /scripts
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --uid $UID \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol/web && \
    chmod -R 755 /vol/web && \
    chmod -R +x /scripts

ENV PATH="/scripts:/py/bin:$PATH"

USER django-user

VOLUME /vol/web/media
VOLUME /vol/web/static

CMD ["run.sh"]

=scripts/run.sh=

#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate

uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi

=========

when I run

docker compose -f docker-compose-deploy.yml build
docker compose -f docker-compose-deploy.yml up -d

I get following output for app service:

2025-01-17 01:28:03 exec /scripts/run.sh: no such file or directory
2025-01-17 01:28:10 exec /scripts/run.sh: no such file or directory

****************************

I've converted all CR LF to LF in all .sh files.
I've rebuild images:
docker compose -f docker-compose-deploy.yml build
Service app now runs correctly.
However there is still problem with proxy service:

2025-01-17 20:54:55 /docker-entrypoint.sh: exec: line 47: /run.sh: not found
2025-01-17 20:55:05 /docker-entrypoint.sh: exec: line 47: /run.sh: not found

Proxy service:

=Dockerfile=

FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="londonappdeveloper.com"

COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

USER root

RUN mkdir -p /vol/static && \
    mkdir -p /vol/media && \
    chmod 755 /vol && \
    chown -R nginx:nginx /vol && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh

VOLUME /vol/static
VOLUME /vol/media


USER nginx

CMD ["/run.sh"]

=run.sh=

#!/bin/sh

set -e

envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
nginx -g 'daemon off;'

>

running 
docker compose -f docker-compose-deploy.yml build
docker compose -f docker-compose-deploy.yml up -d
finally shows all services running but still when I try to open app at:
http://localhost/
I get
Bad Request (400)

I see in app logs:

2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: using the "epoll" event method
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: nginx/1.27.3
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: built by gcc 13.2.1 20240309 (Alpine 13.2.1_git20240309) 
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: OS: Linux 5.15.133.1-microsoft-standard-WSL2
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: getrlimit(RLIMIT_NOFILE): 1048576:1048576
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker processes
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 9
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 10
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 11
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 12
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 13
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 14
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 15
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 16
2025-01-18 21:14:15 172.25.0.1 - - [18/Jan/2025:20:14:15 +0000] "GET / HTTP/1.1" 400 154 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0" "-"
2025-01-18 21:14:15 172.25.0.1 - - [18/Jan/2025:20:14:15 +0000] "GET /favicon.ico HTTP/1.1" 400 154 "http://localhost/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0" "-"

In proxy logs:
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: using the "epoll" event method
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: nginx/1.27.3
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: built by gcc 13.2.1 20240309 (Alpine 13.2.1_git20240309) 
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: OS: Linux 5.15.133.1-microsoft-standard-WSL2
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: getrlimit(RLIMIT_NOFILE): 1048576:1048576
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker processes
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 9
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 10
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 11
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 12
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 13
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 14
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 15
2025-01-18 21:12:13 2025/01/18 20:12:13 [notice] 8#8: start worker process 16
2025-01-18 21:14:15 172.25.0.1 - - [18/Jan/2025:20:14:15 +0000] "GET / HTTP/1.1" 400 154 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0" "-"
2025-01-18 21:14:15 172.25.0.1 - - [18/Jan/2025:20:14:15 +0000] "GET /favicon.ico HTTP/1.1" 400 154 "http://localhost/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0" "-"