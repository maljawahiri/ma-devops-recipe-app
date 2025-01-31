aws-devops-deployment-automation-terraform-aws-docker
ma-devops-recipe-app
https://github.com/maljawahiri/ma-devops-recipe-app.git 

https://samsungu.udemy.com/course/devops-deployment-automation-terraform-aws-docker/learn/lecture/43786934#overview

https://www.youtube.com/watch?app=desktop&v=TFsFLzNL5Fk&t=236s
Deploying Django to Google App Engine using Docker
London App Developer

https://www.udemy.com/course/django-python/?referralCode=3B849741B22196721D94&couponCode=NEWYEARCAREER
https://www.udemy.com/course/django-python-advanced/?referralCode=D9B14BE6FBA4FB2DB06D&couponCode=NEWYEARCAREER

https://calculator.aws/#/
https://docs.google.com/spreadsheets/d/1vvjWNn2dCV45AlPQZOdCxSwAj73sHRzUGrRux0HwQZQ/edit?gid=0#gid=0
https://docs.google.com/spreadsheets/d/1q0EPAeO1WaSeX_fQqIL4n08YWjYV-_oz1jT3VE_OhXs/edit?gid=0#gid=0


https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html
https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-windows.html
https://github.com/99designs/aws-vault?tab=readme-ov-file#installing
https://github.com/abiosoft/colima

git config --global push.autoSetupRemote true

VSCode Extensions

Pylance
Python
Docker
HashiCorp Terraform
Python Debugger

>

aws configure sso
SSO start URL: https://londonappdev.awsapps.com/start# // link from IAM Identity Center
SSO Region: <region used for IAM Identity Center>
aws-vault list
aws-vault exec <profile.name> --duration=8h
aws-vault add <profile_name>
aws-vault exec myprofile -- aws s3 ls

https://github.com/LondonAppDeveloper/devops-recipe-app-api-starting-point
https://gitlab.com/londonappdeveloper/devops-recipe-app-api-starting-point

https://docs.djangoproject.com/en/5.1/howto/static-files/deployment/

git clone https://github.com/maljawahiri/ma-devops-recipe-app.git

docker compose build
docker compose up -d
docker exec -it ma-devops-recipe-app-app-1 /bin/sh

localhost:8000/admin
docker compose run --rm app sh -c "python manage.py createsuperuser"

admin@invalid.invalid
<keepass:aws-ma-devops-recipe-app>

http://localhost:8000/admin/

take down service with volumes
docker compose down --volumes

http://localhost:8000/api/docs
POST
/api/user/create/
{
  "email": "user@example.com",
  "password": "string",
  "name": "string"
}
POST
/api/user/token/
{
  "token": "e2a94d5fec7f797dae945f704c33f29d0f2fe199"
}
top right
Authorize
tokenAuth
Token e2a94d5fec7f797dae945f704c33f29d0f2fe199

POST
/api/recipe/recipes/
{
  "id": 1,
POST
/api/recipe/recipes/{id}/upload-image/
multipart/form-data
d:\usr\src\training\aws\aws-architect\src\code\s3\
{
  "id": 1,
  "image": "http://localhost:8000/static/media/uploads/recipe/0e21bfb9-cf18-449e-bfaf-72f9a6c84e1c.jpg"
}

docker compose -f docker-compose-deploy.yml build
docker compose -f docker-compose-deploy.yml up -d

2025-01-17 01:28:03 exec /scripts/run.sh: no such file or directory
2025-01-17 01:28:10 exec /scripts/run.sh: no such file or directory
2025-01-17 01:28:16 exec /scripts/run.sh: no such file or directory

fixed EOL in all .sh files from CR LF to LF

2025-01-17 20:54:55 /docker-entrypoint.sh: exec: line 47: /run.sh: not found
2025-01-17 20:55:05 /docker-entrypoint.sh: exec: line 47: /run.sh: not found
2025-01-17 20:55:20 /docker-entrypoint.sh: exec: line 47: /run.sh: not found

docker run --rm -it ma-devops-recipe-app-proxy /bin/sh

CMD ["/run.sh"] => CMD ["sh", "/run.sh"]

git config core.eol lf
git config core.autocrlf input

git commit ...

git rm --cached -r .
git reset --hard HEAD

https://github.com/LondonAppDeveloper/devops-recipe-app-api/compare/s04-02-clone-and-create-repo...s04-06-update-static-and-media-files?expand=1
https://codechecker.app/result/5747299741335552/

http://localhost/api/docs
http://localhost/admin/

https://github.com/LondonAppDeveloper/devops-recipe-app-api/compare/s04-06-update-static-and-media-files...s04-07-switch-uwsgi-to-gunicorn?expand=1

to replace var placeholders with env values use:
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
if there are vars with $ which are not supposed to be replaced use:
        include              gunicorn_headers;

>

create S3 bucket
ma-devops-recipe-app-us-east-1-tf-state
create DynnamoDB table to lock S3 file
ma-devops-recipe-app-tf-lock
ma-devops-recipe-app-api-tf-lock
Partition key
LockID

>

https://github.com/github/gitignore/blob/main/Terraform.gitignore

https://registry.terraform.io/providers/hashicorp/aws/latest

infra/setup - run from local laptop to deploy setup Terraform: everything needed for CI/CD job to work
infra/deploy - create deployment environment infra like dev/stg/prod env, deploy code, resources to run in AWS
Run terraform from docker-compose:
* consistent env across all developers
* consistent on local machine and on CI/CD

aws-vault list
aws-vault exec research_user1 --duration=1h
docker compose run --rm terraform -chdir=setup init

git tag 05_35-initialise_setup_terraform

git tag 05_35_02-initialise_setup_terraform

docker compose run --rm terraform -chdir=setup fmt
docker compose run --rm terraform -chdir=setup validate

>

docker compose run --rm terraform -chdir=deploy init
docker compose run --rm terraform -chdir=deploy fmt
docker compose run --rm terraform -chdir=deploy validate

git tag 05_36-configure_deploy_terraform

>

06_aws_setup_terraform

Create CD IAM user:
Used by Github build jobs
Defines all permissions in code
Create shared resources across envs:
ECR Repositories

https://developer.hashicorp.com/terraform/language/backend/s3#s3-bucket-permissions
https://developer.hashicorp.com/terraform/language/backend/s3#dynamodb-table-permissions
https://developer.hashicorp.com/terraform/language/values/outputs
https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user

docker compose run --rm terraform -chdir=deploy init -reconfigure
docker compose run --rm terraform -chdir=deploy validate

docker compose run --rm terraform -chdir=setup fmt
docker compose run --rm terraform -chdir=setup validate
docker compose run --rm terraform -chdir=setup apply

git tag 06_38_ias_user_for_cd
