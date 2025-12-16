# ===========================================
# FlagPilot - RAGFlow Admin User Setup (PowerShell)
# ===========================================
# Creates admin user in RAGFlow when registration is disabled
# Run this after docker compose up -d
#
# Usage: .\scripts\init-ragflow-admin.ps1
# ===========================================

$ErrorActionPreference = "Stop"

# Load .env
$envFile = Get-Content ".env" -ErrorAction SilentlyContinue
$envVars = @{}
foreach ($line in $envFile) {
    if ($line -match '^([^#][^=]+)=(.*)$') {
        $envVars[$matches[1]] = $matches[2]
    }
}

# Defaults
$ADMIN_EMAIL = if ($envVars["RAGFLOW_ADMIN_EMAIL"]) { $envVars["RAGFLOW_ADMIN_EMAIL"] } else { "admin@flagpilot.local" }
$ADMIN_PASSWORD = if ($envVars["RAGFLOW_ADMIN_PASSWORD"]) { $envVars["RAGFLOW_ADMIN_PASSWORD"] } else { "FlagPilot_Admin_2024!" }
$MYSQL_ROOT_PASSWORD = $envVars["MYSQL_ROOT_PASSWORD"]
$MYSQL_DATABASE = "rag_flow"

Write-Host "=== FlagPilot RAGFlow Admin Setup ===" -ForegroundColor Cyan
Write-Host "Admin Email: $ADMIN_EMAIL"

# Wait for MySQL
Write-Host "Waiting for MySQL to be ready..."
for ($i = 1; $i -le 30; $i++) {
    $result = docker exec ragflow-mysql mysqladmin ping -h 127.0.0.1 --silent 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "MySQL is ready!" -ForegroundColor Green
        break
    }
    Write-Host "Waiting... ($i/30)"
    Start-Sleep -Seconds 2
}

# Generate password hash using Python in RAGFlow container
Write-Host "Generating password hash..."
$PASSWORD_HASH = docker exec ragflow-server python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('$ADMIN_PASSWORD'))" 2>$null

if (-not $PASSWORD_HASH) {
    Write-Host "Could not generate password hash." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Enable registration temporarily to create admin account:" -ForegroundColor Cyan
    Write-Host "  1. Set REGISTER_ENABLED=1 in .env"
    Write-Host "  2. docker compose up -d ragflow"
    Write-Host "  3. Register at http://localhost:9380"
    Write-Host "  4. Set REGISTER_ENABLED=0 in .env"
    Write-Host "  5. docker compose up -d ragflow"
    exit 1
}

# Generate 32-char hex ID (RAGFlow uses 32-char varchar, not 36-char UUID)
$USER_ID = docker exec ragflow-server python3 -c "import uuid; print(uuid.uuid4().hex)" 2>$null
$TIMESTAMP = docker exec ragflow-server python3 -c "import time; print(int(time.time() * 1000))" 2>$null

# Create SQL command - matching RAGFlow's exact schema
$SQL = @"
INSERT INTO user (id, create_time, update_time, nickname, password, email, is_authenticated, is_active, is_anonymous, status, is_superuser)
SELECT 
    '$USER_ID' as id,
    $TIMESTAMP as create_time,
    $TIMESTAMP as update_time,
    'Admin' as nickname,
    '$PASSWORD_HASH' as password,
    '$ADMIN_EMAIL' as email,
    '1' as is_authenticated,
    '1' as is_active,
    '0' as is_anonymous,
    '1' as status,
    1 as is_superuser
WHERE NOT EXISTS (
    SELECT 1 FROM user WHERE email = '$ADMIN_EMAIL'
);
"@

# Execute SQL
Write-Host "Creating admin user in RAGFlow database..."
$SQL | docker exec -i ragflow-mysql mysql -u root -p"$MYSQL_ROOT_PASSWORD" $MYSQL_DATABASE 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== RAGFlow Admin Created Successfully ===" -ForegroundColor Green
    Write-Host "Email: $ADMIN_EMAIL" -ForegroundColor Cyan
    Write-Host "Password: $ADMIN_PASSWORD" -ForegroundColor Cyan
    Write-Host "URL: http://localhost:9380"
    Write-Host ""
    Write-Host "NOTE: After login, go to Settings -> API to get your API key." -ForegroundColor Yellow
    Write-Host "      Then update RAGFLOW_API_KEY in .env" -ForegroundColor Yellow
} else {
    Write-Host "Error creating admin user. Checking if user already exists..." -ForegroundColor Yellow
    $checkUser = "SELECT email FROM user WHERE email = '$ADMIN_EMAIL';" | docker exec -i ragflow-mysql mysql -u root -p"$MYSQL_ROOT_PASSWORD" $MYSQL_DATABASE 2>$null
    if ($checkUser -match $ADMIN_EMAIL) {
        Write-Host "User already exists!" -ForegroundColor Green
        Write-Host "Email: $ADMIN_EMAIL" -ForegroundColor Cyan
        Write-Host "URL: http://localhost:9380"
    } else {
        Write-Host "Failed to create admin user." -ForegroundColor Red
        exit 1
    }
}
