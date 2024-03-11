# Aries Traceability Getting Started Tutorial

This tutorial will guide you through setting up an instance of this controller with your Traction tenant ID. You will then be able to register web dids and manage traceable credentials.

- [Deployment](#deployment)
    - [Pre-requisites](#pre-requisites)
    - [Environment](#environment)
    - [Build and deploy](#build-and-deploy)
    - [Helm charts](#helm-charts)

- [Configuration](#configuration)
    - [Creating a did](#create-did)

## Quickstart

`cp .env.example .env`
`docker-compose --env-file .env -f docker/docker-compose.yml -f docker/docker-compose.services.yml up --build`

## Deployment

### Pre-requisites

- Docker / docker-compose
- An A record pointing to the public IP of your deployment environment
    - This will be the `did:web:` base
- HTTPS traffic enabled to 443
- A Traction `tenant_id` and `api_key`
- If running the provided utility script, `curl` and `jq` are required.

### Environment

```bash
# Clone the repository
git clone https://github.com/OpSecId/aries-traceability.git

# Clone the aca-py repository
git clone https://github.com/hyperledger/aries-cloudagent-python.git

# Move to the project directory and fill in the .env file values
cd aries-traceability && \
cp .env.example .env

```

There's a utility script available to generate secrets for convenience
```bash
./scripts/generate_secrets.sh
```

### Build and deploy
```bash
docker-compose up --build --detach
```

### Helm charts
Create the following variables and secrets in your github project
Variables:
- TRACTION_API_ENDPOINT
- TRACEABILITY_CONTROLLER_IMAGE
- TRACEABILITY_CONTROLLER_DOMAIN
Secrets:
- POSTGRES_URI
- POSTGRES_USER
- POSTGRES_PASSWORD
- TRACTION_API_KEY
- TRACTION_TENANT_ID

#### Test the templates
```bash
source .env && \
helm template traction-tenant-traceability-controller ./charts -f ./charts/values.yaml \
            --namespace traction-tenant-traceability-controller --create-namespace \
            --set controller.image=$TRACEABILITY_CONTROLLER_IMAGE \
            --set controller.domain=$TRACEABILITY_CONTROLLER_DOMAIN \
            --set controller.environment.TRACEABILITY_CONTROLLER_DOMAIN=$TRACEABILITY_CONTROLLER_DOMAIN \
            --set controller.environment.POSTGRES_URI=$POSTGRES_URI \
            --set controller.environment.TRACTION_API_KEY=$TRACTION_API_KEY \
            --set controller.environment.TRACTION_TENANT_ID=$TRACTION_TENANT_ID \
            --set controller.environment.TRACTION_API_ENDPOINT=$TRACTION_API_ENDPOINT \
            --set postgres.environment.POSTGRES_USER=$POSTGRES_USER \
            --set postgres.environment.POSTGRES_PASSWORD=$POSTGRES_PASSWORD
```

#### Deploy
```bash
source .env && \
helm upgrade --install --atomic --timeout 2m \
            traction-tenant-traceability-controller ./charts -f ./charts/values.yaml \
            --set controller.image=$TRACEABILITY_CONTROLLER_IMAGE \
            --set controller.domain=$TRACEABILITY_CONTROLLER_DOMAIN \
            --set controller.environment.TRACEABILITY_CONTROLLER_DOMAIN=$TRACEABILITY_CONTROLLER_DOMAIN \
            --set controller.environment.POSTGRES_URI=$POSTGRES_URI \
            --set controller.environment.TRACTION_API_KEY=$TRACTION_API_KEY \
            --set controller.environment.TRACTION_TENANT_ID=$TRACTION_TENANT_ID \
            --set controller.environment.TRACTION_API_ENDPOINT=$TRACTION_API_ENDPOINT \
            --set postgres.environment.POSTGRES_USER=$POSTGRES_USER \
            --set postgres.environment.POSTGRES_PASSWORD=$POSTGRES_PASSWORD
```


## Deployment
### Creating a did
A super admin can register new identifiers.

To create an identifier, choose a label and run the provided script.
```bash
./scripts/register_did.sh my_did_label
```

You will be returned with a resolvable `did` and all the information you need to load the Postman environment. You can now control your did to issue, manage and verify credentials.