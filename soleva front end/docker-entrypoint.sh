#!/bin/sh
set -e

# Replace environment variables in built files
echo "Configuring environment variables..."

# Replace API_BASE_URL in built JS files if needed
if [ -n "$VITE_API_BASE_URL" ]; then
    find /usr/share/nginx/html -name "*.js" -type f -exec sed -i "s|__API_BASE_URL__|$VITE_API_BASE_URL|g" {} \;
fi

echo "Starting Nginx..."
exec nginx -g 'daemon off;'
