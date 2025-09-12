#!/bin/bash
# Backup Verification Script

echo "Verifying Soleva backup..."

# Check backup directory
if [ ! -d ".\backups\pre-deployment-2025-09-12-18-48-43" ]; then
    echo "ERROR: Backup directory not found!"
    exit 1
fi

# Check essential files
essential_files=(
    "backup-manifest.json"
    "RECOVERY_INSTRUCTIONS.md"
    "backup-database.sh"
    "docker.env.backup"
    "project-files/docker-compose.yml"
    "project-files/docker.env"
)

for file in "${essential_files[@]}"; do
    if [ ! -f ".\backups\pre-deployment-2025-09-12-18-48-43/$file" ]; then
        echo "ERROR: Missing essential file: $file"
        exit 1
    fi
done

echo "Backup verification completed successfully!"
echo "Backup location: .\backups\pre-deployment-2025-09-12-18-48-43"
echo "All essential files are present."
