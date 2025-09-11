# SSL Certificate Renewal Script for Soleva (PowerShell)
# This script renews SSL certificates using Let's Encrypt Certbot

Write-Host "Checking for SSL certificate renewals..." -ForegroundColor Green

# Run certbot renewal
$certbotCommand = @"
docker run --rm -v "${PWD}/certbot/conf:/etc/letsencrypt" -v "${PWD}/certbot/www:/var/www/certbot" certbot/certbot renew --webroot --webroot-path=/var/www/certbot
"@

Invoke-Expression $certbotCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "Reloading nginx configuration..." -ForegroundColor Yellow
    docker exec soleva_nginx nginx -s reload

    if ($LASTEXITCODE -eq 0) {
        Write-Host "SSL certificate renewal completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Failed to reload nginx" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "SSL certificate renewal failed" -ForegroundColor Red
    exit 1
}
