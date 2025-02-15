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

>

I've following Terraform code

=deploy/main.tf=

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.23.0"
    }
  }

  backend "s3" {
    bucket               = "ma-devops-recipe-app-us-east-1-tf-state"
    key                  = "tf-state-deploy"
    workspace_key_prefix = "tf-state-deploy-env"
    region               = "us-east-1"
    encrypt              = true
    dynamodb_table       = "devops-recipe-app-api-tf-lock"
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      Environment = terraform.workspace
      Project     = var.project
      Contact     = var.contact
      ManageBy    = "Terraform/deploy"
    }
  }
}

locals {
  prefix = "${var.prefix}-${terraform.workspace}"
}

data "aws_region" "current" {}

=deploy/deploy=

variable "prefix" {
description = "Prefix for resources in AWS"
default     = "mraa"
}

variable "project" {
description = "Project name for tagging resources"
default     = "ma-recipe-app-api"
}

variable "contact" {
description = "Contact email for tagging resources"
default     = "contact@_______.com"
}

and I've ran

docker compose run --rm terraform -chdir=deploy init
docker compose run --rm terraform -chdir=deploy fmt
docker compose run --rm terraform -chdir=deploy validate

Now I've realized that dynamodb_table should be:
"ma-devops-recipe-app-api-tf-lock"
What should I do to correct AWS deployment except editing the main.tf

A:
docker compose run --rm terraform -chdir=deploy init -reconfigure
docker compose run --rm terraform -chdir=deploy validate
docker compose run --rm terraform -chdir=deploy plan

_________________________________________________________________________________________________________

I've following Terraform code

=setup/main.tf=

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.23.0"
    }
  }

  backend "s3" {
    bucket         = "ma-devops-recipe-app-us-east-1-tf-state"
    key            = "tf-state-setup"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "ma-devops-recipe-app-tf-lock"
  }
}

provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Environment = terraform.workspace
      Project     = var.project
      Contact     = var.contact
      ManageBy    = "Terraform/setup"
    }
  }
}

=setup/variables.tf=

variable "tf_state_bucket" {
  description = "Name of S3 bucket in AWS for storing TF state"
  default     = "ma-devops-recipe-app-us-east-1-tf-state"
}

variable "tf_state_lock_table" {
  description = "Name of DynamoDB table for TF state locking"
  default     = "ma-devops-recipe-app-tf-lock"
}

variable "project" {
  description = "Project name for tagging resources"
  default     = "ma-recipe-app-api"
}

variable "contact" {
  description = "Contact name for tagging resources"
  default     = "c@_______.com"
}

=setup/outputs.tf=

output "cd_user_access_key_id" {
  description = "Access key ID for CD user"
  value       = aws_iam_access_key.cd.id
}

output "cd_user_access_key_secret" {
  description = "Access key secret for CD user"
  value       = aws_iam_access_key.cd.secret
  sensitive   = true
}

=setup/iam.tf=

#######################################################################
# Create IAM user and policies for Continuous Deployment (CD) account #
#######################################################################

resource "aws_iam_user" "cd" {
  name = "ma-recipe-app-api-cd"
}

resource "aws_iam_access_key" "cd" {
  user = aws_iam_user.cd.name
}

#########################################################
# Policy for Teraform backend to S3 and DynamoDB access #
#########################################################

data "aws_iam_policy_document" "tf_backend" {
  statement {
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${var.tf_state_bucket}"]
  }

  statement {
    effect  = "Allow"
    actions = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = [
      "arn:aws:s3:::${var.tf_state_bucket}/tf-state-deploy/*",
      "arn:aws:s3:::${var.tf_state_bucket}/tf-state-deploy-env/*"
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem"
    ]
    resources = ["arn:aws:dynamodb:*:*:table/${var.tf_state_lock_table}"]
  }
}

resource "aws_iam_policy" "tf_backend" {
  name        = "${aws_iam_user.cd.name}-tf-s3-dynamodb"
  description = "Allow user to use S3 and DynamoDB for TF backend resources"
  policy      = data.aws_iam_policy_document.tf_backend.json
}

