# /bin/bash

source .env
curl -X 'POST' \
  "https://$TRACEABILITY_CONTROLLER_DOMAIN/register/did" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $TRACTION_API_KEY" \
  -d '{"label": "'$1'"}' | jq '.'
