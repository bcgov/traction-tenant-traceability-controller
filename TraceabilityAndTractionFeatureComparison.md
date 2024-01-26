# Traceability and Traction feature comparison

## Table of Contents

- [Functionalities](#functionalities)
  - [OAuth](#oauth)
  - [DID WEB](#did-web)
    - [Register and Resolve](#register-and-resolve)
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

We offer a dynamic token endpoint, inviting clients to seamlessly request their access tokens. This is the pivotal hub where the majority of exchanges come to life, fostering a streamlined and efficient interaction.

### DID WEB

The traceability specification hinges on the utilization of [did:web](https://w3c-ccg.github.io/did-method-web/) identifiers, providing a robust foundation for seamless data exchange.

#### Register and Resolve

We seamlessly register a `did:web` address within aca-py using the `/wallets/did/create` endpoint, ensuring a secure keypair is generated. Subsequently, we store and publish the resulting document, laying the groundwork for further exchanges.

To resolve other `did:web` addresses, we use the `/resolver/resolve` endpoint in aca-py.

### Credentials

**The traceability spec leverages the [vc-api](https://w3c-ccg.github.io/vc-api/) spec.**

#### Issuance

Hitting the `/credentials/issue` service endpoint will issue a credential.

#### Status

Each web did is equipped with both a [`StatusList2021`](https://www.w3.org/TR/vc-bitstring-status-list/) and a [`RevocationList2020`](https://w3c-ccg.github.io/vc-status-rl-2020/) credential, serving as essential components for effective status management.
**StatusList2021 was renamed to BitstringStatusList**

#### Verification

In addition to aca-py verifications, we will conduct thorough checks on the `expirationDate` and `credentialStatus` of the Verified Credentials (VCs).

#### Storage

We securely store the issued credential in a PostgreSQL database, leveraging [aries-askar](https://github.com/hyperledger/aries-askar). This approach ensures the ability to efficiently update the statuses of issued credentials as needed.

### Presentations

#### Exchanges

Presentation exchanges occur over an [OAuth authentication channel](https://w3c-ccg.github.io/traceability-interop/draft/#presentation-authentication). A submitter initiates the process by requesting a token and subsequently sends a presentation to the `/presentations` service endpoint.

#### Workflows

Presentations have the capability to be linked to a [workflow](https://w3c-ccg.github.io/traceability-vocab/#workflow) instance ID. These IDs play a crucial role in logically grouping the credentials within, allowing for a structured organization. Depending on the specific business case, the same ID might be employed across multiple presentations.
