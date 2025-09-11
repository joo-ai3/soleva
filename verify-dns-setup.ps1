# DNS Verification Script for solevaeg.com
# This script verifies that DNS A records are properly configured

Write-Host "🔍 Verifying DNS Setup for solevaeg.com" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Function to resolve DNS
function Test-DNSResolution {
    param([string]$Domain)

    try {
        $result = Resolve-DnsName -Name $Domain -Type A -ErrorAction Stop
        $ip = $result.IPAddress
        Write-Host "✅ $Domain resolves to: $ip" -ForegroundColor Green
        return $ip
    } catch {
        Write-Host "❌ $Domain does not resolve or DNS not propagated yet" -ForegroundColor Red
        return $null
    }
}

# Test both domains
$domain1 = "solevaeg.com"
$domain2 = "www.solevaeg.com"

$ip1 = Test-DNSResolution $domain1
$ip2 = Test-DNSResolution $domain2

# Check if both domains resolve to the same IP
if ($ip1 -and $ip2) {
    if ($ip1 -eq $ip2) {
        Write-Host "✅ Both domains resolve to the same IP address" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Domains resolve to different IP addresses" -ForegroundColor Yellow
        Write-Host "   solevaeg.com: $ip1" -ForegroundColor Yellow
        Write-Host "   www.solevaeg.com: $ip2" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📋 DNS Setup Checklist:" -ForegroundColor Cyan
Write-Host "1. Ensure A records for solevaeg.com and www.solevaeg.com point to your server IP" -ForegroundColor Cyan
Write-Host "2. DNS propagation can take up to 48 hours" -ForegroundColor Cyan
Write-Host "3. Use tools like dnschecker.org to verify global propagation" -ForegroundColor Cyan

Write-Host ""
Write-Host "🔗 Useful Commands:" -ForegroundColor Cyan
Write-Host "- Check DNS: Resolve-DnsName -Name solevaeg.com -Type A" -ForegroundColor Cyan
Write-Host "- Flush DNS cache: Clear-DnsClientCache" -ForegroundColor Cyan
