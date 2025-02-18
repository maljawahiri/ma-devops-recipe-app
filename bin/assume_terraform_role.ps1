param(
    [string]$RoleName = "ma-recipe-app-terraform-role"  # Default role name if not specified
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