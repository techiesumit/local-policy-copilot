#!/usr/bin/env bash
set -euo pipefail

REGION="us-east-1"
DOMAIN_NAME="${1:-local-policy-copilot-dev}"

echo "Deleting OpenSearch domain: ${DOMAIN_NAME} in ${REGION} ..."
aws opensearch delete-domain --region "${REGION}" --domain-name "${DOMAIN_NAME}" >/dev/null

echo "Delete requested. Waiting until the domain no longer exists..."
for i in {1..120}; do
  if aws opensearch describe-domain --region "${REGION}" --domain-name "${DOMAIN_NAME}" >/dev/null 2>&1; then
    echo "Still deleting... (${i}/120)"
    sleep 30
  else
    echo "Domain deleted."
    exit 0
  fi
done

echo "Timed out waiting for domain deletion."
exit 1