resource "aws_iam_user_policy_attachment" "tf_backend" {
  user       = aws_iam_user.cd.name
  policy_arn = aws_iam_policy.tf_backend.arn
}

I've created in IAM research_user1 with following Policies attached:
AmazonS3FullAccess
AmazonEC2FullAccess
IAMFullAccess
I've generated access key and secret key for this user and configured aws-vault with this user.
I authenticate this user using aws-vault

aws-vault exec research_user1 --duration=1h

and I've ran:
docker compose run --rm terraform -chdir=setup init
...
Terraform has been successfully initialized
...
docker compose run --rm terraform -chdir=setup fmt
docker compose run --rm terraform -chdir=setup validate
...
Success: The configuration is valid.
docker compose run --rm terraform -chdir=setup apply
...
aws_iam_user.cd: Creating...
╷
│ Error: creating IAM User (ma-recipe-app-api-cd): InvalidClientTokenId: The security token included in the request is invalid
│ status code: 403, request id: bb03...
│
│ with aws_iam_user.cd,
│ on iam.tf line 5, in resource "aws_iam_user" "cd":
│ 5: resource "aws_iam_user" "cd" {
│

As I can see research_user1 can run:
aws s3 ls
2022-04-11 11:54:21 lab1
2022-04-12 12:54:21 lab2

and
aws sts get-caller-identity
{
    "UserId": "AIDA...",
    "Account": "..."
    "Arn": "arn:aws:iam::...:user/research_user1"
}

However following commands fail:
aws iam get-user
An error occurred (InvalidClientTokenId) when calling the GetUser operation: The security token included in the request is invalid

aws-vault exec research_user1 -- aws iam list-user-policies --user-name research_user1
An error occurred (InvalidClientTokenId) when calling...

aws-vault exec research_user1 -- aws iam list-attached-user-policies --user-name research_user1
An error occurred (InvalidClientTokenId) when calling the ListAttachedUserPolicies operation: The security token included in the request is invalid

_________________________________________________________________________________________________________

A:
You can verify the IAM permissions for research_user1 using the AWS CLI in a few ways: https://docs.aws.amazon.com/IAM/latest/UserGuide/iam_example_iam_CreateUser_section.html

Check your current permissions using get-user:

aws-vault exec research_user1 -- aws iam get-user

List all policies attached to your user:

aws-vault exec research_user1 -- aws iam list-attached-user-policies --user-name research_user1

List inline policies if any:

aws-vault exec research_user1 -- aws iam list-user-policies --user-name research_user1

To test specific IAM permissions, you can use the IAM policy simulator via CLI:

aws-vault exec research_user1 -- aws iam simulate-principal-policy \
    --policy-source-arn arn:aws:iam::YOUR_ACCOUNT_ID:user/research_user1 \
    --action-names iam:CreateUser iam:CreateAccessKey iam:PutUserPolicy iam:AttachUserPolicy

You can also check if you have the required permissions by testing a dry run: https://repost.aws/questions/QUmtU1yP8uSGizM60PsT-Iyg/access-denied-when-going-into-users

aws-vault exec research_user1 -- aws iam get-user --user-name test-permissions

This will fail with either an "AccessDenied" error (indicating you don't have permissions) or a "NoSuchEntity" error (indicating you have permissions to check for users but the test user doesn't exist).

Remember to replace research_user1 with your actual IAM username if it's different. If you don't have sufficient permissions, you'll need to contact your AWS account administrator to grant the necessary IAM permissions. https://docs.aws.amazon.com/IAM/latest/UserGuide/access_permissions-required.html

>

if research_user1 is missing neccessary permissions how can I add them from command line?

A:

To add the necessary permissions to research_user1, you'll need to use an AWS account that has IAM administrative privileges. Here's how you can do it: https://repost.aws/questions/QUetBfcivwST67sjs1VOY7yw/allow-to-grant-select-on-mysql-information-schema

First, switch to an admin user (let's call it admin_user):

aws-vault exec admin_user -- aws iam create-policy \
    --policy-name IAMUserManagementPolicy \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:CreateUser",
                    "iam:CreateAccessKey",
                    "iam:PutUserPolicy",
                    "iam:AttachUserPolicy",
                    "iam:CreatePolicy",
                    "iam:DeleteUser",
                    "iam:DeleteAccessKey",
                    "iam:DeleteUserPolicy",
                    "iam:DetachUserPolicy",
                    "iam:GetUser",
                    "iam:ListUsers",
                    "iam:ListAccessKeys",
                    "iam:ListUserPolicies",
                    "iam:ListAttachedUserPolicies"
                ],
                "Resource": "*"
            }
        ]
    }'

