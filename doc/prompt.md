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

___

using Python 3.12 on Windows 10
given 
=requirements.txt=
Django>=4.0.4,<4.1
djangorestframework>=3.13.1,<3.14
psycopg2>=2.9.3,<2.10
drf-spectacular>=0.22.1,<0.23
Pillow>=9.1.0,<9.2
gunicorn>=21.2.0,<21.3

virtualenv .venv
In Git Bash:
source .venv/Scripts/activate
pip install -r requirements.txt
...

  Traceback (most recent call last):
    File "<string>", line 989, in <module>
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\__init__.py", line 117, in setup
      return distutils.core.setup(**attrs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\_distutils\core.py", line 186, in setup
      return run_commands(dist)
             ^^^^^^^^^^^^^^^^^^
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\_distutils\core.py", line 202, in run_commands
      dist.run_commands()
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\_distutils\dist.py", line 983, in run_commands
      self.run_command(cmd)
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\dist.py", line 999, in run_command
      super().run_command(command)
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\_distutils\dist.py", line 1002, in run_command
      cmd_obj.run()
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\command\bdist_wheel.py", line 379, in run
      self.run_command("build")
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\_distutils\cmd.py", line 339, in run_command
      self.distribution.run_command(command)
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\dist.py", line 999, in run_command
      super().run_command(command)
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\_distutils\dist.py", line 1002, in run_command
      cmd_obj.run()
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\_distutils\command\build.py", line 136, in run
      self.run_command(cmd_name)
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\_distutils\cmd.py", line 339, in run_command
      self.distribution.run_command(command)
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\dist.py", line 999, in run_command
      super().run_command(command)
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\_distutils\dist.py", line 1002, in run_command
      cmd_obj.run()
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\command\build_ext.py", line 99, in run
      _build_ext.run(self)
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\_distutils\command\build_ext.py", line 365, in run
      self.build_extensions()
    File "<string>", line 804, in build_extensions
  RequiredDependencyException: zlib
  
  During handling of the above exception, another exception occurred:
  
  Traceback (most recent call last):
    File "D:\usr\src\training\aws\aws-devops-deployment-automation-terraform-aws-docker\src\ma-devops-recipe-app\.venv\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 353, in <module>
      main()
    File "D:\usr\src\training\aws\aws-devops-deployment-automation-terraform-aws-docker\src\ma-devops-recipe-app\.venv\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 335, in main
      json_out['return_val'] = hook(**hook_input['kwargs'])
                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "D:\usr\src\training\aws\aws-devops-deployment-automation-terraform-aws-docker\src\ma-devops-recipe-app\.venv\Lib\site-packages\pip\_vendor\pyproject_hooks\_in_process\_in_process.py", line 251, in build_wheel
      return _build_backend().build_wheel(wheel_directory, config_settings,
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\build_meta.py", line 438, in build_wheel
      return _build(['bdist_wheel', '--dist-info-dir', str(metadata_directory)])
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\build_meta.py", line 426, in _build
      return self._build_with_temp_dir(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\build_meta.py", line 407, in _build_with_temp_dir
      self.run_setup()
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\build_meta.py", line 522, in run_setup
      super().run_setup(setup_script=setup_script)
    File "C:\Users\Marcin\AppData\Local\Temp\pip-build-env-i9ce0c14\overlay\Lib\site-packages\setuptools\build_meta.py", line 320, in run_setup
      exec(code, locals())
    File "<string>", line 1009, in <module>
  RequiredDependencyException:
  
  The headers or library files could not be found for zlib,
  a required dependency when compiling Pillow from source.
  
  Please see the install instructions at:
     https://pillow.readthedocs.io/en/latest/installation.html
  
  
  <string>:45: RuntimeWarning: Pillow 9.1.1 does not support Python 3.12 and does not provide prebuilt Windows binaries. We do not recommend building from source on Windows.
  [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for Pillow
Failed to build Pillow
ERROR: ERROR: Failed to build installable wheels for some pyproject.toml based projects (Pillow)

>

I also have 
=docker-compose.yml=
version: "3.9"

services:
  app:
    build:
      context: .
      args:
        - DEV=true
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app
      - dev-static-data:/vol/web/static
      - dev-media-data:/vol/web/media
    command: >
      sh -c "python manage.py wait_for_db &&
             python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    environment:
      - DB_HOST=db
      - DB_NAME=devdb
      - DB_USER=devuser
      - DB_PASS=changeme
      - DEBUG=1
    depends_on:
      - db

  db:
    image: postgres:13-alpine
    volumes:
      - dev-db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=devdb
      - POSTGRES_USER=devuser
      - POSTGRES_PASSWORD=changeme

volumes:
  dev-db-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ../data/dev/db
  dev-static-data:
  dev-media-data:

In IntelliJ SDK dialog I've selected:
Python SDK from disk
Add Python interpreter:
Docker Compose
Server: Docker
Configuation files:
D:/usr/src/training/aws/aws-devops-deployment-automation-terraform-aws-docker/src/ma-devops-recipe-app/docker-compose.yml
Service:
app
Environment variables:
<none>
Python interpreter:
python

Is it correct?

>

provide link to tutorial showing how to setup Run configuration for Python project imported to IntelliJ IDEA Ultimate with Python plugin or PyCharm in Windows 10 using remote Python interpreter using docker-compose.yml.
In particular I want to understand how to setup script input.
Dockerfile in the project has
CMD ["run.sh"]
and 
=run.sh=
#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate

gunicorn --bind :9000 --workers 4 app.wsgi

so I need to run this script from within Docker container.
When I try to provide path inside to run.sh inside Docker container:
/scripts/run.sh
it fails with:
 Container ma-devops-recipe-app-db-1  Running
 Container ma-devops-recipe-app-app-1  Recreate
 Container ma-devops-recipe-app-app-1  Recreated
Attaching to app-1
app-1  | python: can't open file '/opt/project/\scripts\run.sh': [Errno 2] No such file or directory
Aborting on container exit...
 Container ma-devops-recipe-app-app-1  Stopping
 Container ma-devops-recipe-app-app-1  Stopped
app-1 exited with code 2

When I try to provide path run.sh on Windows:
D:\usr\src\training\aws\aws-devops-deployment-automation-terraform-aws-docker\src\ma-devops-recipe-app\scripts\run.sh
it fails with:
 Container ma-devops-recipe-app-db-1  Running
 Container ma-devops-recipe-app-app-1  Recreate
 Container ma-devops-recipe-app-app-1  Recreated
Attaching to app-1
app-1  |   File "/opt/project/scripts/run.sh", line 5
app-1  |     python manage.py wait_for_db
app-1  |            ^
app-1  | SyntaxError: invalid syntax
Aborting on container exit...
app-1 exited with code 1
 Container ma-devops-recipe-app-app-1  Stopping
 Container ma-devops-recipe-app-app-1  Stopped

>

what are you talking about?
check out previous conversation.
I have Python project already imported into IntelliJ IDEA Ultimate with SDK configured to use Python interpreter from docker-compose which I already providede to you.
Now I want to run the project.
In Dockerfile I've already provided to you there is step to execute run.sh
How can I do it using Run confifuration from IntelliJ IDEA Ultimate?

>

Create Python Django project with REST API to create/get/update/delete recipes.
Project should contain .idea directory and IML file to load it into IntelliJ IDEA Ultimate with Python plugin.
Make sure the project runs from IntelliJ IDEA Ultimate with Python plugin.
