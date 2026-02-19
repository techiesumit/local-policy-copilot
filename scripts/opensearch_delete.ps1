param(
  [Parameter(Mandatory=$false)][string]$DomainName = "local-policy-copilot-dev",
  [Parameter(Mandatory=$false)][string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "Deleting OpenSearch domain '$DomainName' in $Region ..." -ForegroundColor Cyan
aws opensearch delete-domain --region $Region --domain-name $DomainName | Out-Null
# delete-domain is the AWS CLI call that deletes the domain. [web:102]

Write-Host "Waiting for the domain to disappear..." -ForegroundColor Yellow
for ($i=1; $i -le 120; $i++) {
  try {
    aws opensearch describe-domain --region $Region --domain-name $DomainName | Out-Null
    Start-Sleep -Seconds 30
    Write-Host "Still deleting... ($i/120)"
  } catch {
    Write-Host "Domain deleted." -ForegroundColor Green
    exit 0
  }
}
# describe-domain is used here as a simple “exists?” check. [web:114]

throw "Timed out waiting for deletion."
