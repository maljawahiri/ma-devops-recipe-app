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

- Pylance
- Python
- Docker
- HashiCorp Terraform
- Python Debugger

* * *

```
aws configure sso
SSO start URL: https://londonappdev.awsapps.com/start# // link from IAM Identity Center
SSO Region: <region used for IAM Identity Center>
aws-vault list
aws-vault exec <profile.name> --duration=8h
aws-vault add <profile_name>
aws-vault exec myprofile -- aws s3 ls
```

https://github.com/LondonAppDeveloper/devops-recipe-app-api-starting-point
https://gitlab.com/londonappdeveloper/devops-recipe-app-api-starting-point

https://docs.djangoproject.com/en/5.1/howto/static-files/deployment/

```
git clone https://github.com/maljawahiri/ma-devops-recipe-app.git

docker compose build
docker compose up -d
docker compose -f docker-compose-local.yml up -d
docker exec -it ma-devops-recipe-app-app-1 /bin/sh

localhost:8000/admin
docker compose run --rm app sh -c "python manage.py createsuperuser"

admin@invalid.invalid
<keepass:aws-ma-devops-recipe-app>
```

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

```
docker compose -f docker-compose-deploy.yml build
docker compose -f docker-compose-deploy.yml up -d
```

> 2025-01-17 01:28:03 exec /scripts/run.sh: no such file or directory
> 2025-01-17 01:28:10 exec /scripts/run.sh: no such file or directory
> 2025-01-17 01:28:16 exec /scripts/run.sh: no such file or directory

fixed EOL in all .sh files from CR LF to LF

> 2025-01-17 20:54:55 /docker-entrypoint.sh: exec: line 47: /run.sh: not found
> 2025-01-17 20:55:05 /docker-entrypoint.sh: exec: line 47: /run.sh: not found
> 2025-01-17 20:55:20 /docker-entrypoint.sh: exec: line 47: /run.sh: not found

docker run --rm -it ma-devops-recipe-app-proxy /bin/sh

> CMD ["/run.sh"] => CMD ["sh", "/run.sh"]
```
git config core.eol lf
git config core.autocrlf input

git commit ...

git rm --cached -r .
git reset --hard HEAD
```
https://github.com/LondonAppDeveloper/devops-recipe-app-api/compare/s04-02-clone-and-create-repo...s04-06-update-static-and-media-files?expand=1
https://codechecker.app/result/5747299741335552/

http://localhost/api/docs
http://localhost/admin/

https://github.com/LondonAppDeveloper/devops-recipe-app-api/compare/s04-06-update-static-and-media-files...s04-07-switch-uwsgi-to-gunicorn?expand=1

to replace var placeholders with env values use:
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
if there are vars with $ which are not supposed to be replaced use:
>        include              gunicorn_headers;

* * *

create S3 bucket
ma-devops-recipe-app-us-east-1-tf-state
create DynnamoDB table to lock S3 file
ma-devops-recipe-app-tf-lock
ma-devops-recipe-app-api-tf-lock
Partition key
LockID

* * *

https://github.com/github/gitignore/blob/main/Terraform.gitignore

https://registry.terraform.io/providers/hashicorp/aws/latest

infra/setup - run from local laptop to deploy setup Terraform: everything needed for CI/CD job to work
infra/deploy - create deployment environment infra like dev/stg/prod env, deploy code, resources to run in AWS
Run terraform from docker-compose:
* consistent env across all developers
* consistent on local machine and on CI/CD
```
aws-vault list
aws-vault exec research_user1 --duration=1h
docker compose run --rm terraform -chdir=setup init

git tag 05_35-initialise_setup_terraform

git tag 05_35_02-initialise_setup_terraform

docker compose run --rm terraform -chdir=setup fmt
docker compose run --rm terraform -chdir=setup validate
```

* * *

```
docker compose run --rm terraform -chdir=deploy init
docker compose run --rm terraform -chdir=deploy fmt
docker compose run --rm terraform -chdir=deploy validate

git tag 05_36-configure_deploy_terraform
```

* * *

## 06_aws_setup_terraform

Create CD IAM user:
Used by Github build jobs
Defines all permissions in code
Create shared resources across envs:
ECR Repositories

https://developer.hashicorp.com/terraform/language/backend/s3#s3-bucket-permissions
https://developer.hashicorp.com/terraform/language/backend/s3#dynamodb-table-permissions
https://developer.hashicorp.com/terraform/language/values/outputs
https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user

```
docker compose run --rm terraform -chdir=deploy init -reconfigure
docker compose run --rm terraform -chdir=deploy validate

docker compose run --rm terraform -chdir=setup fmt
docker compose run --rm terraform -chdir=setup validate
docker compose run --rm terraform -chdir=setup apply

git tag 06_38_ias_user_for_cd
```

