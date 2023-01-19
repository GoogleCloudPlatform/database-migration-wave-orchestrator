#!/bin/bash
set -e

eval "$(jq -r '@sh "CERT_NAME=\(.cert_name) PROJECT_ID=\(.project_id)"')"
SITE_NAME=$(gcloud compute ssl-certificates describe ${CERT_NAME} --project=${PROJECT_ID} --format="value(managed.domains[0])")
jq --null-input --arg site "$SITE_NAME" '{"site": $site}'
