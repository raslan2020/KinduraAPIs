#!/bin/bash

# PostgreSQL Database Setup Script for Kindura Medical App
# This script helps automate the PostgreSQL database creation

set -e

echo "🚀 Kindura Medical App - PostgreSQL Setup"
echo "=========================================="
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed."
    echo "Please install PostgreSQL first:"
    echo "  sudo apt update"
    echo "  sudo apt install postgresql postgresql-contrib"
    exit 1
fi

echo "✅ PostgreSQL found!"
echo ""

# Get database configuration
read -p "Enter database name [kindura_db]: " DB_NAME
DB_NAME=${DB_NAME:-kindura_db}

read -p "Enter database user [kindura_user]: " DB_USER
DB_USER=${DB_USER:-kindura_user}

read -sp "Enter database password: " DB_PASSWORD
echo ""

read -p "Enter database host [localhost]: " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "Enter database port [5432]: " DB_PORT
DB_PORT=${DB_PORT:-5432}

echo ""
echo "Creating PostgreSQL database..."

# Create database and user
sudo -u postgres psql <<EOF
-- Drop database if exists (uncomment if you want to recreate)
-- DROP DATABASE IF EXISTS $DB_NAME;
-- DROP USER IF EXISTS $DB_USER;

-- Create database and user
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Configure user
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'UTC';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- PostgreSQL 15+ requires additional permissions
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;

EOF

echo ""
echo "✅ Database created successfully!"
echo ""
echo "📝 Add these lines to your .env file:"
echo "=========================================="
echo "DB_ENGINE=django.db.backends.postgresql"
echo "DB_NAME=$DB_NAME"
echo "DB_USER=$DB_USER"
echo "DB_PASSWORD=$DB_PASSWORD"
echo "DB_HOST=$DB_HOST"
echo "DB_PORT=$DB_PORT"
echo "=========================================="
echo ""

# Offer to update .env file
read -p "Would you like to automatically update .env file? (y/n): " UPDATE_ENV

if [ "$UPDATE_ENV" = "y" ] || [ "$UPDATE_ENV" = "Y" ]; then
    ENV_FILE=".env"
    
    # Backup existing .env
    if [ -f "$ENV_FILE" ]; then
        cp "$ENV_FILE" "${ENV_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
        echo "✅ Backed up existing .env file"
    fi
    
    # Remove old DB settings if they exist
    sed -i '/^DB_ENGINE=/d' "$ENV_FILE" 2>/dev/null || true
    sed -i '/^DB_NAME=/d' "$ENV_FILE" 2>/dev/null || true
    sed -i '/^DB_USER=/d' "$ENV_FILE" 2>/dev/null || true
    sed -i '/^DB_PASSWORD=/d' "$ENV_FILE" 2>/dev/null || true
    sed -i '/^DB_HOST=/d' "$ENV_FILE" 2>/dev/null || true
    sed -i '/^DB_PORT=/d' "$ENV_FILE" 2>/dev/null || true
    
    # Add new DB settings
    {
        echo ""
        echo "# PostgreSQL Database Configuration"
        echo "DB_ENGINE=django.db.backends.postgresql"
        echo "DB_NAME=$DB_NAME"
        echo "DB_USER=$DB_USER"
        echo "DB_PASSWORD=$DB_PASSWORD"
        echo "DB_HOST=$DB_HOST"
        echo "DB_PORT=$DB_PORT"
    } >> "$ENV_FILE"
    
    echo "✅ .env file updated successfully!"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Run migrations: python manage.py migrate"
echo "2. Load data: python manage.py loaddata data_backup.json"
echo "3. Start server: python manage.py runserver"
echo ""
echo "✅ Setup complete!"