Attach the policy to research_user1:

aws-vault exec admin_user -- aws iam attach-user-policy \
    --user-name research_user1 \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/IAMUserManagementPolicy

Alternatively, if you want to use an existing AWS managed policy:

# Attach IAM full access (be cautious with this as it grants full IAM permissions)
aws-vault exec admin_user -- aws iam attach-user-policy \
    --user-name research_user1 \
    --policy-arn arn:aws:iam::aws:policy/IAMFullAccess

Or for more limited permissions:

# Attach PowerUserAccess (provides broad permissions but no IAM management)
aws-vault exec admin_user -- aws iam attach-user-policy \
    --user-name research_user1 \
    --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

Verify the attached policies:

aws-vault exec admin_user -- aws iam list-attached-user-policies \
    --user-name research_user1

Remember to:

Replace YOUR_ACCOUNT_ID with your actual AWS account ID

Use an admin account that has permissions to manage IAM

Consider the principle of least privilege and only grant the permissions that are actually needed

Be cautious when granting IAM permissions as they can be security-sensitive

If you need to remove these permissions later:

aws-vault exec admin_user -- aws iam detach-user-policy \
    --user-name research_user1 \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/IAMUserManagementPolicy

>

aws-vault exec research_user1 --duration=1h
aws s3 ls
2022-04-11 11:54:21 lab1
2022-04-12 12:54:21 lab2
aws iam get-user
An error occurred (InvalidClientTokenId) when calling the GetUser operation: The security token included in the request is invalid

>

what do you mean by " you have different AWS credentials configured in different places"
I'm using aws-vault so it ensures single credentials are selected.
Those are credentials for research_user1
Perhaps research_user1 has no permissions to make
aws iam get-user
call.
I can see that I can make successful
aws sts get-caller-identity

>

aws-vault exec research_user1 -- aws organizations list-policies --filter SERVICE_CONTROL_POLICY
An error occurred (AccessDeniedException) when calling the ListPolicies operation: You don't have permissions to access this resource.

aws-vault exec research_user1 -- aws organizations list-policies-for-target --target-id ROOT_OR_OU_ID --filter SERVICE_CONTROL_POLICY
An error occurred (InvalidInputException) when calling the ListPoliciesForTarget operation: You provided a value that does not match the required pattern.

_________________________________________________________________________________________________________________________________

I got Terraform app I want to deploy using DockerCompose:

=docker-compose.yml=

services:
  terraform:
    image: hashicorp/terraform:1.6.2
    volumes:
      - ./setup:/tf/setup
      - ./deploy:/tf/deploy
    working_dir: /tf
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}
      - AWS_DEFAULT_REGION=us-east-1
      - TF_WORKSPACE=${TF_WORKSPACE}

=setup/main.tf=

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.23.0"
    }
  }

  backend "s3" {
    bucket         = "ma-devops-recipe-app-us-east-1-tf-state"
    key            = "tf-state-setup"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "ma-devops-recipe-app-tf-lock"
  }
}

provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Environment = terraform.workspace
      Project     = var.project
      Contact     = var.contact
      ManageBy    = "Terraform/setup"
    }
  }
}

=setup/variables.tf=

variable "tf_state_bucket" {
  description = "Name of S3 bucket in AWS for storing TF state"
  default     = "ma-devops-recipe-app-us-east-1-tf-state"
}

