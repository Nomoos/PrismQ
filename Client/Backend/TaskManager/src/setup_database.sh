#!/bin/bash
# Database Setup Script for TaskManager
# Initializes the database schema and seeds endpoint definitions

set -e

echo "TaskManager Database Setup"
echo "=========================="
echo ""

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_NAME="${DB_NAME:-taskmanager_test}"
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASS:-}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DB_DIR="$SCRIPT_DIR/database"

echo "Database Configuration:"
echo "  Host: $DB_HOST"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Check if MySQL is available
if ! command -v mysql &> /dev/null; then
    echo "Error: mysql command not found. Please install MySQL client."
    exit 1
fi

# Create database if it doesn't exist
echo "Creating database if not exists..."
if [ -z "$DB_PASS" ]; then
    mysql -h "$DB_HOST" -u "$DB_USER" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
else
    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
fi

# Import schema
echo "Importing database schema..."
if [ -z "$DB_PASS" ]; then
    mysql -h "$DB_HOST" -u "$DB_USER" "$DB_NAME" < "$DB_DIR/schema.sql"
else
    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$DB_DIR/schema.sql"
fi

# Import seed data
echo "Seeding endpoint definitions..."
if [ -z "$DB_PASS" ]; then
    mysql -h "$DB_HOST" -u "$DB_USER" "$DB_NAME" < "$DB_DIR/seed_endpoints.sql"
else
    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$DB_DIR/seed_endpoints.sql"
fi

echo ""
echo "✓ Database setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update config/config.php with your database credentials"
echo "2. Test the API: curl http://localhost/api/health"
echo ""
