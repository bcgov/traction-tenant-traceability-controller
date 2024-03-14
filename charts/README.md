# TTTC deployment charts


To test the charts
```bash
source .env && \
helm template traction-tenant-traceability-controller ./traction-tenant-traceability-controller \
    -f ./traction-tenant-traceability-controller/values.yaml \
    --set postgres.environment.POSTGRES_USER=$POSTGRES_USER \
    --set postgres.environment.POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    --set controller.environment.POSTGRES_URI=$POSTGRES_URI \
    --set controller.environment.TRACTION_API_KEY=$TRACTION_API_KEY \
    --set controller.environment.TRACTION_TENANT_ID=$TRACTION_TENANT_ID \
    --set controller.environment.TRACTION_API_ENDPOINT=$TRACTION_API_ENDPOINT \
    --set controller.environment.TRACEABILITY_CONTROLLER_DOMAIN=$TRACEABILITY_CONTROLLER_DOMAIN

```