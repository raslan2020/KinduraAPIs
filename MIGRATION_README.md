# Server Migration Documentation

Welcome! This directory contains complete documentation and automation scripts for migrating your Django REST Framework Medical App (Kindura) from one server to another.

## 📚 Documentation Files

### 1. **SERVER_MIGRATION_GUIDE.md** (Main Guide)
**👉 START HERE**

Complete step-by-step guide covering:
- Prerequisites and preparation
- Backing up from old server
- Setting up new server
- Installing all dependencies (Python, PostgreSQL, Nginx, etc.)
- Database setup and configuration
- Application deployment
- SSL certificate setup
- Production configuration
- Troubleshooting

**When to use:** Follow this for complete understanding of the entire migration process.

---

### 2. **QUICK_REFERENCE.md** (Command Cheat Sheet)
Quick reference for common commands and operations:
- Pre-migration checklist
- All migration commands
- Database backup/restore commands
- Django management commands
- Service management (Gunicorn, Nginx, PostgreSQL)
- SSL certificate commands
- Monitoring and debugging
- Troubleshooting quick fixes

**When to use:** Quick lookup for specific commands during or after migration.

---

### 3. **POSTGRES_MIGRATION_GUIDE.md**
Specific guide for migrating from SQLite to PostgreSQL (already completed):
- PostgreSQL installation
- Database creation
- Django settings update
- Data migration
- Rollback procedures

**When to use:** Already completed, but useful for reference.

---

## 🛠️ Automation Scripts

### 1. **scripts/backup_for_migration.sh**
Automated backup script for old server.

**What it does:**
- Backs up application code
- Exports PostgreSQL database
- Creates Django fixture backup
- Backs up configuration files (.env)
- Creates compressed archive
- Generates migration notes

**Usage:**
```bash
cd /home/KinduraAPIs
./scripts/backup_for_migration.sh
```

**Output:** 
- `~/backups/kindura_backup_YYYYMMDD_HHMMSS.tar.gz`

---

### 2. **scripts/deploy_to_new_server.sh**
Automated deployment script for new server.

**What it does:**
- Updates system packages
- Installs Python 3.10
- Installs PostgreSQL
- Installs system dependencies
- Configures firewall
- Creates database and user
- Extracts application
- Sets up virtual environment
- Configures environment variables
- Runs migrations
- Restores data
- Collects static files

**Usage:**
```bash
# On new server, after transferring backup
cd ~
./deploy_to_new_server.sh
```

---

### 3. **setup_postgres.sh**
PostgreSQL database setup helper (already used).

**What it does:**
- Creates PostgreSQL database
- Creates database user
- Sets proper permissions
- Updates .env file

---

## 🚀 Migration Process Overview

### Quick Start (Automated)

**On OLD Server:**
```bash
cd /home/KinduraAPIs
./scripts/backup_for_migration.sh
# Download the generated .tar.gz file
```

**Transfer to NEW Server:**
```bash
scp kindura_backup_*.tar.gz user@new_server:~/
```

**On NEW Server:**
```bash
cd ~
tar -xzf kindura_backup_*.tar.gz
cd kindura_backup_*/
./scripts/deploy_to_new_server.sh
# Follow the prompts
```

**Complete Setup:**
- Setup Gunicorn service (see SERVER_MIGRATION_GUIDE.md)
- Configure Nginx (see SERVER_MIGRATION_GUIDE.md)
- Install SSL certificate
- Test application

---

### Manual Process (Step-by-Step)

Follow **SERVER_MIGRATION_GUIDE.md** sections in order:
1. Backup from Old Server
2. Prepare New Server
3. Install System Dependencies
4. Setup PostgreSQL Database
5. Deploy Application Code
6. Configure Application
7. Restore Database
8. Final Configuration & Testing
9. Go Live

Use **QUICK_REFERENCE.md** for command lookups.

---

## 📋 Pre-Migration Checklist

