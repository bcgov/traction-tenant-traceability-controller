# Aries Traceability Getting Started Tutorial

This tutorial will guide you through setting up an instance of this controller with your Traction tenant ID. You will then be able to register web dids and manage traceable credentials.

- [Deployment](#deployment)
    - [Pre-requisites](#pre-requisites)
    - [Environment](#environment)
    - [Build and deploy](#build-and-deploy)
    - [Creating a did](#create-did)

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

## Creating a did
A super admin can register new identifiers.

To create an identifier, choose a label and run the provided script.
```bash
./scripts/register_did.sh my_did_label
```

You will be returned with a resolvable `did` and all the information you need to load the Postman environment. You can now control your did to issue, manage and verify credentials.