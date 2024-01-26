# /bin/python3

echo "ASKAR_SEED: $(openssl rand -base64 24)"
echo "JWT_SECRET: $(uuidgen)"
echo "VERIFIER_API_KEY: $(uuidgen)"
echo "TRACEABILITY_ADMIN_API_KEY: $(uuidgen)"