> aws_iam_user.cd: Creating...
> ╷
> │ Error: creating IAM User (ma-recipe-app-api-cd): InvalidClientTokenId: The security token included in the request is invalid
> │ status code: 403, request id: bb03...
> │
> │ with aws_iam_user.cd,
> │ on iam.tf line 5, in resource "aws_iam_user" "cd":
> │ 5: resource "aws_iam_user" "cd" {
> │

something is broken with aws-vault

instead of using aws-vault
```
aws configure --profile "research_user1_cli"
$ENV:AWS_PROFILE="research_user1"
$ENV:AWS_ACCESS_KEY_ID = aws configure get aws_access_key_id
$ENV:AWS_SECRET_ACCESS_KEY = aws configure get aws_secret_access_key

docker compose run --rm terraform -chdir=setup apply
```
To output sensitive value
docker compose run --rm terraform -chdir=setup outputs cd_user_access_key_secret

https://stackoverflow.com/questions/71734015/why-did-aws-vault-auth-failed-error-using-credentials-to-get-account-id-error

> Some things won't work with aws-vault's temporary credentials. Try to use the exec command and pass the parameter --no-session to use the original credentials:
> aws-vault exec brankovich --no-session -- docker-compose -f deploy/docker-compose.yml run --rm terraform init

aws-vault exec research_user1 --no-session

## 06_39_create_ecr_repos

https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecr_repository

allow pushing images with same tag e.g. LATEST
> image_tag_mutability = "MUTABLE"

force delete ECR repository on Terraform destroy
> force_delete         = true

disable image scan for vulnaberities whenever image is pushed
> scan_on_push = false
``` 
docker compose run --rm terraform -chdir=setup fmt
docker compose run --rm terraform -chdir=setup validate
docker compose run --rm terraform -chdir=setup apply
```
## 06_40_add_iam_permissions_for_ecr_repos

https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-push.html

Add permissions to allow to push  to ECR images built by Github Actions CI/CD job 
```
docker compose run --rm terraform -chdir=setup fmt
docker compose run --rm terraform -chdir=setup validate
docker compose run --rm terraform -chdir=setup apply
```
## 07_CI_CD

Git workflow
* when code is checked
  * peer review / linting / unit tests
* when code is deployed
  * which env
* what branch will be used

Workflow design
High level design
* Git source control
* Hosted CI/CD service
  * GitLab CI/CD or GitHub Actions
* Terraform to deploy env

Environments
* Dev - deployment from local machine
* Staging - main branch
* Production - prod branch

Branches
* main (default, protected - git push discouraged)
  * deploys to staging
* prod (protected)
  * deploys to prod
* feature/<name>, bugfix/<name>, etc.
  * merge into main
* hotfix/<name>
  * merge into main or prod

Workflow design

![Workflow design diagram](resources/github_workflow.png)

### 07_43_github_vs_gitlab

free CI/CD tools:
* GitLab:  400 min per month
* GitHub: 2000 min per month
GitLab - open source, can be self hosted
GitHub Pull Request == GitLab Merge Request

### 07_45_overview_of_github_actions

Workflows:
.github/workflows
triggers determine when workflow runs
workflow consist of jobs
job consist of steps

ma-devops-recipe-app workflows:
* checks - unit tests and linting
  * on: pull_request (main)
* deploy
  * on: push (main & prod)
* destroy
  * on: manual (options)

### Setup variables in Github repository.
https://developer.hashicorp.com/terraform/cli/commands/output
docker compose run --rm terraform -chdir=setup output
Grab cd_user_access_key_id, ecr_repo_app, ecr_repo_proxy
docker compose run --rm terraform -chdir=setup output cd_user_access_key_secret
Grab cd_user_access_key_secret
Navigate to repo on Github:
https://github.com/maljawahiri/ma-devops-recipe-app
Settings > Secrets and variables > Actions secrets and variables
secrets - only visible once, not displayed in Github Action job output
environment secrets - for specific environment
repository secrets - available for whole repository
https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment

Add repository Actions variables:
* AWS_ACCESS_KEY_ID
* ECR_REPO_APP
* ECR_REPO_PROXY
* AWS_ACCOUNT_ID
AWS Console > Top-right User menu > Account ID
* DOCKERHUB_USER
hub.docker.com user

Add repository Actions secrets:
* AWS_SECRET_ACCESS_KEY
* DOCKERHUB_TOKEN
hub.docker.com > Top-right User menu > Account Settings > Personal access tokens
Generate access token
ma-devops-recipe-app-token
Read-only
* TF_VAR_db_password
Convention in Terraform is that it will allow you to set variables defined in Terraform variables via environment variable that are prefixed with TF_VAR_ e.g
if there is Terraform variable db_password we can set it via environment variable TF_VAR_db_password
<keepass:aws-ma-devops-recipe-app-db>
* TF_VAR_django_secret_key
<keepass:aws-ma-devops-recipe-app-django>

### 07_47_add_python_checks
checks.yml - workflow triggered on main branch PR events
test-and-lint.yml - reusable workflow used by checks.yml
Variables passed to reusable workflow need to be declared both in calling workflow as well as in called workflow
Github Actions has a marketplace. We will use:
https://github.com/docker/login-action
https://github.com/github/vscode-github-actions

git tag 07_47_add_python_checks
