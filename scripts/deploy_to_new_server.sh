#!/bin/bash

################################################################################
# New Server Deployment Script
# Run this script on the NEW server after transferring backup
################################################################################

set -e

echo "🚀 Kindura Medical App - New Server Deployment"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Please do not run this script as root${NC}"
    exit 1
fi

# Configuration
APP_DIR="$HOME/applications/KinduraAPIs"
BACKUP_FILE=""

# Step 1: System Update
echo -e "${BLUE}Step 1/10: Updating system packages...${NC}"
sudo apt update
sudo apt upgrade -y
echo -e "${GREEN}✅ System updated${NC}"

# Step 2: Install Python 3.10
echo ""
echo -e "${BLUE}Step 2/10: Installing Python 3.10...${NC}"
if ! command -v python3.10 &> /dev/null; then
    sudo apt install software-properties-common -y
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install python3.10 python3.10-venv python3.10-dev python3-pip -y
    echo -e "${GREEN}✅ Python 3.10 installed${NC}"
else
    echo -e "${GREEN}✅ Python 3.10 already installed${NC}"
fi

# Step 3: Install PostgreSQL
echo ""
echo -e "${BLUE}Step 3/10: Installing PostgreSQL...${NC}"
if ! command -v psql &> /dev/null; then
    sudo apt install postgresql postgresql-contrib -y
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    echo -e "${GREEN}✅ PostgreSQL installed${NC}"
else
    echo -e "${GREEN}✅ PostgreSQL already installed${NC}"
fi

# Step 4: Install System Dependencies
echo ""
echo -e "${BLUE}Step 4/10: Installing system dependencies...${NC}"
sudo apt install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    nginx \
    git \
    curl \
    wget \
    supervisor \
    certbot \
    python3-certbot-nginx

echo -e "${GREEN}✅ System dependencies installed${NC}"

# Step 5: Configure Firewall
echo ""
echo -e "${BLUE}Step 5/10: Configuring firewall...${NC}"
sudo apt install ufw -y
sudo ufw --force enable
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
echo -e "${GREEN}✅ Firewall configured${NC}"

# Step 6: Setup PostgreSQL Database
echo ""
echo -e "${BLUE}Step 6/10: Setting up PostgreSQL database...${NC}"
read -p "Enter database name [kindura_db]: " DB_NAME
DB_NAME=${DB_NAME:-kindura_db}

read -p "Enter database user [kindura_user]: " DB_USER
DB_USER=${DB_USER:-kindura_user}

read -sp "Enter database password: " DB_PASSWORD
echo ""

echo "Creating database and user..."
sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
EOF

echo -e "${GREEN}✅ Database created${NC}"

# Step 7: Extract Application
echo ""
echo -e "${BLUE}Step 7/10: Setting up application...${NC}"
read -p "Enter path to backup file (e.g., ~/kindura_backup_*.tar.gz): " BACKUP_FILE

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

mkdir -p "$HOME/applications"
cd "$HOME/applications"
tar -xzf "$BACKUP_FILE"

# Find the extracted directory
EXTRACTED_DIR=$(tar -tzf "$BACKUP_FILE" | head -1 | cut -f1 -d"/")
if [ -d "$EXTRACTED_DIR" ]; then
    mv "$EXTRACTED_DIR" KinduraAPIs
fi

cd KinduraAPIs
echo -e "${GREEN}✅ Application extracted${NC}"

# Step 8: Setup Virtual Environment
echo ""
echo -e "${BLUE}Step 8/10: Creating virtual environment...${NC}"
python3.10 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Virtual environment created and packages installed${NC}"

# Step 9: Configure Environment Variables
echo ""
echo -e "${BLUE}Step 9/10: Configuring environment variables...${NC}"

read -p "Enter your domain name (or IP address): " DOMAIN
read -sp "Enter new Django SECRET_KEY (or press Enter to generate): " SECRET_KEY
echo ""

if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
fi

cat > .env << EOF
# Django Settings
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Add your other environment variables from .env.backup here
EOF

echo -e "${GREEN}✅ Environment variables configured${NC}"
echo -e "${YELLOW}⚠️  Please review and update .env file with additional settings${NC}"

# Step 10: Run Migrations and Restore Data
echo ""
echo -e "${BLUE}Step 10/10: Running migrations and restoring data...${NC}"

python manage.py migrate

echo ""
echo "Choose restoration method:"
echo "1) PostgreSQL dump (database_backup.sql)"
echo "2) Django fixture (django_data_backup.json)"
read -p "Enter choice [1]: " RESTORE_CHOICE
RESTORE_CHOICE=${RESTORE_CHOICE:-1}

if [ "$RESTORE_CHOICE" = "1" ]; then
    if [ -f "database_backup.sql" ]; then
        psql -U "$DB_USER" -h localhost -d "$DB_NAME" < database_backup.sql
        echo -e "${GREEN}✅ Database restored from PostgreSQL dump${NC}"
    else
        echo -e "${RED}❌ database_backup.sql not found${NC}"
    fi
elif [ "$RESTORE_CHOICE" = "2" ]; then
    if [ -f "django_data_backup.json" ]; then
        python manage.py loaddata django_data_backup.json
        echo -e "${GREEN}✅ Data restored from Django fixture${NC}"
    else
        echo -e "${RED}❌ django_data_backup.json not found${NC}"
    fi
fi

# Collect static files
mkdir -p staticfiles
python manage.py collectstatic --noinput
echo -e "${GREEN}✅ Static files collected${NC}"

# Create logs directory
mkdir -p logs

deactivate

# Summary and next steps
echo ""
echo "=================================================="
echo -e "${GREEN}✅ DEPLOYMENT COMPLETED!${NC}"
echo "=================================================="
echo ""
echo "Next Steps to Complete Setup:"
echo ""
echo "1. Review and update .env file:"
echo "   nano $APP_DIR/.env"
echo ""
echo "2. Setup Gunicorn service:"
echo "   Follow instructions in SERVER_MIGRATION_GUIDE.md (Step 3)"
echo ""
echo "3. Configure Nginx:"
echo "   Follow instructions in SERVER_MIGRATION_GUIDE.md (Step 4)"
echo ""
echo "4. Setup SSL certificate:"
echo "   sudo certbot --nginx -d $DOMAIN"
echo ""
echo "5. Start services:"
echo "   sudo systemctl start gunicorn"
echo "   sudo systemctl start nginx"
echo ""
echo "6. Test the application:"
echo "   curl http://localhost:8000"
echo ""
echo "=================================================="
