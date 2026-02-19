#!/usr/bin/env bash
set -euo pipefail

REGION="us-east-1"
DOMAIN_NAME="${1:-local-policy-copilot-dev}"
ENGINE_VERSION="${ENGINE_VERSION:-OpenSearch_2.11}"

INSTANCE_TYPE="${INSTANCE_TYPE:-t3.small.search}"
INSTANCE_COUNT="${INSTANCE_COUNT:-1}"

VOLUME_SIZE_GB="${VOLUME_SIZE_GB:-10}"
VOLUME_TYPE="${VOLUME_TYPE:-gp3}"

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
# Restrict access to principals in *this* AWS account (basic guard for a public domain).
ACCESS_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::${ACCOUNT_ID}:root" },
      "Action": "es:*",
      "Resource": "arn:aws:es:${REGION}:${ACCOUNT_ID}:domain/${DOMAIN_NAME}/*"
    }
  ]
}
EOF
)

echo "Creating OpenSearch domain: ${DOMAIN_NAME} in ${REGION} ..."
aws opensearch create-domain \
  --region "${REGION}" \
  --domain-name "${DOMAIN_NAME}" \
  --engine-version "${ENGINE_VERSION}" \
  --cluster-config "InstanceType=${INSTANCE_TYPE},InstanceCount=${INSTANCE_COUNT},DedicatedMasterEnabled=false,ZoneAwarenessEnabled=false" \
  --ebs-options "EBSEnabled=true,VolumeType=${VOLUME_TYPE},VolumeSize=${VOLUME_SIZE_GB}" \
  --encryption-at-rest-options "Enabled=true" \
  --node-to-node-encryption-options "Enabled=true" \
  --domain-endpoint-options "EnforceHTTPS=true,TLSSecurityPolicy=Policy-Min-TLS-1-2-2019-07" \
  --access-policies "${ACCESS_POLICY}" \
  >/dev/null

echo "Waiting for domain to become Active (Processing=false) ..."
for i in {1..120}; do
  processing="$(aws opensearch describe-domain \
    --region "${REGION}" \
    --domain-name "${DOMAIN_NAME}" \
    --query 'DomainStatus.Processing' \
    --output text || true)"

  endpoint="$(aws opensearch describe-domain \
    --region "${REGION}" \
    --domain-name "${DOMAIN_NAME}" \
    --query 'DomainStatus.Endpoint' \
    --output text || true)"

  if [[ "${processing}" == "False" && -n "${endpoint}" && "${endpoint}" != "None" ]]; then
    echo "Domain ready."
    echo "Endpoint: https://${endpoint}"
    exit 0
  fi

  echo "Still provisioning... (${i}/120)"
  sleep 30
done

echo "Timed out waiting for domain to be ready."
exit 1