variable "tf_state_lock_table" {
  description = "Name of DynamoDB table for TF state locking"
  default     = "ma-devops-recipe-app-tf-lock"
}

variable "project" {
  description = "Project name for tagging resources"
  default     = "ma-recipe-app-api"
}

variable "contact" {
  description = "Contact name for tagging resources"
  default     = "c@_______.com"
}

=setup/outputs.tf=

output "cd_user_access_key_id" {
  description = "Access key ID for CD user"
  value       = aws_iam_access_key.cd.id
}

output "cd_user_access_key_secret" {
  description = "Access key secret for CD user"
  value       = aws_iam_access_key.cd.secret
  sensitive   = true
}

=setup/iam.tf=

#######################################################################
# Create IAM user and policies for Continuous Deployment (CD) account #
#######################################################################

resource "aws_iam_user" "cd" {
  name = "ma-recipe-app-api-cd"
}

resource "aws_iam_access_key" "cd" {
  user = aws_iam_user.cd.name
}

#########################################################
# Policy for Teraform backend to S3 and DynamoDB access #
#########################################################

data "aws_iam_policy_document" "tf_backend" {
  statement {
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${var.tf_state_bucket}"]
  }

  statement {
    effect  = "Allow"
    actions = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = [
      "arn:aws:s3:::${var.tf_state_bucket}/tf-state-deploy/*",
      "arn:aws:s3:::${var.tf_state_bucket}/tf-state-deploy-env/*"
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem"
    ]
    resources = ["arn:aws:dynamodb:*:*:table/${var.tf_state_lock_table}"]
  }
}

resource "aws_iam_policy" "tf_backend" {
  name        = "${aws_iam_user.cd.name}-tf-s3-dynamodb"
  description = "Allow user to use S3 and DynamoDB for TF backend resources"
  policy      = data.aws_iam_policy_document.tf_backend.json
}

resource "aws_iam_user_policy_attachment" "tf_backend" {
  user       = aws_iam_user.cd.name
  policy_arn = aws_iam_policy.tf_backend.arn
}

I've created in IAM research_user1 with following Policies attached:
AmazonS3FullAccess
AmazonEC2FullAccess
IAMFullAccess

I want to issue following commands:

docker compose run --rm terraform -chdir=setup fmt
docker compose run --rm terraform -chdir=setup validate
docker compose run --rm terraform -chdir=setup apply

What is the recommended way to authenticate terraform calls in AWS?

A:
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)

>>>

In AWS Console I've created in IAM research_user1 with following Policies attached:
AmazonS3FullAccess
AmazonEC2FullAccess
IAMFullAccess

I've corporate app which provides me with temporary credentials for AWS CLI.
After running the app in cmd when I issue:

aws s3 ls
2022-04-11 11:54:21 lab1
2022-04-12 12:54:21 lab2

aws iam get-user
An error occurred (ValidationError) when calling the GetUser operation: Must specify userName when calling with non-User credentials

aws iam get-user --user-name research_user1
{
  "User": {
    "Path": "/",
    "UserName": "research_user1",
    "UserId": "...",
    "Arn": "arn:aws..."
    "CreateDate": "..."
  }
}

I've terraform configuration

=deploy/main.tf=

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.23.0"
    }
  }

  backend "s3" {
    bucket               = "ma-devops-recipe-app-us-east-1-tf-state"
    key                  = "tf-state-deploy"
    workspace_key_prefix = "tf-state-deploy-env"
    region               = "us-east-1"
    encrypt              = true
    dynamodb_table       = "ma-devops-recipe-app-api-tf-lock"
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      Environment = terraform.workspace
      Project     = var.project
      Contact     = var.contact
      ManageBy    = "Terraform/deploy"
    }
  }
}

locals {
  prefix = "${var.prefix}-${terraform.workspace}"
}

data "aws_region" "current" {}

=deploy/variables.tf=

variable "prefix" {
  description = "Prefix for resources in AWS"
  default     = "mraa"
}

variable "project" {
  description = "Project name for tagging resources"
  default     = "ma-recipe-app-api"
}

