# Aries Traceability

Implementation of the W3C-CCG Traceability API for Aries/Traction.

## Purpose

This project aims to establish interoperability between the BC Gov Traction platform and the W3C Traceability specification.

## Key Concepts & Functionalities

### DID WEB

A key component is linking a DID Web address with a stored keypair in aca-py. To achieve this, we leverage the web did creation method from aca-py and publish the did document.

### Resolving Identifiers

To resolve DID Web identifiers, we utilize the `/resolver/resolve` endpoint in aca-py.

### Managing credentials

The traceability spec leverages the vc-api endpoints to issue, update and verify credentials.

#### Credential Status

Every web did will have a `StatusList2021` with revocation purpose for the credentials it issues.


## Deployment

### Pre-requisites

- Docker / docker-compose
- An A record pointing to the public IP of your deployment environment
    - This will be the `did:web:` base
- HTTPS traffic enabled to 443
- A Traction `tenant_id` and `api_key`

### Prep the environment

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

## Creating an identifier
A super admin can register new identifiers.

To create an identifier, choose a label and run the provided script.
```bash
./scripts/register_did.sh my_did
```

You will be returned with a resolvable `did` and all the information you need to load the Postman environment. You can now control your did to issue, manage and verify credentials.

