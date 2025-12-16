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
MYSQL_DATABASE="rag_flow"

echo "=== FlagPilot RAGFlow Admin Setup ==="
echo "Admin Email: $ADMIN_EMAIL"

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

# Delete existing admin user if exists
echo "Removing existing admin user (if any)..."
docker exec ragflow-mysql mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -e "DELETE FROM user WHERE email = '$ADMIN_EMAIL';" 2>/dev/null || true

# Generate password hash (werkzeug scrypt)
echo "Generating password hash..."
PASSWORD_HASH=$(docker exec ragflow-server python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('$ADMIN_PASSWORD'))" 2>/dev/null)

if [ -z "$PASSWORD_HASH" ]; then
    echo "Could not generate password hash."
    echo ""
    echo "Alternative: Enable registration temporarily to create admin account:"
    echo "  1. Set REGISTER_ENABLED=1 in .env"
    echo "  2. docker compose up -d ragflow"
    echo "  3. Register at http://localhost:9380"
    echo "  4. Set REGISTER_ENABLED=0 in .env"
    echo "  5. docker compose up -d ragflow"
    exit 1
fi

# Generate 32-char hex ID and timestamp
USER_ID=$(docker exec ragflow-server python3 -c "import uuid; print(uuid.uuid4().hex)" 2>/dev/null)
TIMESTAMP=$(docker exec ragflow-server python3 -c "import time; print(int(time.time() * 1000))" 2>/dev/null)

# Create admin user in MySQL (all char fields as strings)
echo "Creating admin user in RAGFlow database..."
docker exec ragflow-mysql mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" <<EOF
INSERT INTO user (id, create_time, update_time, nickname, password, email, is_authenticated, is_active, is_anonymous, status, is_superuser)
VALUES (
    '$USER_ID',
    $TIMESTAMP,
    $TIMESTAMP,
    'Admin',
    '$PASSWORD_HASH',
    '$ADMIN_EMAIL',
    '1',
    '1',
    '0',
    '1',
    1
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
