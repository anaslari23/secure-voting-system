#!/bin/bash
# Generate self-signed SSL certificates for local development
# This script creates cert.pem and key.pem in the backend/ directory

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "🔐 Generating SSL certificates for local development..."

# Create backend directory if it doesn't exist
mkdir -p "$BACKEND_DIR"

# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out "$BACKEND_DIR/cert.pem" \
  -keyout "$BACKEND_DIR/key.pem" \
  -days 365 \
  -subj "/C=IN/ST=Delhi/L=New Delhi/O=Election Commission/OU=IT/CN=localhost"

echo "✅ SSL certificates generated successfully!"
echo "   - Certificate: $BACKEND_DIR/cert.pem"
echo "   - Private Key: $BACKEND_DIR/key.pem"
echo ""
echo "⚠️  These are self-signed certificates for development only."
echo "   Your browser will show a security warning - this is expected."
echo "   For production, use certificates from a trusted Certificate Authority."
