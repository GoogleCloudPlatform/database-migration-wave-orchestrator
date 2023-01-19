eval "$(jq -r '@sh "PROJECT_ID=\(.project_id)"')"

gcloud services enable iap.googleapis.com --project ${PROJECT_ID}
BRAND_NAME=$(gcloud beta iap oauth-brands list --project=${PROJECT_ID} --format="value(name)")
jq --null-input --arg brand "$BRAND_NAME" '{"brand": $brand}'
