# Storage

A postgresDB is used for storage. We use Aries-Askar to manage object stores when reading/writing to the database.

## Stored objects

### DID documents
DID documents are created and stored when a new web did is registered. It will then be publicly resolvable.
The DID documents containe information such as the did controller, verification keys and services.
data key: `didDocuments:{organizationId}`

### Issued credential
When an issuer issues a credential, it will keep a record of this credential to be querried by it's id.
This credential is meant for internal use only mostly to manage the status of this credential.
data key: `issuedCredentials:{organizationId}:{credentialId}`

### Recieved credential
When an entity recieves a presentation, the credentials contained in this credential will be stored, grouped by a workflow ID if present. Otherwise they are stored under a null workflow id
data key: `recievedCredentials:{organizationId}:{workflowId}`

### Status list entries
The status list entries will contain a list of all used indexes from a status list.
This is for the issue to pick an available index when issuing a new credential.
data key: `statusListEntries:{organizationId}:{statusListCredentialId}`

### Status list credentials
This is a store for the status list credentials maintained by an issuer.
Once a list is created, it will be publicly available for verifiers to query the status of a recieved credential.
data key: `statusListCredentials:{organizationId}:{statusListCredentialId}`

### Issuer client hashes
We store a hash of registered issuers for authentication purposes
data key: `issuerClientHashes`

### Holder client hashes
An issuer will be able to generate client credentials for their clients to send them presentations.
We keep a list of client hashes for authentication purposes
data key: `holderClientHashes:{organizationId}`