variable "contact" {
  description = "Contact email for tagging resources"
  default     = "..."
}

=docker-compose.yml=
services:
  terraform:
    image: hashicorp/terraform:1.6.2
    volumes:
      - ./setup:/tf/setup
      - ./deploy:/tf/deploy
    working_dir: /tf
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}
      - AWS_DEFAULT_REGION=us-east-1
      - TF_WORKSPACE=${TF_WORKSPACE}

When I run:
docker compose run --rm terraform -chdir=deploy init
time="2025-02-14T20:45:21+01:00" level=warning msg="The \"AWS_ACCESS_KEY_ID\" variable is not set. Defaulting to a blank string."
time="2025-02-14T20:45:21+01:00" level=warning msg="The \"AWS_SECRET_ACCESS_KEY\" variable is not set. Defaulting to a blank string."
time="2025-02-14T20:45:21+01:00" level=warning msg="The \"AWS_SESSION_TOKEN\" variable is not set. Defaulting to a blank string."
time="2025-02-14T20:45:21+01:00" level=warning msg="The \"TF_WORKSPACE\" variable is not set. Defaulting to a blank string."│ Error: No valid credential sources found 
│ Error: failed to refresh cached credentials, no EC2 IMDS role found, operation error ec2imds: GetMetadata, http response error StatusCode: 403, request to EC2 IMDS failed

How can I make terraform use research_user1 which has all necessary roles and policies attached?
I can't generated access key and secret key for research_user1.
I must use corporate app which provides me with temporary credentials for AWS CLI.

>

nope that's not critical part
the critical part is that default temporary credentials I have for AWS CLI are for some user different than research_user1
As you can see if I issue:

aws iam get-user
An error occurred (ValidationError) when calling the GetUser operation: Must specify userName when calling with non-User credentials

Only if I change context to research_user1 I get correct data:
aws iam get-user --user-name research_user1
{
  "User": {
    "Path": "/",
    "UserName": "research_user1",
    "UserId": "...",
    "Arn": "arn:aws..."
    "CreateDate": "..."
  }
}

So if I specify temporary credentials I'll not be executing terraform command as research_user1 but as some user without necessary roles and policies attached.
I need to execute terraform command as research_user1.
How can I do it?

>

I've created Role terraform-role with with following Permissions policies:
AmazonS3FullAccess
AmazonEC2FullAccess
IAMFullAccess
AmazonDynamoDBFullAccess
What should I do make 
docker compose run --rm terraform -chdir=deploy init
work correctly given I've access to AWS CLI using corporate temporary credentials which produce
aws iam get-user
An error occurred (ValidationError) when calling the GetUser operation: Must specify userName when calling with non-User credentials

>

ok, let's summarize because I got lost.
I've role terraform-role which have all necessary permissions to run terraform actions.
I've AWS CLI access with temporary credentials which don't have permissions to run terraform actions but can see terraform-role when I issue:
aws iam list-roles
Provide concise list of steps to allow perform terraform actions using docker-compose.yml I provided before.
Steps shall not involve modifications of the terraform code.
Steps should be easily reproducable in future when I get new temporary credentials.

A:
echo %AWS_ACCESS_KEY_ID%
echo %AWS_SECRET_ACCESS_KEY%
echo %AWS_SESSION_TOKEN%
aws sts get-caller-identity --query Account --output text
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/terraform-role --role-session-name terraform-session > temp_role.json
for /f "tokens=4 delims=\" %i in ('findstr /i "AccessKeyId" temp_role.json') do set AWS_ACCESS_KEY_ID=%i
set AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID:~0,-2%
set AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID:"=%

for /f "tokens=4 delims=\" %i in ('findstr /i "SecretAccessKey" temp_role.json') do set AWS_SECRET_ACCESS_KEY=%i
set AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY:~0,-2%
set AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY:"=%

for /f "tokens=4 delims=\" %i in ('findstr /i "SessionToken" temp_role.json') do set AWS_SESSION_TOKEN=%i
set AWS_SESSION_TOKEN=%AWS_SESSION_TOKEN:~0,-2%
set AWS_SESSION_TOKEN=%AWS_SESSION_TOKEN:"=%

