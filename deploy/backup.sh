#!/usr/bin/env bash
# ==============================================================================
# SmokerKhata - Encrypted Database Backup Script
# Performs daily pg_dump, encrypts with GPG symmetric encryption, and manages
# local retention and optional cloud upload (S3 / Backblaze B2).
# ==============================================================================

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/smokerkhata}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/smokerkhata_${TIMESTAMP}.sql.gz"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"
RETENTION_DAYS=30

mkdir -p "${BACKUP_DIR}"

if [[ -z "${BACKUP_ENCRYPTION_KEY:-}" ]]; then
    echo "ERROR: BACKUP_ENCRYPTION_KEY environment variable is not set." >&2
    exit 1
fi

echo "[$(date)] Starting pg_dump backup..."
pg_dump --clean --if-exists --no-owner --no-privileges "${DATABASE_URL}" | gzip > "${BACKUP_FILE}"

echo "[$(date)] Encrypting backup with GPG symmetric cipher..."
gpg --batch --yes --symmetric --cipher-algo AES256 --passphrase "${BACKUP_ENCRYPTION_KEY}" -o "${ENCRYPTED_FILE}" "${BACKUP_FILE}"

# Remove unencrypted plain archive
rm -f "${BACKUP_FILE}"

echo "[$(date)] Encrypted backup created: ${ENCRYPTED_FILE}"

# Upload to S3 / Backblaze B2 if bucket configured
if [[ -n "${BACKUP_S3_BUCKET:-}" ]]; then
    echo "[$(date)] Uploading to S3 bucket ${BACKUP_S3_BUCKET}..."
    aws s3 cp "${ENCRYPTED_FILE}" "s3://${BACKUP_S3_BUCKET}/backups/$(basename "${ENCRYPTED_FILE}")"
fi

# Retention management: purge local backups older than 30 days
echo "[$(date)] Cleaning up local backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -name "smokerkhata_*.sql.gz.gpg" -type f -mtime +"${RETENTION_DAYS}" -delete

echo "[$(date)] Backup process completed successfully."
