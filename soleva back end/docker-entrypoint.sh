#!/bin/bash
set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting Soleva backend container..."

# Wait for database to be ready
log "Waiting for database..."
max_attempts=30
attempt=1
while ! nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432} 2>/dev/null; do
    if [ $attempt -ge $max_attempts ]; then
        log "ERROR: Database not ready after $max_attempts attempts"
        exit 1
    fi
    log "Database not ready, attempt $attempt/$max_attempts..."
    sleep 2
    ((attempt++))
done
log "Database is ready!"

# Wait for Redis to be ready
log "Waiting for Redis..."
max_attempts=30
attempt=1
while ! nc -z redis 6379 2>/dev/null; do
    if [ $attempt -ge $max_attempts ]; then
        log "ERROR: Redis not ready after $max_attempts attempts"
        exit 1
    fi
    log "Redis not ready, attempt $attempt/$max_attempts..."
    sleep 2
    ((attempt++))
done
log "Redis is ready!"

# Run database migrations with better error handling
log "Running database migrations..."
if python manage.py makemigrations --noinput; then
    log "Makemigrations completed successfully"
else
    log "WARNING: Makemigrations failed, continuing..."
fi

# Try migrations with fallback
if python manage.py migrate --noinput; then
    log "Database migrations completed successfully"
else
    log "ERROR: Database migrations failed"
    # Try a simpler migration approach
    log "Attempting alternative migration approach..."

    # Run migrations in specific order to avoid dependency issues
    python manage.py migrate auth --noinput || log "Failed to migrate auth"
    python manage.py migrate contenttypes --noinput || log "Failed to migrate contenttypes"
    python manage.py migrate sessions --noinput || log "Failed to migrate sessions"
    python manage.py migrate users --noinput || log "Failed to migrate users"
    python manage.py migrate admin --noinput || log "Failed to migrate admin"

    # Continue with other migrations
    for app in shipping otp products offers cart coupons notifications accounting payments tracking website_management orders; do
        python manage.py migrate $app --noinput || log "Failed to migrate $app"
    done
fi

# Collect static files
log "Collecting static files..."
if python manage.py collectstatic --noinput --clear; then
    log "Static files collected successfully"
else
    log "WARNING: Static files collection failed"
fi

# Create superuser if it doesn't exist (with error handling)
log "Creating superuser if it doesn't exist..."
python manage.py shell << EOF 2>/dev/null || log "Superuser creation check failed"
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(email='admin@solevaeg.com').exists():
        User.objects.create_superuser(
            email='admin@solevaeg.com',
            password='${ADMIN_PASSWORD}',
            first_name='Admin',
            last_name='User'
        )
        print('Superuser created successfully')
    else:
        print('Superuser already exists')
except Exception as e:
    print(f'Error checking/creating superuser: {e}')
EOF

# Create logs directory if it doesn't exist
mkdir -p /app/logs

# Start the server with better error handling
log "Starting Django server with Gunicorn..."

# Enable reload only when DEBUG is true
GUNICORN_ARGS=(
    --bind 0.0.0.0:8000
    --workers ${GUNICORN_WORKERS:-4}
    --worker-class gevent
    --worker-connections 1000
    --max-requests 1000
    --max-requests-jitter 100
    --timeout 30
    --keep-alive 2
    --access-logfile /app/logs/gunicorn-access.log
    --error-logfile /app/logs/gunicorn-error.log
    --log-level ${LOG_LEVEL:-info}
)

if [ "${DEBUG}" = "True" ] || [ "${DEBUG}" = "true" ] || [ "${DEBUG}" = "1" ]; then
    GUNICORN_ARGS+=( --reload )
fi

exec gunicorn "${GUNICORN_ARGS[@]}" soleva_backend.wsgi:application
