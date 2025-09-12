#!/bin/bash

# Soleva Platform Security Audit Script
# This script performs comprehensive security checks

set -e

echo "🔒 Starting Soleva Platform Security Audit..."
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ISSUES_FOUND=0
WARNINGS_FOUND=0
CHECKS_PASSED=0

# Helper functions
log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((ISSUES_FOUND++))
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((WARNINGS_FOUND++))
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((CHECKS_PASSED++))
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root - ensure this is intentional for production deployment"
    else
        log_success "Not running as root"
    fi
}

# Check file permissions
check_file_permissions() {
    log_info "Checking file permissions..."
    
    # Check for sensitive files
    SENSITIVE_FILES=(
        ".env"
        "docker.env"
        "soleva back end/.env"
        "soleva front end/.env"
    )
    
    for file in "${SENSITIVE_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            PERMS=$(stat -c "%a" "$file")
            if [[ "$PERMS" != "600" ]] && [[ "$PERMS" != "640" ]]; then
                log_warning "File $file has permissions $PERMS (recommended: 600 or 640)"
            else
                log_success "File $file has secure permissions ($PERMS)"
            fi
        fi
    done
    
    # Check for world-writable files
    WORLD_WRITABLE=$(find . -type f -perm -002 2>/dev/null | grep -v ".git" | head -10)
    if [[ -n "$WORLD_WRITABLE" ]]; then
        log_warning "Found world-writable files:"
        echo "$WORLD_WRITABLE"
    else
        log_success "No world-writable files found"
    fi
}

# Check environment variables
check_environment_variables() {
    log_info "Checking environment variables..."
    
    # Critical environment variables that should be set
    REQUIRED_VARS=(
        "SECRET_KEY"
        "DATABASE_URL"
        "ALLOWED_HOSTS"
    )
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [[ -z "${!var}" ]]; then
            log_error "Environment variable $var is not set"
        else
            log_success "Environment variable $var is set"
        fi
    done
    
    # Check for default/weak values
    if [[ "$SECRET_KEY" == *"django-insecure"* ]]; then
        log_error "SECRET_KEY appears to be using default Django value"
    fi
    
    if [[ "$DEBUG" == "True" ]] || [[ "$DEBUG" == "true" ]]; then
        log_warning "DEBUG is enabled - ensure this is not production"
    else
        log_success "DEBUG is disabled"
    fi
}

# Check Docker security
check_docker_security() {
    log_info "Checking Docker security configuration..."
    
    if command -v docker &> /dev/null; then
        # Check if Docker daemon is running
        if docker ps &> /dev/null; then
            log_success "Docker daemon is accessible"
            
            # Check for privileged containers
            PRIVILEGED=$(docker ps --format "table {{.Names}}\t{{.Status}}" --filter "label=privileged=true" | tail -n +2)
            if [[ -n "$PRIVILEGED" ]]; then
                log_warning "Found privileged containers:"
                echo "$PRIVILEGED"
            else
                log_success "No privileged containers running"
            fi
            
            # Check Docker compose file security
            if [[ -f "docker-compose.production.yml" ]]; then
                # Check for hardcoded secrets
                if grep -q "password.*=" docker-compose.production.yml; then
                    log_warning "Potential hardcoded passwords in docker-compose.production.yml"
                else
                    log_success "No hardcoded passwords found in Docker Compose file"
                fi
                
                # Check for privileged mode
                if grep -q "privileged.*true" docker-compose.production.yml; then
                    log_warning "Containers running in privileged mode found"
                else
                    log_success "No privileged containers in Docker Compose"
                fi
            fi
        else
            log_warning "Docker daemon not accessible or not running"
        fi
    else
        log_info "Docker not installed - skipping Docker security checks"
    fi
}