echo %AWS_ACCESS_KEY_ID%
echo %AWS_SECRET_ACCESS_KEY%
echo %AWS_SESSION_TOKEN%

del temp_role.json

aws sts get-caller-identity
{
    "UserId": "AROA...:terraform-session",
    "Account": "123456789012",
    "Arn": "arn:aws:sts::123456789012:assumed-role/terraform-role/terraform-session"
}

@echo off
REM 1. Obtain AWS Account ID
FOR /F "delims=" %%A IN ('aws sts get-caller-identity --query Account --output text') DO SET ACCOUNT_ID=%%A

REM 2. Assume terraform-role
aws sts assume-role --role-arn arn:aws:iam::%ACCOUNT_ID%:role/terraform-role --role-session-name terraform-session > temp_role.json

REM 3. Extract and set AWS_ACCESS_KEY_ID
for /f "tokens=4 delims=\" %%i in ('findstr /i "AccessKeyId" temp_role.json') do set AWS_ACCESS_KEY_ID=%%i
set AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID:~0,-2%
set AWS_ACCESS_KEY_ID=%AWS_ACCESS_KEY_ID:"=%

REM 4. Extract and set AWS_SECRET_ACCESS_KEY
for /f "tokens=4 delims=\" %%i in ('findstr /i "SecretAccessKey" temp_role.json') do set AWS_SECRET_ACCESS_KEY=%%i
set AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY:~0,-2%
set AWS_SECRET_ACCESS_KEY=%AWS_SECRET_ACCESS_KEY:"=%

REM 5. Extract and set AWS_SESSION_TOKEN
for /f "tokens=4 delims=\" %%i in ('findstr /i "SessionToken" temp_role.json') do set AWS_SESSION_TOKEN=%%i
set AWS_SESSION_TOKEN=%AWS_SESSION_TOKEN:~0,-2%
set AWS_SESSION_TOKEN=%AWS_SESSION_TOKEN:"=%

REM 6. Clean up
del temp_role.json

REM 7. Confirm Assumed Role
aws sts get-caller-identity

echo Assumed terraform-role and exported credentials.

>>>


I've terraform configuration

=deploy/main.tf=

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.23.0"
    }
  }

  backend "s3" {
    bucket               = "ma-devops-recipe-app-us-east-1-tf-state"
    key                  = "tf-state-deploy"
    workspace_key_prefix = "tf-state-deploy-env"
    region               = "us-east-1"
    encrypt              = true
    dynamodb_table       = "ma-devops-recipe-app-api-tf-lock"
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      Environment = terraform.workspace
      Project     = var.project
      Contact     = var.contact
      ManageBy    = "Terraform/deploy"
    }
  }
}

locals {
  prefix = "${var.prefix}-${terraform.workspace}"
}

data "aws_region" "current" {}

=deploy/variables.tf=

variable "prefix" {
  description = "Prefix for resources in AWS"
  default     = "mraa"
}

variable "project" {
  description = "Project name for tagging resources"
  default     = "ma-recipe-app-api"
}

variable "contact" {
  description = "Contact email for tagging resources"
  default     = "..."
}

=docker-compose.yml=
services:
  terraform:
    image: hashicorp/terraform:1.6.2
    volumes:
      - ./setup:/tf/setup
      - ./deploy:/tf/deploy
    working_dir: /tf
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}
      - AWS_DEFAULT_REGION=us-east-1
      - TF_WORKSPACE=${TF_WORKSPACE}


I've created Role terraform-role with with following Permissions policies:
AmazonS3FullAccess
AmazonEC2FullAccess
IAMFullAccess
AmazonDynamoDBFullAccess

I've corporate app which provides me with temporary credentials for AWS CLI.
After running the app in cmd when I issue:

aws s3 ls
2022-04-11 11:54:21 lab1
2022-04-12 12:54:21 lab2

