# Generate Self-Signed SSL Certificate for Testing
# This creates a fallback certificate when Let's Encrypt certs are not available

Write-Host "🔐 Generating Self-Signed SSL Certificate..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

$certDir = "ssl/selfsigned"
$certPath = "$certDir/solevaeg.com.crt"
$keyPath = "$certDir/solevaeg.com.key"

# Create directory if it doesn't exist
if (!(Test-Path $certDir)) {
    New-Item -ItemType Directory -Path $certDir -Force | Out-Null
}

# Check if certificates already exist
if ((Test-Path $certPath) -and (Test-Path $keyPath)) {
    Write-Host "✅ Self-signed certificates already exist" -ForegroundColor Green
    Write-Host "   Certificate: $certPath" -ForegroundColor Green
    Write-Host "   Private Key: $keyPath" -ForegroundColor Green
    exit 0
}

Write-Host "Generating new self-signed certificate..." -ForegroundColor Yellow

# Create OpenSSL configuration for the certificate
$opensslConf = @"
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = EG
ST = Cairo
L = Cairo
O = Soleva
OU = IT
CN = solevaeg.com

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = solevaeg.com
DNS.2 = www.solevaeg.com
DNS.3 = localhost
"@

$opensslConf | Out-File -FilePath "$certDir/openssl.conf" -Encoding ASCII

# Generate private key
Write-Host "Generating private key..." -ForegroundColor Yellow
openssl genrsa -out $keyPath 2048

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to generate private key" -ForegroundColor Red
    exit 1
}

# Generate certificate
Write-Host "Generating certificate..." -ForegroundColor Yellow
openssl req -new -x509 -key $keyPath -out $certPath -days 365 -config "$certDir/openssl.conf" -extensions v3_req

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to generate certificate" -ForegroundColor Red
    exit 1
}

# Verify certificate
Write-Host "Verifying certificate..." -ForegroundColor Yellow
openssl x509 -in $certPath -text -noout | Select-String -Pattern "Subject:|DNS:" | ForEach-Object {
    Write-Host "   $($_.Line.Trim())" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Self-signed certificate generated successfully!" -ForegroundColor Green
Write-Host "   Certificate: $certPath" -ForegroundColor Green
Write-Host "   Private Key: $keyPath" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️ Note: This is a self-signed certificate for testing only." -ForegroundColor Yellow
Write-Host "   Replace with Let's Encrypt certificates in production." -ForegroundColor Yellow
