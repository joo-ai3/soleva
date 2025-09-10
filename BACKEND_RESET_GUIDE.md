# 🔄 Backend Reset & Migration Fix Guide

## 🚨 Problem Description

Your backend container is experiencing:
- Continuous restarts
- Migration failures: `"relation 'users' does not exist"`
- Database connection issues
- Orphan container conflicts

## 🛠️ Complete Solution

### **Option 1: Automated Fix (Recommended)**

**For Windows (PowerShell):**
```powershell
# Dry run first to see what will happen
.\backend-reset-fix.ps1 -DryRun

# If you're sure, run the actual fix
.\backend-reset-fix.ps1
```

**For Linux/macOS (Bash):**
```bash
# Dry run first to see what will happen
./backend-reset-fix.sh --dry-run

# If you're sure, run the actual fix
./backend-reset-fix.sh
```

### **Option 2: Manual Step-by-Step Fix**

If you prefer manual control, follow these steps:

## 📋 Manual Steps

### Step 1: Stop All Services
```bash
docker compose down --remove-orphans
```

### Step 2: Remove Migration Files
```bash
# Remove all migration files (keep __init__.py)
find "soleva back end" -path "*/migrations/*.py" -not -name "__init__.py" -delete

# Verify cleanup
find "soleva back end" -path "*/migrations/*.py" -not -name "__init__.py"
```

### Step 3: Reset Database
```bash
# Start PostgreSQL
docker compose up -d postgres

# Wait for it to be ready (check with: docker compose logs postgres)

# Reset the database
docker compose exec postgres psql -U soleva_user -d soleva_db << 'EOF'
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO soleva_user;
GRANT ALL ON SCHEMA public TO public;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO soleva_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO soleva_user;
EOF
```

### Step 4: Start Backend
```bash
# Start Redis first
docker compose up -d redis

# Start backend
docker compose up -d backend

# Check logs
docker compose logs backend
```

### Step 5: Recreate Migrations
```bash
# Create new migrations
docker compose exec backend python manage.py makemigrations

# Apply migrations
docker compose exec backend python manage.py migrate
```

### Step 6: Create Superuser
```bash
# Create superuser
docker compose exec backend python manage.py createsuperuser
```

## 🔍 Verification Steps

### Check Container Status
```bash
docker compose ps
```
Should show all containers as "healthy" or "running"

### Test Backend Health
```bash
curl http://localhost:8000/api/health/
```
Should return a successful response

### Check Database Tables
```bash
docker compose exec backend python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT tablename FROM pg_tables WHERE schemaname=\"public\";')
tables = cursor.fetchall()
print(f'Found {len(tables)} tables:')
for table in tables[:5]:
    print(f'  - {table[0]}')
"
```

### View Logs
```bash
# Real-time logs
docker compose logs -f backend

# Recent logs
docker compose logs --tail=50 backend
```

## 📊 What the Fix Does

### ✅ Migration Cleanup
- Removes all existing migration files from all Django apps
- Keeps `__init__.py` files intact
- Prevents migration conflicts

### ✅ Database Reset
- Drops the entire `public` schema
- Recreates it with proper permissions
- Grants necessary privileges to the database user

### ✅ Fresh Start
- Recreates all migrations from scratch
- Applies them in correct order
- Creates superuser account

### ✅ Health Verification
- Tests backend API connectivity
- Verifies database connections
- Confirms all services are running

## ⚠️ Important Warnings

### Data Loss Warning
**❌ This will DELETE ALL existing data in your database!**
- User accounts
- Product data
- Orders and transactions
- All application data

### Backup First (If Needed)
If you need to preserve data:
```bash
# Create backup before running the script
docker compose exec postgres pg_dump -U soleva_user soleva_db > backup.sql

# Later, you can restore with:
# docker compose exec -T postgres psql -U soleva_user -d soleva_db < backup.sql
```

### Service Dependencies
The backend requires:
- ✅ PostgreSQL running and healthy
- ✅ Redis running and accessible
- ✅ Proper environment variables in `docker.env`

## 🎯 Expected Results

After running the fix, you should see:

```
✅ PostgreSQL is ready!
✅ Redis is ready!
✅ Backend container started!
✅ Makemigrations completed successfully
✅ Migrations applied successfully
✅ Superuser setup completed!
✅ Backend API is responding
```

## 🚨 Troubleshooting

### If Backend Still Fails
```bash
# Check detailed logs
docker compose logs backend

# Test database connection manually
docker compose exec backend python manage.py dbshell --command "SELECT 1;"

# Check Redis connection
docker compose exec redis redis-cli -a "Redis@2025" ping
```

### If Migrations Still Fail
```bash
# Force recreate specific app migrations
docker compose exec backend python manage.py makemigrations users
docker compose exec backend python manage.py migrate users

# Check migration status
docker compose exec backend python manage.py showmigrations
```

### If Health Check Fails
```bash
# Check what the health endpoint returns
curl -v http://localhost:8000/api/health/

# Test basic Django functionality
docker compose exec backend python manage.py check
```

## 📞 Support Information

### Access Credentials (After Fix)
- **Admin URL:** http://localhost/admin/
- **API Base:** http://localhost:8000/api/
- **Superuser Email:** admin@thesoleva.com
- **Superuser Password:** S0l3v@_Admin!2025#

### Useful Commands
```bash
# Monitor services
docker compose ps
docker compose logs -f

# Restart services
docker compose restart backend
docker compose restart postgres redis

# Clean restart
docker compose down
docker compose up -d
```

### Apps Reset by This Script
The script handles migrations for these Django apps:
- `users` (most critical - fixes "relation users does not exist")
- `products`, `cart`, `orders`, `coupons`
- `notifications`, `shipping`, `payments`
- `tracking`, `offers`, `accounting`
- `otp`, `website_management`

## 🎉 Success Indicators

Your backend is fixed when:
- ✅ `docker compose ps` shows all services as "healthy"
- ✅ Backend logs show successful startup without errors
- ✅ API endpoints respond successfully
- ✅ Admin panel is accessible
- ✅ No more "relation users does not exist" errors

**🎯 Run the automated script now to fix all your backend issues!**

---

*Note: The automated script includes safety confirmations and detailed logging. Always review what it will do in dry-run mode first.*
