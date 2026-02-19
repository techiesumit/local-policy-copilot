param(
  [Parameter(Mandatory=$false)][string]$DomainName = "local-policy-copilot-dev",
  [Parameter(Mandatory=$false)][string]$Region = "us-east-1",
  [Parameter(Mandatory=$false)][string]$EngineVersion = "OpenSearch_2.11",
  [Parameter(Mandatory=$false)][string]$InstanceType = "t3.small.search",
  [Parameter(Mandatory=$false)][int]$InstanceCount = 1,
  [Parameter(Mandatory=$false)][int]$VolumeSize = 10,
  [Parameter(Mandatory=$false)][string]$VolumeType = "gp3"
)

$ErrorActionPreference = "Stop"

# Domain naming constraints exist (length/pattern); keep it lowercase with hyphens. [web:94]
$accountId = (aws sts get-caller-identity --query Account --output text)

# Basic public-domain guard: allow only your AWS account root as principal. [web:95]
$accessPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::${accountId}:root" },
      "Action": "es:*",
      "Resource": "arn:aws:es:${Region}:${accountId}:domain/${DomainName}/*"
    }
  ]
}
"@

Write-Host "Creating OpenSearch domain '$DomainName' in $Region ..." -ForegroundColor Cyan

aws opensearch create-domain `
  --region $Region `
  --domain-name $DomainName `
  --engine-version $EngineVersion `
  --cluster-config "InstanceType=$InstanceType,InstanceCount=$InstanceCount,DedicatedMasterEnabled=false,ZoneAwarenessEnabled=false" `
  --ebs-options "EBSEnabled=true,VolumeType=$VolumeType,VolumeSize=$VolumeSize" `
  --encryption-at-rest-options "Enabled=true" `
  --node-to-node-encryption-options "Enabled=true" `
  --domain-endpoint-options "EnforceHTTPS=true,TLSSecurityPolicy=Policy-Min-TLS-1-2-2019-07" `
  --access-policies $accessPolicy | Out-Null
# create-domain is the AWS CLI call that provisions the domain. [web:94]

Write-Host "Waiting for the domain endpoint to be available..." -ForegroundColor Yellow

for ($i=1; $i -le 120; $i++) {
  $endpoint = (aws opensearch describe-domain `
      --region $Region `
      --domain-name $DomainName `
      --query "DomainStatus.Endpoint" `
      --output text) 2>$null

  if ($endpoint -and $endpoint -ne "None") {
    Write-Host "Domain ready." -ForegroundColor Green
    Write-Host "Endpoint: https://$endpoint"
    exit 0
  }

  Start-Sleep -Seconds 30
  Write-Host "Still provisioning... ($i/120)"
}
# describe-domain returns domain info including the domain endpoint. [web:114]

throw "Timed out waiting for domain endpoint."
