# Soleva Website - Recovery Instructions

## Backup Information
- **Created**: 2025-09-12 18:50:16
- **Backup Path**: .\backups\pre-deployment-2025-09-12-18-48-43
- **Project Version**: 1.0.0

## Recovery Steps

### 1. Project Files Recovery
To restore project files:
```
# Copy project files back to deployment directory
cp -r project-files/* /var/www/soleva/
```

### 2. Database Recovery
To restore database:
```
# Stop services
docker-compose down

# Start only database
docker-compose up -d postgres

# Restore database
gunzip -c database-backup.sql.gz | docker-compose exec -T postgres psql -U soleva_user -d soleva_db

# Start all services
docker-compose up -d
```

### 3. Configuration Recovery
To restore configurations:
```
# Copy configuration files
cp configurations/docker.env ../docker.env
cp configurations/soleva.conf ../nginx/conf.d/soleva.conf
# ... restore other configs as needed
```

### 4. SSL Certificates
SSL certificates will be regenerated automatically by certbot.
If needed, run:
```
docker-compose run --rm certbot
```

## Verification
After recovery, verify:
1. Website loads: https://solevaeg.com
2. Admin panel works: https://solevaeg.com/admin/
3. Database connectivity
4. All services running: docker-compose ps

## Contact
For support, contact the development team.
