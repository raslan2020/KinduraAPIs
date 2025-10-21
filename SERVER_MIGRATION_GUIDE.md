# Complete Server Migration Guide
## Django REST Framework Medical App - Kindura

This guide covers the complete process of migrating your Django REST Framework application from one server to another, including data backup, environment setup, and deployment.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backup from Old Server](#backup-from-old-server)
3. [Prepare New Server](#prepare-new-server)
4. [Install System Dependencies](#install-system-dependencies)
5. [Setup PostgreSQL Database](#setup-postgresql-database)
6. [Deploy Application Code](#deploy-application-code)
7. [Configure Application](#configure-application)
8. [Restore Database](#restore-database)
9. [Final Configuration & Testing](#final-configuration--testing)
10. [Go Live](#go-live)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You Need
- ✅ SSH access to both old and new servers
- ✅ Root or sudo privileges on new server
- ✅ Domain name (optional, but recommended)
- ✅ Basic knowledge of Linux commands

### Information to Gather
- Old server IP address
- New server IP address
- Database credentials
- Domain name settings

---

## Backup from Old Server

### Step 1: Connect to Old Server

```bash
ssh username@old_server_ip
cd /path/to/your/project
```

### Step 2: Backup Django Application Code

```bash
# Navigate to project directory
cd /home/KinduraAPIs

# Create a backup directory
mkdir -p ~/backups
cd ~/backups

# Create timestamped backup
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="kindura_backup_${BACKUP_DATE}"
mkdir $BACKUP_DIR

# Copy entire project (excluding virtual environment)
rsync -av --exclude='env/' \
          --exclude='__pycache__/' \
          --exclude='*.pyc' \
          --exclude='.git/' \
          --exclude='*.log' \
          /home/KinduraAPIs/ $BACKUP_DIR/

echo "✅ Code backup created at: ~/backups/$BACKUP_DIR"
```

### Step 3: Backup PostgreSQL Database

```bash
# Export PostgreSQL database
cd ~/backups/$BACKUP_DIR

# Using pg_dump (recommended for PostgreSQL)
pg_dump -U postgres -h localhost kindura_db > database_backup.sql

# Verify backup file size
ls -lh database_backup.sql

# Alternative: Django's dumpdata (framework-agnostic)
cd /home/KinduraAPIs
source env/bin/activate
python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    -e contenttypes \
    -e auth.Permission \
    --indent 2 \
    -o ~/backups/$BACKUP_DIR/django_data_backup.json

deactivate
```

### Step 4: Backup Environment Variables

```bash
# Copy .env file
cp /home/KinduraAPIs/.env ~/backups/$BACKUP_DIR/.env.backup

# Important: Review and sanitize if needed before transferring
```

### Step 5: Backup Media/Static Files

```bash
# If you have user uploads or static files
cp -r /home/KinduraAPIs/pdf_uploads ~/backups/$BACKUP_DIR/ 2>/dev/null || true
cp -r /home/KinduraAPIs/user_logs ~/backups/$BACKUP_DIR/ 2>/dev/null || true
```

### Step 6: Create Compressed Archive

```bash
cd ~/backups
tar -czf kindura_backup_${BACKUP_DATE}.tar.gz $BACKUP_DIR/

echo "✅ Complete backup created: kindura_backup_${BACKUP_DATE}.tar.gz"
ls -lh kindura_backup_${BACKUP_DATE}.tar.gz
```

### Step 7: Download Backup to Local Machine

```bash
# On your local machine, run:
scp username@old_server_ip:~/backups/kindura_backup_*.tar.gz ~/Downloads/

# Or use alternative methods:
# - SFTP client (FileZilla, WinSCP)
# - rsync
# - Cloud storage (S3, Google Drive)
```

---

## Prepare New Server

### Step 1: Connect to New Server

```bash
ssh username@new_server_ip
```

### Step 2: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 3: Create Project User (Optional but Recommended)

```bash
# Create a dedicated user for the application
sudo adduser kindura
sudo usermod -aG sudo kindura

# Switch to new user
su - kindura
```

### Step 4: Setup Directory Structure

```bash
# Create application directory
mkdir -p ~/applications
cd ~/applications
```

---

## Install System Dependencies

### Step 1: Install Python 3.10

```bash
# Check if Python 3.10 is available
python3.10 --version

# If not installed:
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev -y

# Install pip
sudo apt install python3-pip -y

# Verify installation
python3.10 --version
pip3 --version
```

### Step 2: Install PostgreSQL

```bash
# Install PostgreSQL 14+
sudo apt install postgresql postgresql-contrib -y

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
sudo systemctl status postgresql
psql --version
```

### Step 3: Install Additional System Packages

```bash
# Install build essentials and libraries
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

# Verify installations
gcc --version
nginx -v
```

### Step 4: Install and Configure Firewall (UFW)

```bash
# Install UFW
sudo apt install ufw -y

# Configure firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw allow 5432/tcp  # PostgreSQL (only if needed externally)

# Enable firewall
sudo ufw --force enable
sudo ufw status
```

---

## Setup PostgreSQL Database

### Step 1: Secure PostgreSQL Installation

```bash
# Set password for postgres user
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your_secure_password';"
```

### Step 2: Create Database and User

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# In PostgreSQL prompt, run these commands:
```

```sql
-- Create database
CREATE DATABASE kindura_db;

-- Create user
CREATE USER kindura_user WITH PASSWORD 'your_secure_db_password';

-- Configure user settings
ALTER ROLE kindura_user SET client_encoding TO 'utf8';
ALTER ROLE kindura_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE kindura_user SET timezone TO 'UTC';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE kindura_db TO kindura_user;

-- Connect to the database
\c kindura_db

-- Grant schema permissions (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO kindura_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO kindura_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO kindura_user;

-- Exit PostgreSQL
\q
```

### Step 3: Configure PostgreSQL for Remote Access (if needed)

```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/14/main/postgresql.conf

# Find and modify:
# listen_addresses = 'localhost'  # Change to '*' for all interfaces
# or specify IP: listen_addresses = 'localhost,your_server_ip'

# Edit pg_hba.conf for authentication
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Add this line (adjust as needed):
# host    kindura_db    kindura_user    0.0.0.0/0    md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Step 4: Test Database Connection

```bash
# Test connection
psql -U kindura_user -h localhost -d kindura_db

# If successful, you'll see:
# kindura_db=>

# Exit with \q
```

---

## Deploy Application Code

### Step 1: Transfer Backup to New Server

```bash
# On your local machine:
scp ~/Downloads/kindura_backup_*.tar.gz username@new_server_ip:~/

# Or on the new server, download from old server:
scp username@old_server_ip:~/backups/kindura_backup_*.tar.gz ~/
```

### Step 2: Extract Application Files

```bash
# On new server
cd ~/applications
tar -xzf ~/kindura_backup_*.tar.gz
mv kindura_backup_* KinduraAPIs
cd KinduraAPIs

# Verify files
ls -la
```

### Step 3: Create Python Virtual Environment

```bash
# Create virtual environment
python3.10 -m venv env

# Activate virtual environment
source env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 4: Install Python Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify installations
pip list
```

### Step 5: Set Correct Permissions

```bash
# Set ownership (if using dedicated user)
sudo chown -R kindura:kindura ~/applications/KinduraAPIs

# Set permissions
chmod -R 755 ~/applications/KinduraAPIs
chmod 600 .env  # Protect sensitive file
```

---

## Configure Application

### Step 1: Create and Configure .env File

```bash
cd ~/applications/KinduraAPIs
nano .env
```

Add the following content (adjust values):

```env
# Django Settings
SECRET_KEY=your-new-secret-key-generate-a-new-one
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=kindura_db
DB_USER=kindura_user
DB_PASSWORD=your_secure_db_password
DB_HOST=localhost
DB_PORT=5432

# LiveKit Configuration (from old server)
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_secret
LIVEKIT_URL=your_livekit_url

# Add any other environment variables from old .env.backup
```

### Step 2: Generate New Django Secret Key

```bash
# Generate a new secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Copy the output and update SECRET_KEY in .env
```

### Step 3: Update settings.py (if needed)

```bash
nano medical_app/settings.py
```

Ensure these settings are correct:

```python
# Should already be configured from migration
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Add CSRF trusted origins for your domain
CSRF_TRUSTED_ORIGINS = [
    'https://your-domain.com',
    'https://www.your-domain.com',
]

# Static and Media files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## Restore Database

### Step 1: Run Django Migrations

```bash
cd ~/applications/KinduraAPIs
source env/bin/activate

# Run migrations to create database schema
python manage.py migrate

# Verify migrations
python manage.py showmigrations
```

### Step 2: Restore PostgreSQL Database

**Option A: Using PostgreSQL dump file (Recommended)**

```bash
# Restore from pg_dump backup
psql -U kindura_user -h localhost -d kindura_db < database_backup.sql

# Verify restoration
psql -U kindura_user -h localhost -d kindura_db -c "SELECT COUNT(*) FROM users_user;"
```

**Option B: Using Django fixture file**

```bash
# If you used dumpdata
python manage.py loaddata django_data_backup.json

# Verify
python manage.py shell
```

In Django shell:
```python
from users.models import User
from courses.models import Course
from medicines.models import Medicine

print(f"Users: {User.objects.count()}")
print(f"Courses: {Course.objects.count()}")
print(f"Medicines: {Medicine.objects.count()}")
exit()
```

### Step 3: Create Django Superuser (if needed)

```bash
# Only if you need a new admin account
python manage.py createsuperuser

# Follow the prompts
```

---

## Final Configuration & Testing

### Step 1: Collect Static Files

```bash
# Collect all static files
python manage.py collectstatic --noinput

# Verify static files
ls -la staticfiles/
```

### Step 2: Test Django Application

```bash
# Test the development server
python manage.py runserver 0.0.0.0:8000

# On another terminal or browser:
curl http://localhost:8000
# Or visit http://your-server-ip:8000
```

### Step 3: Setup Gunicorn (Production WSGI Server)

```bash
# Install Gunicorn
pip install gunicorn

# Test Gunicorn
gunicorn medical_app.wsgi:application --bind 0.0.0.0:8000

# Create Gunicorn systemd service
sudo nano /etc/systemd/system/gunicorn.service
```

Add this content:

```ini
[Unit]
Description=Gunicorn daemon for Kindura Medical App
After=network.target

[Service]
User=kindura
Group=kindura
WorkingDirectory=/home/kindura/applications/KinduraAPIs
Environment="PATH=/home/kindura/applications/KinduraAPIs/env/bin"

ExecStart=/home/kindura/applications/KinduraAPIs/env/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/kindura/applications/KinduraAPIs/gunicorn.sock \
          --timeout 120 \
          --access-logfile /home/kindura/applications/KinduraAPIs/logs/gunicorn-access.log \
          --error-logfile /home/kindura/applications/KinduraAPIs/logs/gunicorn-error.log \
          medical_app.wsgi:application

[Install]
WantedBy=multi-user.target
```

Create logs directory:

```bash
mkdir -p ~/applications/KinduraAPIs/logs

# Start and enable Gunicorn
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

### Step 4: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/kindura
```

Add this configuration:

```nginx
upstream kindura_app {
    server unix:/home/kindura/applications/KinduraAPIs/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com your-server-ip;

    client_max_body_size 50M;

    # Logging
    access_log /var/log/nginx/kindura-access.log;
    error_log /var/log/nginx/kindura-error.log;

    # Static files
    location /static/ {
        alias /home/kindura/applications/KinduraAPIs/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/kindura/applications/KinduraAPIs/media/;
        expires 30d;
    }

    # Application
    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://kindura_app;
        
        # WebSocket support (for LiveKit)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

Enable the site:

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/kindura /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl status nginx
```

### Step 5: Setup SSL Certificate (HTTPS)

```bash
# Using Let's Encrypt Certbot
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow the prompts
# Choose option 2 to redirect HTTP to HTTPS

# Test auto-renewal
sudo certbot renew --dry-run

# Certificate will auto-renew
```

---

## Go Live

### Step 1: Update DNS Records

Point your domain to the new server:
- A Record: `your-domain.com` → `new-server-ip`
- A Record: `www.your-domain.com` → `new-server-ip`

Wait for DNS propagation (can take 5 minutes to 48 hours).

### Step 2: Final Testing

```bash
# Test HTTPS
curl https://your-domain.com

# Test API endpoints
curl https://your-domain.com/api/users/ -H "Authorization: Token your-test-token"

# Check logs
sudo tail -f /var/log/nginx/kindura-error.log
tail -f ~/applications/KinduraAPIs/logs/gunicorn-error.log
```

### Step 3: Monitor Application

```bash
# Check all services
sudo systemctl status postgresql
sudo systemctl status gunicorn
sudo systemctl status nginx

# Check disk space
df -h

# Check memory
free -h

# Check processes
htop
```

### Step 4: Setup Automated Backups

Create backup script:

```bash
nano ~/backup_kindura.sh
```

Add:

```bash
#!/bin/bash
BACKUP_DIR="/home/kindura/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U kindura_user kindura_db > $BACKUP_DIR/db_backup_$DATE.sql

# Backup uploaded files
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz ~/applications/KinduraAPIs/media/ 2>/dev/null

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable and schedule:

```bash
chmod +x ~/backup_kindura.sh

# Add to crontab
crontab -e

# Add this line (daily at 2 AM):
0 2 * * * /home/kindura/backup_kindura.sh >> /home/kindura/backup.log 2>&1
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check credentials in .env
cat .env | grep DB_

# Test connection manually
psql -U kindura_user -h localhost -d kindura_db

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

#### 2. Gunicorn Won't Start

```bash
# Check logs
sudo journalctl -u gunicorn -n 50

# Check socket file permissions
ls -la /home/kindura/applications/KinduraAPIs/gunicorn.sock

# Restart service
sudo systemctl restart gunicorn
```

#### 3. Nginx 502 Bad Gateway

```bash
# Check Gunicorn is running
sudo systemctl status gunicorn

# Check Nginx error logs
sudo tail -f /var/log/nginx/kindura-error.log

# Verify socket connection
curl --unix-socket /home/kindura/applications/KinduraAPIs/gunicorn.sock http
```

#### 4. Static Files Not Loading

```bash
# Recollect static files
python manage.py collectstatic --clear --noinput

# Check permissions
ls -la staticfiles/

# Verify Nginx config
sudo nginx -t
```

#### 5. Permission Denied Errors

```bash
# Fix ownership
sudo chown -R kindura:kindura /home/kindura/applications/KinduraAPIs

# Fix permissions
chmod -R 755 /home/kindura/applications/KinduraAPIs
chmod 600 /home/kindura/applications/KinduraAPIs/.env
```

### Getting Help

**Check Logs:**
```bash
# Application logs
tail -f ~/applications/KinduraAPIs/logs/gunicorn-error.log

# Nginx logs
sudo tail -f /var/log/nginx/kindura-error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# System logs
sudo journalctl -xe
```

---

## Maintenance Commands

### Restart Services

```bash
# Restart all services
sudo systemctl restart postgresql
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Or restart all at once
sudo systemctl restart postgresql gunicorn nginx
```

### Update Application

```bash
cd ~/applications/KinduraAPIs
source env/bin/activate

# Pull new code (if using git)
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart Gunicorn
sudo systemctl restart gunicorn
```

### Database Maintenance

```bash
# Create manual backup
pg_dump -U kindura_user kindura_db > backup_$(date +%Y%m%d).sql

# Vacuum database
psql -U kindura_user -d kindura_db -c "VACUUM ANALYZE;"
```

---

## Security Checklist

- [ ] Changed default PostgreSQL password
- [ ] Created strong database user password
- [ ] Generated new Django SECRET_KEY
- [ ] Set DEBUG=False in production
- [ ] Configured firewall (UFW)
- [ ] Installed SSL certificate (HTTPS)
- [ ] Set proper file permissions
- [ ] Configured ALLOWED_HOSTS
- [ ] Setup automated backups
- [ ] Reviewed .env file security
- [ ] Disabled unnecessary services
- [ ] Keep system updated (`sudo apt update && sudo apt upgrade`)

---

## Migration Checklist

**Before Migration:**
- [ ] Backup old server database
- [ ] Backup old server code
- [ ] Backup .env file
- [ ] Document all custom configurations
- [ ] Note all environment variables

**During Migration:**
- [ ] Setup new server
- [ ] Install dependencies
- [ ] Configure PostgreSQL
- [ ] Deploy application
- [ ] Restore database
- [ ] Configure web server

**After Migration:**
- [ ] Test all API endpoints
- [ ] Verify database data
- [ ] Check file uploads work
- [ ] Monitor logs for errors
- [ ] Update DNS records
- [ ] Test from different locations
- [ ] Setup monitoring
- [ ] Configure backups

---

## Quick Reference

### Service Management
```bash
sudo systemctl status postgresql  # Check database
sudo systemctl status gunicorn    # Check app server
sudo systemctl status nginx       # Check web server
```

### Log Files
```bash
~/applications/KinduraAPIs/logs/gunicorn-error.log  # Application
/var/log/nginx/kindura-error.log                    # Web server
/var/log/postgresql/postgresql-14-main.log          # Database
```

### Important Paths
```bash
~/applications/KinduraAPIs/          # Application root
~/applications/KinduraAPIs/env/      # Virtual environment
/etc/nginx/sites-available/kindura   # Nginx config
/etc/systemd/system/gunicorn.service # Gunicorn config
```

---

**✅ Migration Complete!**

Your Django REST Framework application should now be running successfully on the new server with PostgreSQL database and all data intact.
