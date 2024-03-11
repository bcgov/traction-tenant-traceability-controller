# /bin/bash

# source .env && \
# curl -X 'POST' \
#   "https://$TRACEABILITY_CONTROLLER_DOMAIN/$DID_NAMESPACE" \
#   -H "accept: application/json" \
#   -H "Content-Type: application/json" \
#   -H "X-API-Key: $TRACTION_API_KEY" \
#   -d '{}' | jq '.'

source .env && \
curl -X 'POST' \
  "http://3.96.9.60:8080/$DID_NAMESPACE" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $TRACTION_API_KEY" \
  -d '{}' | jq '.'
