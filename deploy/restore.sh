#!/usr/bin/env bash
# ==============================================================================
# SmokerKhata - Encrypted Database Restore Script
# Restores an encrypted .sql.gz.gpg backup into a target / staging database.
# Usage: ./restore.sh <path_to_encrypted_file> [target_database_url]
# ==============================================================================

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <path_to_encrypted_backup.gpg> [target_db_url]" >&2
    exit 1
fi

ENCRYPTED_FILE="$1"
RESTORE_DB_URL="${2:-${DATABASE_URL:-}}"

if [[ -z "${RESTORE_DB_URL}" ]]; then
    echo "ERROR: Target database URL not provided and DATABASE_URL is not set." >&2
    exit 1
fi

if [[ -z "${BACKUP_ENCRYPTION_KEY:-}" ]]; then
    echo "ERROR: BACKUP_ENCRYPTION_KEY environment variable is not set." >&2
    exit 1
fi

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "${TEMP_DIR}"' EXIT

DECRYPTED_SQL="${TEMP_DIR}/restore.sql"

echo "[$(date)] Decrypting ${ENCRYPTED_FILE}..."
gpg --batch --yes --decrypt --passphrase "${BACKUP_ENCRYPTION_KEY}" "${ENCRYPTED_FILE}" | gunzip > "${DECRYPTED_SQL}"

echo "[$(date)] Restoring to database ${RESTORE_DB_URL}..."
psql "${RESTORE_DB_URL}" < "${DECRYPTED_SQL}"

echo "[$(date)] Database restoration completed successfully."
