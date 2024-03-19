# Aries Traceability Getting Started Tutorial

This tutorial will guide you through setting up an instance of this controller with your Traction tenant ID. You will then be able to register web dids and manage traceable credentials.

- [Traction setup](#traction-setup)
    - [Create account](#create-account)
    - [Create API key](#create-api-key)
- [Deployment](#deployment)
    - [Docker](#docker)
        - [Pre-requisites](#pre-requisites)
        - [Environment](#environment)
        - [Build and deploy](#build-and-deploy)
    - [Kubernetes](#kubernetes)
        - [Helm charts](#helm-charts)
- [Configuration](#configuration)
    - [Creating a did](#create-did)

## Traction Setup

### Create account

Register for an account with the [traction sandbox](https://traction-sandbox-tenant-ui.apps.silver.devops.gov.bc.ca/)

### Create API Key

Once logged in, navigate to the api keys section and create a new key with the alias `Traceability-controller`.

Keep your credentials somewhere secure.

## Deployment

### Docker

#### Pre-requisites

- Docker / docker-compose
- An A record pointing to the public IP of your deployment environment
    - This will be the `did:web:` base and the api endpoint
- HTTPS traffic enabled to port 443
- A Traction `tenant_id` and `api_key`
- If running the provided utility script, `curl` and `jq` are required.

#### Environment

Clone the repository in your deployment environment
```bash
# Clone the repository
git clone https://github.com/OpSecId/aries-traceability.git

# Move to the project directory and fill in the `.env` file values
cd aries-traceability && cp .env.example .env

```

You will need to provide you traction credentials, the domain of your application and the postgres connection URI.

An email is recommended for let's encrypt notifications.

#### Build and deploy
```bash
docker-compose \
--env-file .env \
-f docker/docker-compose.yml \
-f docker/docker-compose.services.yml \
up --build --detach

```

#### Reset deployment
```bash
docker-compose \
--env-file .env \
-f docker/docker-compose.yml \
-f docker/docker-compose.services.yml \
down --volumes

```

### Kubernetes

#### Helm charts
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

##### Test the templates
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

##### Deploy
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