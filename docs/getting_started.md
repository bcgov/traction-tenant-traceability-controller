

## Register a traction tenant and create api key

Register for an account with the [traction sandbox](https://traction-sandbox-tenant-ui.apps.silver.devops.gov.bc.ca/)

Once logged in, navigate to the api keys section and create a new key with the alias `Traceability-client`.

Keep your credentials somewhere secure.

## Deploy the application

Clone the repo in your deployment environment. 
You will need the port 443 exposed and an A record pointing to your public IP.

Copy the `.env.example` file and fill in the values:

Enter the value of your A record for the `TRACEABILITY_DOMAIN_NAME` and generate a `TRACEABILITY_ADMIN_API_KEY`. Keep this key safe an use it to manage your identifiers.

The `TRACTION_TENANT_ID` and the `TRACTION_API_KEY` are the values obtained in step 1. If you are not using the sandbox environment, change the `TRACTION_API_URL`.

Until the latest endpoints are deployed to the traction environment, you must have the latests version of aca-py available for verification. Provide a `VERIFIER_ENDPOINT` and a `VERIFIER_API_KEY`.

Fill the `POSTGRES_USER` and `POSTGRES_PASS` values for the postgres superuser. The host and port will use your docker network for this deployment.

Generate a 44 char secret for the `ASKAR_KEY` and another secret for `JWT_SECRET`.

Provide an inbox for `LETSENCRYPT_EMAIL`. The traefik service will renew certificates every 90 days. Notifications will be sent 1 month in advance.

Once set, deploy the application with docker-compose:
```
docker-compose up --build --detach
```

Confirm all the runners are deployed correctly.



