# PostgreSQL Migration Guide

## Current Status ✅
- ✅ SQLite data exported to `data_backup.json`
- ✅ psycopg2-binary installed
- ✅ Django settings updated to support PostgreSQL

## Next Steps

### 1. Install PostgreSQL (if not already installed)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, run:
CREATE DATABASE kindura_db;
CREATE USER kindura_user WITH PASSWORD 'your_secure_password';
ALTER ROLE kindura_user SET client_encoding TO 'utf8';
ALTER ROLE kindura_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE kindura_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE kindura_db TO kindura_user;
\q
```

### 3. Update Your .env File

Add these lines to `/home/KinduraAPIs/.env`:

```env
# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=kindura_db
DB_USER=kindura_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

**IMPORTANT:** Replace `your_secure_password` with a strong password!

### 4. Run Migrations to PostgreSQL

```bash
cd /home/KinduraAPIs
source env/bin/activate
python manage.py migrate
```

### 5. Load Your Data

```bash
python manage.py loaddata data_backup.json
```

### 6. Verify the Migration

```bash
# Check if data loaded correctly
python manage.py shell

# In Django shell:
from users.models import User
from courses.models import *
from medicines.models import *
from schedules.models import *

# Check counts
print(f"Users: {User.objects.count()}")
print(f"Courses: {Course.objects.count() if 'Course' in dir() else 'N/A'}")
# Add more checks as needed
```

### 7. Test Your Application

```bash
python manage.py runserver
```

## Rollback Plan (if needed)

If something goes wrong, you can easily rollback:

1. Comment out or remove PostgreSQL env vars from `.env`
2. The app will automatically fallback to SQLite
3. Your original `db.sqlite3` is untouched

## Production Considerations

- Use environment variables for all sensitive data (already configured)
- Consider using connection pooling (pgbouncer)
- Set up regular backups using `pg_dump`
- Update your deployment scripts to include PostgreSQL setup
- Consider using managed PostgreSQL (AWS RDS, Digital Ocean, etc.)

## Backup Command (for future use)

```bash
# PostgreSQL backup
pg_dump -U kindura_user -h localhost kindura_db > backup_$(date +%Y%m%d).sql

# Django backup
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 -o backup_$(date +%Y%m%d).json
```
