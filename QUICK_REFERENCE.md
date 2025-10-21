# Quick Reference Guide - Server Migration

## 📋 Pre-Migration Checklist

```bash
# On OLD server
□ Test application is working
□ Document current configuration
□ Note all environment variables
□ Identify all dependencies
□ Check database size: du -sh db.sqlite3 or psql -c "\l+"
```

---

## 🔄 Migration Commands Cheat Sheet

### **Phase 1: Backup Old Server**

```bash
# Quick automated backup
cd /home/KinduraAPIs
chmod +x scripts/backup_for_migration.sh
./scripts/backup_for_migration.sh

# Manual backup commands
BACKUP_DIR=~/backups/kindura_$(date +%Y%m%d)
mkdir -p $BACKUP_DIR

# Backup code
rsync -av --exclude='env/' /home/KinduraAPIs/ $BACKUP_DIR/

# Backup PostgreSQL
pg_dump -U postgres kindura_db > $BACKUP_DIR/database_backup.sql

# Backup Django data
python manage.py dumpdata --indent 2 -o $BACKUP_DIR/data.json

# Create archive
tar -czf ~/kindura_backup.tar.gz -C ~/backups kindura_*
```

### **Phase 2: Transfer to New Server**

```bash
# From local machine
scp user@old_server:~/kindura_backup.tar.gz ~/Downloads/
scp ~/Downloads/kindura_backup.tar.gz user@new_server:~/

# Direct server-to-server
scp user@old_server:~/kindura_backup.tar.gz user@new_server:~/
```

### **Phase 3: Setup New Server**

```bash
# Quick automated deployment
cd ~
tar -xzf kindura_backup.tar.gz
cd kindura_backup_*
chmod +x scripts/deploy_to_new_server.sh
./scripts/deploy_to_new_server.sh

# Manual setup (abbreviated)
sudo apt update && sudo apt upgrade -y
sudo apt install python3.10 python3.10-venv postgresql nginx -y
```

---

## 🗄️ Database Commands

### PostgreSQL Setup

```bash
# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE kindura_db;
CREATE USER kindura_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE kindura_db TO kindura_user;
\c kindura_db
GRANT ALL ON SCHEMA public TO kindura_user;
\q
```

### Backup & Restore

```bash
# Backup
pg_dump -U postgres kindura_db > backup.sql
pg_dump -U postgres kindura_db | gzip > backup.sql.gz  # Compressed

# Restore
psql -U kindura_user -d kindura_db < backup.sql
gunzip < backup.sql.gz | psql -U kindura_user -d kindura_db  # Compressed

# Test connection
psql -U kindura_user -h localhost -d kindura_db

# Check data
psql -U kindura_user -d kindura_db -c "SELECT COUNT(*) FROM users_user;"
```

---

## 🐍 Django Commands

### Migrations

```bash
source env/bin/activate

# Check migrations
python manage.py showmigrations

# Run migrations
python manage.py migrate

# Create new migrations (if models changed)
python manage.py makemigrations
```

### Data Management

```bash
# Export data
python manage.py dumpdata > data.json
python manage.py dumpdata --indent 2 -o data.json  # Formatted
python manage.py dumpdata users > users.json  # Specific app
python manage.py dumpdata --exclude auth.permission > data.json  # Exclude

# Import data
python manage.py loaddata data.json

# Flush database (DANGER!)
python manage.py flush

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell
```

### Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput

# Clear and recollect
python manage.py collectstatic --clear --noinput
```

---

## 🔧 Service Management

### Gunicorn

```bash
# Manual start (testing)
gunicorn medical_app.wsgi:application --bind 0.0.0.0:8000

# Systemd service
sudo systemctl start gunicorn
sudo systemctl stop gunicorn
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
sudo systemctl enable gunicorn  # Auto-start on boot

# View logs
sudo journalctl -u gunicorn -f
tail -f ~/applications/KinduraAPIs/logs/gunicorn-error.log
```

### Nginx

```bash
# Test configuration
sudo nginx -t

# Start/stop/restart
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx  # Reload config without downtime
sudo systemctl status nginx

# View logs
sudo tail -f /var/log/nginx/kindura-error.log
sudo tail -f /var/log/nginx/kindura-access.log
```

### PostgreSQL

```bash
# Start/stop/restart
sudo systemctl start postgresql
sudo systemctl stop postgresql
sudo systemctl restart postgresql
sudo systemctl status postgresql

# View logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### All Services

```bash
# Restart all
sudo systemctl restart postgresql gunicorn nginx

# Check all
sudo systemctl status postgresql gunicorn nginx
```

---

## 🔒 SSL Certificate (Let's Encrypt)

```bash
# Install certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Renew (automatic)
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# View certificates
sudo certbot certificates

# Revoke certificate
sudo certbot revoke --cert-path /etc/letsencrypt/live/yourdomain.com/cert.pem
```

---

## 📊 Monitoring & Debugging

### System Resources

```bash
# Disk space
df -h
du -sh /home/KinduraAPIs/*

# Memory
free -h
cat /proc/meminfo

# CPU & Processes
htop  # Interactive
top   # Basic
ps aux | grep gunicorn
ps aux | grep nginx
```

### Application Logs

