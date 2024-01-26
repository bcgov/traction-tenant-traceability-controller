# Traceability and Traction feature comparison

## Table of Contents

- [Functionalities](#functionalities)
  - [OAuth](#oauth)
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

### OAuth

We provide a token endpoint for clients to request their tokens. This is how most exchanges are conducted.

### DID WEB

The traceability spec relies on [did:web](https://w3c-ccg.github.io/did-method-web/) identifiers to exchange data.

#### Register

We register a `did:web` address in aca-py through the `/wallets/did/create` endpoint. We will store and publish the resulting document based on the created keypair.

#### Resolve

We need the ability to resolve other `did:web` addresses. To do so we leverage the `/resolver/resolve` endpoint in aca-py.

### Credentials

**The traceability spec leverages the [vc-api](https://w3c-ccg.github.io/vc-api/) spec.**

#### Issuance

Hitting the `/credentials/issue` service endpoint will issue a credential.

#### Status

Every web did will have a [`StatusList2021`](https://www.w3.org/TR/vc-bitstring-status-list/) and a [`RevocationList2020`](https://w3c-ccg.github.io/vc-status-rl-2020/) credential available for status management.
**StatusList2021 was renamed to BitstringStatusList**

#### Verification

On top of the aca-py verifications, we will also verify the `expirationDate` as well as the `credentialStatus` of the VCs.

#### Storage

We store the issued credential in a postgres DB with the use of [aries-askar](https://github.com/hyperledger/aries-askar). This is to ensure we can update statuses of issued credentials.

### Presentations

#### Exchanges

Presentation exchanges happend over an [oauth authentication channel](https://w3c-ccg.github.io/traceability-interop/draft/#presentation-authentication). A submiter will request a token and send a presentation to the `/presentations` service endpoint. 

#### Workflows

Presentations can be linked to a [workflow](https://w3c-ccg.github.io/traceability-vocab/#workflow) instance ID. These ID's serve to logically group contained credentials. The same ID might be used over several presentations depending on the buisness case.

