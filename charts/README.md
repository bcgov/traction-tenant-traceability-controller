# TTTC deployment charts

Copy the following to an `.env` file and fill in the values
```bash
# internal service uri for the postgres DB 
# ex: postgres://admin:p4ssword@postgres-svc:5432
POSTGRES_URI: ""
POSTGRES_USER: ""
POSTGRES_PASSWORD: ""

# the did namespace did:web:{domain}:{did_namespace}:{identifier}
# ex: organizations, instances, identifiers, clients, tenants
DID_NAMESPACE: 'organizations'

# Created api key from a traction tenant account
TRACTION_API_KEY: ''

# Created tenant_id from a traction tenant account
TRACTION_TENANT_ID: ''

# url for the traction api endpoint 
# ex: https://some.traction.api.example.com
TRACTION_API_ENDPOINT: ''

# domain for the traceability controller endpoint 
# ex: my.tttc.domain.example.com
# this value will be used as the did:web: base 
# ex: did:web:my.tttc.domain.example.com:organizations:xyz
TRACEABILITY_CONTROLLER_DOMAIN: ''

# internal service endpoint for the acapy verifier agent admin api
VERIFIER_ENDPOINT: 'http://acapy:8020'
```

To test the charts
```bash
source .env && \
helm template traction-tenant-traceability-controller ./traction-tenant-traceability-controller \
    -f ./traction-tenant-traceability-controller/values.yaml \
    --set controller.environment.POSTGRES_URI=$POSTGRES_URI \
    --set controller.environment.TRACTION_API_KEY=$TRACTION_API_KEY \
    --set controller.environment.TRACTION_TENANT_ID=$TRACTION_TENANT_ID \
    --set controller.environment.TRACTION_API_ENDPOINT=$TRACTION_API_ENDPOINT \
    --set controller.environment.TRACEABILITY_CONTROLLER_DOMAIN=$TRACEABILITY_CONTROLLER_DOMAIN \
    --set controller.environment.VERIFIER_ENDPOINT=$VERIFIER_ENDPOINT

```
