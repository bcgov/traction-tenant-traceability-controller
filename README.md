# Aries Traceability

Implementation of the W3C-CCG Traceability API for Aries/Traction.

## Purpose

This project aims to establish interoperability between the BC Gov Traction platform and the W3C Traceability specification.

## Key Concepts & Functionalities

### DID WEB

A key component is linking a DID Web address with a stored keypair in aca-py. To achieve this, we leverage the DID Sov creation method and provide a user-defined `did:web` endpoint. The current formula to create this address is:

```plaintext
did:web:{domain}:organization:{label} -> did:web:example.com:organization:abc
```

### Resolving Identifiers

To resolve DID Web identifiers, we utilize the `/resolver/resolve` endpoint in aca-py. However, please be aware of a known limitation with the `pydid` library that is currently under investigation. [Learn more](https://github.com/Indicio-tech/pydid/issues/81#issuecomment-1874290829).


### Issuing Credentials

Until new aca-py routes are added to Traction, we leverage the `/jsonld/sign` endpoint.


### Verifying Credentials

Similarly, until new aca-py routes are added to Traction, we leverage a separate acapy service directly. Two known limitations exist in the `pydid` and `pyld` libraries.


### Credential Status

`RevocationList2020` and `StatusList2021` are part of the spec. This layer is managed by this API for issuance, verification, and updates.


### Presentations

For issuance, we leverage the `/jsonld/sign` endpoint. For verification, we use the `/vc/ldp/verify` endpoint.


## Deployment

### Pre-requisites

- Docker / Docker Compose installed
- Dedicated A record pointing to the IP of your deployment environment
- A running aca-py instance for the verifier role (until the latest changes are pulled into the Traction environment)
- A Traction tenant with a dedicated API key

### Steps

```bash
# Clone the repository
git clone https://github.com/OpSecId/aries-traceability.git

# Clone the aca-py repository (required for verifying until the latest changes are pulled into the Traction environment)
git clone https://github.com/hyperledger/aries-cloudagent-python.git

# Move to the project directory
cd aries-traceability

# Create the .env file and fill in the values
cp .env.example .env

# Build the images
docker-compose build

# Deploy and open issues if you encounter a problem
docker-compose up -d

```

## Creating an identifier
This traceability api service will also enable a super admin to register new identifiers.

To create an identifier, choose a label and use the following curl request as an example.
```
curl -X 'POST' \
  'https://{endpoint}/register' \
  -H 'accept: application/json' \
  -H 'X-API-Key: {api_key}' \
  -H 'Content-Type: application/json' \
  -d '{
  "label": "{label}",
  "status_method": "RevocationList2020"
}'

```
Your label must be an alphanumeric lowercase string. You may use dashes(-) and underscores(_).