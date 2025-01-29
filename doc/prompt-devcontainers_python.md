given Python Django app on Windows 10 with:

=docker-compose.yml=

=Dockerfile=

=scripts/run.sh=

when I run

docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml up -d

everything works ok and I can access app on:
http://localhost:8000/api/docs

I want to debug this app in IntelliJ IDEA Ultimate using Dev Containers on Windows 10.
On Windows 10 I've installed:
Docker Desktop for Windows 4.37.1 (178610)
IntelliJ IDEA Ultimate 2024.3.2.1

I have Python and Docker plugins installed and configured in IDEA.
In IntelliJ IDEA Ultimate I've selected to Import project from existing sources and I pointed to Python project directory.
During Import process IntelliJ asks:
Please select project SDK
In IntelliJ SDK dialog I've selected:
Python SDK from disk
Add Python interpreter:
Docker Compose Server: Docker
Configuation files:
D:/usr/src/training/aws/aws-devops-deployment-automation-terraform-aws-docker/src/ma-devops-recipe-app/docker-compose.yml
Service: app
Environment variables: <none>
Python interpreter: python

After long time the Remote Python SDK get's created.
Now I want to run Python app using Run configuration.
In Run configuration in IntelliJ I've selected Remote Python Interpreter created in previous step.
According to Dockerfile CMD ["run.sh"] I should run run.sh script on start which looks as follows:

#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate

gunicorn --bind :9000 --workers 4 app.wsgi

How should I configure Run configuration in IntelliJ to run Python app?
In Run configuration in IntelliJ I have to specify either script or module.
What should I provide there?
Analyze step by step my whole setup and suggest how should I configure Run configuration in IntelliJ to run Python app

______________________________________________________________________________________________________________________

given Python Django app on Windows 10 with following startup script

=scripts/run.sh=

#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate

gunicorn --bind :9000 --workers 4 app.wsgi

how can debug such app in IntelliJ IDE Ultimate?
I've already created project in IntelliJ IDE Ultimate from existing sources of Python app.
For example app contains following file:
=app/user/serializers.py=
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

I want to put breakpoint inside create() method.
How should configure Run configuration in IntelliJ IDE Ultimate so it stops on breakpoint inside create() method?
What should I put as script or module in Run configuration?
What's the difference between debuging script or module in Run configuration?
How should I make sure that all commands from run.sh script:

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate

gunicorn --bind :9000 --workers 4 app.wsgi

get invoked and debugger is attached to Django app so it stops at breakpoint inside create() method.?

A:
Ensure:
python manage.py collectstatic --noinput
python manage.py migrate
was invoked previously.

Configure Run configuration as follows:
Use specific interpreter:
Python interpreter from Docker Compose Server created during project import
script:
D:/usr/src/training/aws/aws-devops-deployment-automation-terraform-aws-docker/src/ma-devops-recipe-app/app/manage.py
Parameters:
runserver 0.0.0.0:9000
Working directory:
D:\usr\src\training\aws\aws-devops-deployment-automation-terraform-aws-docker\src\ma-devops-recipe-app\app
Path to ".env":
D:/usr/src/training/aws/aws-devops-deployment-automation-terraform-aws-docker/src/ma-devops-recipe-app/.env
Path mappings:
./app = /app
