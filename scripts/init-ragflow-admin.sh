#!/bin/bash
# ===========================================
# FlagPilot - RAGFlow Admin User Setup
# ===========================================
# Creates admin user in RAGFlow when registration is disabled
# Run this after docker compose up -d
#
# Usage: ./scripts/init-ragflow-admin.sh
# ===========================================

set -e

# Load .env if exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Defaults
ADMIN_EMAIL="${RAGFLOW_ADMIN_EMAIL:-admin@flagpilot.local}"
ADMIN_PASSWORD="${RAGFLOW_ADMIN_PASSWORD:-FlagPilot_Admin_2024!}"
MYSQL_HOST="127.0.0.1"
MYSQL_PORT="${MYSQL_PORT:-5455}"
MYSQL_USER="${MYSQL_USER:-rag_flow}"
MYSQL_PASSWORD="${MYSQL_PASSWORD}"
MYSQL_DATABASE="rag_flow"

echo "=== FlagPilot RAGFlow Admin Setup ==="
echo "Admin Email: $ADMIN_EMAIL"
echo "MySQL Host: $MYSQL_HOST:$MYSQL_PORT"

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
for i in {1..30}; do
    if docker exec ragflow-mysql mysqladmin ping -h 127.0.0.1 --silent 2>/dev/null; then
        echo "MySQL is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Generate password hash (bcrypt - RAGFlow uses werkzeug)
# We'll use Python inside the container to generate the hash
echo "Generating password hash..."
PASSWORD_HASH=$(docker exec ragflow-server python3 -c "
from werkzeug.security import generate_password_hash
print(generate_password_hash('$ADMIN_PASSWORD'))
" 2>/dev/null)

if [ -z "$PASSWORD_HASH" ]; then
    echo "Error: Failed to generate password hash"
    echo "Trying alternative method..."
    # Fallback - use bcrypt if available
    PASSWORD_HASH=$(docker exec ragflow-mysql python3 -c "
import hashlib
import os
salt = os.urandom(16).hex()
h = hashlib.pbkdf2_hmac('sha256', b'$ADMIN_PASSWORD', salt.encode(), 100000).hex()
print(f'pbkdf2:sha256:100000\${salt}\${h}')
" 2>/dev/null || echo "")
fi

if [ -z "$PASSWORD_HASH" ]; then
    echo "Could not generate password hash. RAGFlow admin may need manual setup."
    echo ""
    echo "Alternative: Enable registration temporarily to create admin account:"
    echo "  1. Set REGISTER_ENABLED=1 in .env"
    echo "  2. docker compose up -d ragflow"
    echo "  3. Register at http://localhost:9380"
    echo "  4. Set REGISTER_ENABLED=0 in .env"
    echo "  5. docker compose up -d ragflow"
    exit 1
fi

# Create admin user in MySQL
echo "Creating admin user in RAGFlow database..."
docker exec ragflow-mysql mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" <<EOF
-- Create admin user if not exists
INSERT INTO user (id, nickname, email, password, status, is_superuser, create_time, update_time)
SELECT 
    UUID() as id,
    'Admin' as nickname,
    '$ADMIN_EMAIL' as email,
    '$PASSWORD_HASH' as password,
    'active' as status,
    1 as is_superuser,
    NOW() as create_time,
    NOW() as update_time
WHERE NOT EXISTS (
    SELECT 1 FROM user WHERE email = '$ADMIN_EMAIL'
);
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=== RAGFlow Admin Created Successfully ==="
    echo "Email: $ADMIN_EMAIL"
    echo "Password: $ADMIN_PASSWORD"
    echo "URL: http://localhost:9380"
    echo ""
    echo "NOTE: After login, go to Settings -> API to get your API key."
    echo "      Then update RAGFLOW_API_KEY in .env"
else
    echo "Error creating admin user. Please check MySQL logs."
    exit 1
fi