- [ ] Read SERVER_MIGRATION_GUIDE.md
- [ ] Have SSH access to both servers
- [ ] Have sudo/root privileges on new server
- [ ] Note down current database credentials
- [ ] Note down all environment variables
- [ ] Have domain name ready (if using)
- [ ] Plan migration timing (low-traffic period)
- [ ] Backup current data

---

## 🎯 Recommended Approach

**For Beginners:**
1. Read SERVER_MIGRATION_GUIDE.md thoroughly
2. Use automated scripts
3. Refer to QUICK_REFERENCE.md for commands

**For Experienced Users:**
1. Skim SERVER_MIGRATION_GUIDE.md
2. Use QUICK_REFERENCE.md for commands
3. Customize scripts as needed

**For Troubleshooting:**
1. Check Troubleshooting section in SERVER_MIGRATION_GUIDE.md
2. Use debugging commands in QUICK_REFERENCE.md
3. Check service logs

---

## 📂 Directory Structure After Migration

```
/home/username/applications/KinduraAPIs/
├── courses/                    # Django app
├── health_profile/            # Django app
├── medical_app/               # Django project settings
├── medicines/                 # Django app
├── schedules/                 # Django app
├── users/                     # Django app
├── utils/                     # Utility functions
├── livekit_app/              # LiveKit integration
├── env/                       # Virtual environment
├── staticfiles/              # Collected static files
├── logs/                      # Application logs
│   ├── gunicorn-access.log
│   └── gunicorn-error.log
├── media/                     # User uploads (if any)
├── manage.py                  # Django management
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (SECURE)
├── scripts/                   # Migration scripts
│   ├── backup_for_migration.sh
│   └── deploy_to_new_server.sh
└── docs/
    ├── SERVER_MIGRATION_GUIDE.md
    ├── QUICK_REFERENCE.md
    ├── POSTGRES_MIGRATION_GUIDE.md
    └── MIGRATION_README.md (this file)
```

---

## 🔒 Security Notes

**IMPORTANT:** 
- Never commit `.env` file to git
- Generate new `SECRET_KEY` for production
- Use strong database passwords
- Set `DEBUG=False` in production
- Configure firewall properly
- Install SSL certificate
- Keep system updated

---

## ✅ Post-Migration Checklist

- [ ] All services running (PostgreSQL, Gunicorn, Nginx)
- [ ] Database data verified
- [ ] Static files loading correctly
- [ ] API endpoints working
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] DNS pointing to new server
- [ ] Automated backups configured
- [ ] Monitoring setup
- [ ] Old server data backed up (before decommissioning)

---

## 🆘 Getting Help

**Check logs:**
```bash
# Application logs
tail -f ~/applications/KinduraAPIs/logs/gunicorn-error.log

# Nginx logs
sudo tail -f /var/log/nginx/kindura-error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

**Service status:**
```bash
sudo systemctl status postgresql gunicorn nginx
```

**Common issues:** See Troubleshooting section in SERVER_MIGRATION_GUIDE.md

---

## 📞 Quick Commands

```bash
# Restart all services
sudo systemctl restart postgresql gunicorn nginx

# Check all services
sudo systemctl status postgresql gunicorn nginx

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create backup
pg_dump -U kindura_user kindura_db > backup_$(date +%Y%m%d).sql
```

---

## 🎓 Learning Resources

- **Django Deployment:** https://docs.djangoproject.com/en/stable/howto/deployment/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Nginx Docs:** https://nginx.org/en/docs/
- **Gunicorn Docs:** https://docs.gunicorn.org/

---

## 📝 Notes

- All scripts are tested on Ubuntu 22.04 LTS
- PostgreSQL version 14+ recommended
- Python 3.10 required
- Nginx and Gunicorn for production
- Automated backups recommended

---

**Ready to migrate?** Start with **SERVER_MIGRATION_GUIDE.md**!

Good luck! 🚀