```bash
# Real-time monitoring
tail -f ~/applications/KinduraAPIs/logs/gunicorn-error.log
sudo tail -f /var/log/nginx/kindura-error.log
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# Last N lines
tail -n 100 ~/applications/KinduraAPIs/logs/gunicorn-error.log

# Search logs
grep "ERROR" ~/applications/KinduraAPIs/logs/gunicorn-error.log
```

### Network & Connectivity

```bash
# Check ports
sudo netstat -tulpn | grep LISTEN
sudo ss -tulpn | grep LISTEN

# Test endpoints
curl http://localhost:8000
curl https://yourdomain.com
curl -I https://yourdomain.com  # Headers only

# DNS check
nslookup yourdomain.com
dig yourdomain.com
```

### Database Checks

```bash
# Database size
psql -U postgres -c "\l+"

# Table sizes
psql -U kindura_user -d kindura_db -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Row counts
psql -U kindura_user -d kindura_db -c "
SELECT schemaname, tablename, n_live_tup 
FROM pg_stat_user_tables 
ORDER BY n_live_tup DESC;"

# Active connections
psql -U postgres -c "SELECT * FROM pg_stat_activity;"
```

---

## 🛡️ Security

### Firewall (UFW)

```bash
# Check status
sudo ufw status verbose

# Allow/deny
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw deny 5432/tcp  # PostgreSQL (if not needed externally)

# Enable/disable
sudo ufw enable
sudo ufw disable

# Reset
sudo ufw reset
```

### File Permissions

```bash
# Set ownership
sudo chown -R username:username /home/username/applications/KinduraAPIs

# Set permissions
chmod -R 755 /home/username/applications/KinduraAPIs
chmod 600 /home/username/applications/KinduraAPIs/.env

# Check permissions
ls -la /home/username/applications/KinduraAPIs
```

---

## 🔄 Automated Backups

### Create Backup Script

```bash
# Create script
cat > ~/backup_daily.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="$HOME/backups"
DATE=$(date +%Y%m%d)
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U kindura_user kindura_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
EOF

chmod +x ~/backup_daily.sh
```

### Schedule with Cron

```bash
# Edit crontab
crontab -e

# Add these lines:
# Daily backup at 2 AM
0 2 * * * /home/username/backup_daily.sh

# Weekly backup on Sunday at 3 AM
0 3 * * 0 /home/username/backup_weekly.sh

# View cron jobs
crontab -l

# View cron logs
grep CRON /var/log/syslog
```

---

## 🔍 Troubleshooting Quick Fixes

### Issue: Gunicorn won't start

```bash
# Check socket permissions
ls -la ~/applications/KinduraAPIs/gunicorn.sock
sudo chown username:www-data ~/applications/KinduraAPIs/gunicorn.sock

# Check logs
sudo journalctl -u gunicorn -n 50
```

### Issue: 502 Bad Gateway

```bash
# Check Gunicorn is running
sudo systemctl status gunicorn

# Restart services
sudo systemctl restart gunicorn nginx

# Check socket connection
curl --unix-socket ~/applications/KinduraAPIs/gunicorn.sock http
```

### Issue: Database connection failed

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U kindura_user -h localhost -d kindura_db

# Check credentials
cat ~/applications/KinduraAPIs/.env | grep DB_
```

### Issue: Static files not loading

```bash
# Recollect static files
cd ~/applications/KinduraAPIs
source env/bin/activate
python manage.py collectstatic --clear --noinput

# Check permissions
ls -la staticfiles/
sudo chown -R username:www-data staticfiles/
```

### Issue: Permission denied

```bash
# Fix ownership
sudo chown -R username:username ~/applications/KinduraAPIs

# Fix permissions
chmod -R 755 ~/applications/KinduraAPIs
chmod 600 ~/applications/KinduraAPIs/.env
```

---

## 📝 Environment Variables Template

```bash
# ~/.applications/KinduraAPIs/.env

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,server-ip

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=kindura_db
DB_USER=kindura_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# LiveKit (if applicable)
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
LIVEKIT_URL=your_livekit_url

# CSRF
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## 🚀 Deployment Checklist

**Pre-deployment:**
- [ ] Backup created and verified
- [ ] DNS records updated
- [ ] SSL certificate ready

**During deployment:**
- [ ] Server updated: `sudo apt update && sudo apt upgrade`
- [ ] Dependencies installed
- [ ] Database created and configured
- [ ] Code deployed
- [ ] Environment variables set
- [ ] Migrations run
- [ ] Data restored
- [ ] Static files collected

**Post-deployment:**
- [ ] Services started and enabled
- [ ] SSL configured
- [ ] Firewall configured
- [ ] Application tested
- [ ] Monitoring setup
- [ ] Backups automated
- [ ] Documentation updated

---

## 📞 Quick Commands Summary

```bash
# Start everything
sudo systemctl start postgresql gunicorn nginx

# Restart everything
sudo systemctl restart postgresql gunicorn nginx

# Check everything
sudo systemctl status postgresql gunicorn nginx

# View all logs
sudo tail -f /var/log/nginx/kindura-error.log \
              ~/applications/KinduraAPIs/logs/gunicorn-error.log \
              /var/log/postgresql/postgresql-14-main.log

# Full application restart
cd ~/applications/KinduraAPIs
source env/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn nginx
```

---

**🎯 Need more help?** Refer to `SERVER_MIGRATION_GUIDE.md` for detailed step-by-step instructions.
