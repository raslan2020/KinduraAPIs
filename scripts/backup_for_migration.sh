#!/bin/bash

################################################################################
# Backup Script for Server Migration
# This script creates a complete backup of your Django application
################################################################################

set -e

echo "🚀 Kindura Medical App - Migration Backup Script"
echo "=================================================="
echo ""

# Configuration
PROJECT_DIR="/home/KinduraAPIs"
BACKUP_BASE_DIR="$HOME/backups"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_BASE_DIR/kindura_backup_${BACKUP_DATE}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create backup directory
echo -e "${BLUE}Creating backup directory...${NC}"
mkdir -p "$BACKUP_DIR"

# Step 1: Backup Application Code
echo ""
echo -e "${BLUE}Step 1/5: Backing up application code...${NC}"
rsync -av --progress \
    --exclude='env/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.git/' \
    --exclude='*.log' \
    --exclude='db.sqlite3' \
    "$PROJECT_DIR/" "$BACKUP_DIR/"

echo -e "${GREEN}✅ Code backup complete${NC}"

# Step 2: Backup PostgreSQL Database
echo ""
echo -e "${BLUE}Step 2/5: Backing up PostgreSQL database...${NC}"
read -p "Enter database name [kindura_db]: " DB_NAME
DB_NAME=${DB_NAME:-kindura_db}

read -p "Enter database user [postgres]: " DB_USER
DB_USER=${DB_USER:-postgres}

echo "Creating PostgreSQL dump..."
pg_dump -U "$DB_USER" -h localhost "$DB_NAME" > "$BACKUP_DIR/database_backup.sql"

if [ -f "$BACKUP_DIR/database_backup.sql" ]; then
    echo -e "${GREEN}✅ Database backup complete ($(du -h $BACKUP_DIR/database_backup.sql | cut -f1))${NC}"
else
    echo -e "${RED}❌ Database backup failed${NC}"
    exit 1
fi

# Step 3: Django dumpdata (as alternative backup)
echo ""
echo -e "${BLUE}Step 3/5: Creating Django fixture backup...${NC}"
cd "$PROJECT_DIR"
if [ -d "env" ]; then
    source env/bin/activate
    python manage.py dumpdata \
        --natural-foreign \
        --natural-primary \
        -e contenttypes \
        -e auth.Permission \
        --indent 2 \
        -o "$BACKUP_DIR/django_data_backup.json"
    
    if [ -f "$BACKUP_DIR/django_data_backup.json" ]; then
        echo -e "${GREEN}✅ Django fixture backup complete ($(du -h $BACKUP_DIR/django_data_backup.json | cut -f1))${NC}"
    fi
    deactivate
else
    echo -e "${RED}⚠️  Virtual environment not found, skipping Django backup${NC}"
fi

# Step 4: Backup configuration files
echo ""
echo -e "${BLUE}Step 4/5: Backing up configuration files...${NC}"

# Copy .env if exists
if [ -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env" "$BACKUP_DIR/.env.backup"
    echo -e "${GREEN}✅ .env file backed up${NC}"
fi

# Copy requirements.txt
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    cp "$PROJECT_DIR/requirements.txt" "$BACKUP_DIR/"
    echo -e "${GREEN}✅ requirements.txt backed up${NC}"
fi

# Step 5: Create migration notes
echo ""
echo -e "${BLUE}Step 5/5: Creating migration notes...${NC}"
cat > "$BACKUP_DIR/MIGRATION_INFO.txt" << EOF
==============================================
Kindura Medical App - Migration Backup
==============================================

Backup Date: $(date)
Backup Location: $BACKUP_DIR

DATABASE INFORMATION:
- Database Name: $DB_NAME
- Database User: $DB_USER
- Database Engine: PostgreSQL

BACKUP CONTENTS:
- Application Code: Yes
- PostgreSQL Dump: Yes (database_backup.sql)
- Django Fixture: $([ -f "$BACKUP_DIR/django_data_backup.json" ] && echo "Yes (django_data_backup.json)" || echo "No")
- Environment File: $([ -f "$BACKUP_DIR/.env.backup" ] && echo "Yes (.env.backup)" || echo "No")
- Requirements: $([ -f "$BACKUP_DIR/requirements.txt" ] && echo "Yes" || echo "No")

PYTHON VERSION:
$(python3 --version)

INSTALLED PACKAGES:
$(pip list | head -20)

MIGRATION INSTRUCTIONS:
See SERVER_MIGRATION_GUIDE.md for complete deployment instructions.

IMPORTANT NOTES:
1. Review and update .env.backup before deploying
2. Generate new SECRET_KEY for production
3. Update ALLOWED_HOSTS in settings
4. Set DEBUG=False for production
5. Setup SSL certificate
6. Configure firewall rules

EOF

echo -e "${GREEN}✅ Migration notes created${NC}"

# Step 6: Create compressed archive
echo ""
echo -e "${BLUE}Creating compressed archive...${NC}"
cd "$BACKUP_BASE_DIR"
tar -czf "kindura_backup_${BACKUP_DATE}.tar.gz" "kindura_backup_${BACKUP_DATE}/"

ARCHIVE_SIZE=$(du -h "kindura_backup_${BACKUP_DATE}.tar.gz" | cut -f1)
echo -e "${GREEN}✅ Archive created: kindura_backup_${BACKUP_DATE}.tar.gz ($ARCHIVE_SIZE)${NC}"

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}✅ BACKUP COMPLETED SUCCESSFULLY!${NC}"
echo "=================================================="
echo ""
echo "Backup Details:"
echo "  📁 Location: $BACKUP_DIR"
echo "  📦 Archive: $BACKUP_BASE_DIR/kindura_backup_${BACKUP_DATE}.tar.gz"
echo "  💾 Size: $ARCHIVE_SIZE"
echo ""
echo "Next Steps:"
echo "  1. Download the backup archive to your local machine:"
echo "     scp username@server_ip:$BACKUP_BASE_DIR/kindura_backup_${BACKUP_DATE}.tar.gz ~/"
echo ""
echo "  2. Transfer to new server:"
echo "     scp ~/kindura_backup_${BACKUP_DATE}.tar.gz username@new_server_ip:~/"
echo ""
echo "  3. Follow SERVER_MIGRATION_GUIDE.md for deployment"
echo ""
echo "=================================================="
