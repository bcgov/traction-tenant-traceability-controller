# /bin/bash

source .env
curl -X 'POST' \
  "https://$TRACEABILITY_DOMAIN_NAME/register/did" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $TRACEABILITY_ADMIN_API_KEY" \
  -d '{"label": "'$1'"}' | jq '.'