aws iam get-user
An error occurred (ValidationError) when calling the GetUser operation: Must specify userName when calling with non-User credentials

When I run:
docker compose run --rm terraform -chdir=deploy init
time="2025-02-14T20:45:21+01:00" level=warning msg="The \"AWS_ACCESS_KEY_ID\" variable is not set. Defaulting to a blank string."
time="2025-02-14T20:45:21+01:00" level=warning msg="The \"AWS_SECRET_ACCESS_KEY\" variable is not set. Defaulting to a blank string."
time="2025-02-14T20:45:21+01:00" level=warning msg="The \"AWS_SESSION_TOKEN\" variable is not set. Defaulting to a blank string."
time="2025-02-14T20:45:21+01:00" level=warning msg="The \"TF_WORKSPACE\" variable is not set. Defaulting to a blank string."│ Error: No valid credential sources found 
│ Error: failed to refresh cached credentials, no EC2 IMDS role found, operation error ec2imds: GetMetadata, http response error StatusCode: 403, request to EC2 IMDS failed

I can't generated access key and secret key for AWS user.
I must use corporate app which provides me with temporary credentials for AWS CLI.
I've role terraform-role which have all necessary permissions to run terraform actions.
I've AWS CLI access with temporary credentials which don't have permissions to run terraform actions but can see terraform-role when I issue:
aws iam list-roles
Provide concise list of steps to allow perform terraform actions using docker-compose.yml I provided before:
docker compose run --rm terraform -chdir=deploy init
Steps shall not involve modifications of the terraform code.
Steps should be easily reproducable in future when I get new temporary credentials.

>

A:

ROLE_ARN=$(aws iam list-roles --query "Roles[?RoleName=='terraform-role'].Arn" --output text)

CREDS=$(aws sts assume-role --role-arn "$ROLE_ARN" --role-session-name "TFSession-$(date +%s)")
export AWS_ACCESS_KEY_ID=$(echo "$CREDS" | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo "$CREDS" | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo "$CREDS" | jq -r '.Credentials.SessionToken')

docker compose run --rm terraform -chdir=deploy init

#!/bin/bash
ROLE_ARN=$(aws iam list-roles --query "Roles[?RoleName=='terraform-role'].Arn" --output text)
CREDS=$(aws sts assume-role --role-arn "$ROLE_ARN" --role-session-name "TFSession-$(date +%s)")
export AWS_ACCESS_KEY_ID=$(echo "$CREDS" | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo "$CREDS" | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo "$CREDS" | jq -r '.Credentials.SessionToken')
docker compose run --rm terraform -chdir=deploy "$@"

./run_terraform.sh init  # Or apply/destroy/etc.

>

==

param(
    [string]$RoleName = "terraform-role"  # Default role name if not specified
)

# Get the role ARN
$ROLE_ARN = (aws iam list-roles --query "Roles[?RoleName=='$RoleName'].Arn" --output text)

# Assume the role and get temporary credentials
$CREDS = aws sts assume-role --role-arn $ROLE_ARN --role-session-name "TFSession-$(Get-Date -Format 'yyyyMMddHHmmss')" | ConvertFrom-Json

# Clean up existing environment variables
Remove-Item Env:\AWS_ACCESS_KEY_ID -ErrorAction SilentlyContinue
Remove-Item Env:\AWS_SECRET_ACCESS_KEY -ErrorAction SilentlyContinue
Remove-Item Env:\AWS_SESSION_TOKEN -ErrorAction SilentlyContinue

# Set new environment variables
$env:AWS_ACCESS_KEY_ID = $CREDS.Credentials.AccessKeyId
$env:AWS_SECRET_ACCESS_KEY = $CREDS.Credentials.SecretAccessKey
$env:AWS_SESSION_TOKEN = $CREDS.Credentials.SessionToken

Write-Host "AWS credentials set for role: $RoleName ($ROLE_ARN)"

==

aws configure set aws_access_key_id $env:AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $env:AWS_SECRET_ACCESS_KEY
aws configure set aws_session_token $env:AWS_SESSION_TOKEN
aws configure set region us-east-1

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