# Check SSL/TLS configuration
check_ssl_configuration() {
    log_info "Checking SSL/TLS configuration..."
    
    # Check Nginx SSL configuration
    if [[ -f "nginx/conf.d/ssl.conf" ]]; then
        # Check for strong SSL ciphers
        if grep -q "ssl_ciphers" nginx/conf.d/ssl.conf; then
            log_success "SSL ciphers are configured"
        else
            log_warning "SSL ciphers not explicitly configured"
        fi
        
        # Check for HSTS
        if grep -q "Strict-Transport-Security" nginx/conf.d/soleva.conf; then
            log_success "HSTS is configured"
        else
            log_error "HSTS is not configured"
        fi
        
        # Check SSL protocols
        if grep -q "ssl_protocols.*TLSv1.3" nginx/conf.d/ssl.conf; then
            log_success "TLS 1.3 is enabled"
        else
            log_warning "TLS 1.3 is not explicitly enabled"
        fi
    else
        log_warning "SSL configuration file not found"
    fi
}

# Check backend security
check_backend_security() {
    log_info "Checking Django backend security..."
    
    cd "soleva back end" || return
    
    # Check for security middleware
    if grep -q "SecurityMiddleware" soleva_backend/settings.py; then
        log_success "Django SecurityMiddleware is enabled"
    else
        log_error "Django SecurityMiddleware is not enabled"
    fi
    
    # Check for CSRF protection
    if grep -q "CsrfViewMiddleware" soleva_backend/settings.py; then
        log_success "CSRF protection is enabled"
    else
        log_error "CSRF protection is not enabled"
    fi
    
    # Check for SQL injection protection
    if command -v bandit &> /dev/null; then
        log_info "Running bandit security scanner..."
        bandit -r . -f json -o ../bandit-report.json 2>/dev/null || true
        
        if [[ -f "../bandit-report.json" ]]; then
            HIGH_ISSUES=$(jq '.results[] | select(.issue_severity == "HIGH")' ../bandit-report.json 2>/dev/null | wc -l)
            MEDIUM_ISSUES=$(jq '.results[] | select(.issue_severity == "MEDIUM")' ../bandit-report.json 2>/dev/null | wc -l)
            
            if [[ "$HIGH_ISSUES" -gt 0 ]]; then
                log_error "Found $HIGH_ISSUES high-severity security issues"
            elif [[ "$MEDIUM_ISSUES" -gt 0 ]]; then
                log_warning "Found $MEDIUM_ISSUES medium-severity security issues"
            else
                log_success "No high or medium security issues found"
            fi
        fi
    else
        log_warning "Bandit not installed - skipping code security scan"
    fi
    
    # Check dependencies for vulnerabilities
    if command -v safety &> /dev/null; then
        log_info "Checking for vulnerable dependencies..."
        if safety check --json --output ../safety-report.json 2>/dev/null; then
            log_success "No vulnerable dependencies found"
        else
            log_warning "Vulnerable dependencies detected - check safety-report.json"
        fi
    else
        log_warning "Safety not installed - skipping dependency vulnerability check"
    fi
    
    cd ..
}

# Check frontend security
check_frontend_security() {
    log_info "Checking frontend security..."
    
    cd "soleva front end" || return
    
    # Check for audit
    if command -v npm &> /dev/null; then
        log_info "Running npm audit..."
        if npm audit --audit-level moderate &> /dev/null; then
            log_success "No moderate or high npm vulnerabilities found"
        else
            log_warning "npm vulnerabilities detected - run 'npm audit' for details"
        fi
    fi
    
    # Check for sensitive data in environment
    if [[ -f ".env" ]]; then
        if grep -i "secret\|key\|password\|token" .env | grep -v "VITE_" | grep -q "="; then
            log_warning "Potential sensitive data in frontend .env file"
        else
            log_success "No sensitive data found in frontend .env"
        fi
    fi
    
    # Check build output for sensitive data
    if [[ -d "dist" ]]; then
        if grep -r "sk_live\|pk_live\|password\|secret" dist/ &> /dev/null; then
            log_error "Potential sensitive data found in build output"
        else
            log_success "No sensitive data found in build output"
        fi
    fi
    
    cd ..
}

