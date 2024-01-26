# Traceability and Traction feature comparison

## Table of Contents

- [Functionalities](#functionalities)
  - [DID WEB](#did-web)
    - [Register](#register-did-web)
    - [Resolve](#resolve-did-web)
  - [Credentials](#credentials)
    - [Issuance](#credential-issuance)
    - [Status](#credential-status)
    - [Verification](#credential-verification)
    - [Storage](#credential-storage)
  - [Presentations](#presentations)
    - [Exchanges](#presentation-exchanges)
    - [Workflows](#presentation-workflows)

## Functionalities

Here is an overview of the core features of the Traceability spec implemented.

### DID WEB

The traceability spec relies on `did:web` identifiers to exchange data.

#### Register

We register a `did:web` address in aca-py through the `/wallets/did/create` endpoint. We will store and publish the resulting document based on the created keypair.

#### Resolve

We need the ability to resolve other `did:web` addresses. To do so we leverage the `/resolver/resolve` endpoint in aca-py.

### Credentials

The traceability spec leverages the vc-api endpoints to issue, update and verify credentials.

#### Issuance

Hitting the `/credentials/issue` service endpoint will issue a credential using the `` crypto suite.

#### Status

Every web did will have a `StatusList2021` and a `RevocationList202` credential available for status management.

#### Verification

On top of the aca-py verifications, we will also verify the `expirationDate` as well as the `credentialStatus` of the VCs.

#### Storage

We store the issued credential in a postgres DB with the use of aries-askar. This is to ensure we can update statuses of issued credentials.

### Presentations

#### Exchanges

Presentation exchanges happend over an oauth communication. A submiter will request a token and send a presentation to the `/presentations` service endpoint. 

#### Workflows

Presentations can be linked to a workflow instance ID. These ID's serve to logically group contained credentials. The same ID might be used over several presentations depending on the buisness case.