# Check network security
check_network_security() {
    log_info "Checking network security configuration..."
    
    # Check for exposed ports
    if command -v netstat &> /dev/null; then
        EXPOSED_PORTS=$(netstat -tuln | grep "0.0.0.0" | grep -v ":80\|:443\|:22" | wc -l)
        if [[ "$EXPOSED_PORTS" -gt 0 ]]; then
            log_warning "Found $EXPOSED_PORTS potentially unnecessary exposed ports"
            netstat -tuln | grep "0.0.0.0" | grep -v ":80\|:443\|:22"
        else
            log_success "Only standard ports (80, 443, 22) are exposed"
        fi
    fi
    
    # Check firewall status
    if command -v ufw &> /dev/null; then
        if ufw status | grep -q "Status: active"; then
            log_success "UFW firewall is active"
        else
            log_warning "UFW firewall is not active"
        fi
    elif command -v iptables &> /dev/null; then
        if iptables -L | grep -q "Chain INPUT"; then
            log_success "iptables firewall rules are configured"
        else
            log_warning "No iptables rules found"
        fi
    else
        log_warning "No firewall detected"
    fi
}

# Check backup and monitoring
check_backup_monitoring() {
    log_info "Checking backup and monitoring setup..."
    
    # Check for backup scripts
    if [[ -f "scripts/backup.sh" ]]; then
        log_success "Backup script found"
        
        # Check if it's executable
        if [[ -x "scripts/backup.sh" ]]; then
            log_success "Backup script is executable"
        else
            log_warning "Backup script is not executable"
        fi
    else
        log_warning "No backup script found"
    fi
    
    # Check for monitoring configuration
    if grep -q "sentry" "soleva back end/soleva_backend/settings.py" 2>/dev/null; then
        log_success "Error monitoring (Sentry) is configured"
    else
        log_warning "No error monitoring detected"
    fi
    
    # Check for log rotation
    if [[ -f "/etc/logrotate.d/nginx" ]] || [[ -f "/etc/logrotate.d/soleva" ]]; then
        log_success "Log rotation is configured"
    else
        log_warning "Log rotation not configured"
    fi
}

# Main execution
main() {
    echo "Starting security audit at $(date)"
    echo
    
    check_root
    check_file_permissions
    check_environment_variables
    check_docker_security
    check_ssl_configuration
    check_backend_security
    check_frontend_security
    check_network_security
    check_backup_monitoring
    
    echo
    echo "=============================================="
    echo "🔒 Security Audit Complete"
    echo "=============================================="
    echo -e "${GREEN}Checks passed: $CHECKS_PASSED${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS_FOUND${NC}"
    echo -e "${RED}Issues found: $ISSUES_FOUND${NC}"
    echo
    
    if [[ $ISSUES_FOUND -gt 0 ]]; then
        echo -e "${RED}❌ Security audit failed - please address the issues above${NC}"
        exit 1
    elif [[ $WARNINGS_FOUND -gt 0 ]]; then
        echo -e "${YELLOW}⚠️  Security audit passed with warnings - consider addressing them${NC}"
        exit 0
    else
        echo -e "${GREEN}✅ Security audit passed - no issues found${NC}"
        exit 0
    fi
}

# Install dependencies if needed
install_dependencies() {
    if [[ "$1" == "--install-deps" ]]; then
        echo "Installing security audit dependencies..."
        
        # Install Python security tools
        pip install bandit safety 2>/dev/null || echo "Failed to install Python security tools"
        
        # Install jq for JSON parsing
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y jq
        elif command -v yum &> /dev/null; then
            sudo yum install -y jq
        elif command -v brew &> /dev/null; then
            brew install jq
        fi
    fi
}

# Parse arguments
if [[ "$1" == "--install-deps" ]]; then
    install_dependencies "$1"
    shift
fi

main "$@"
