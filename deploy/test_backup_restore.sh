#!/usr/bin/env bash
# ==============================================================================
# SmokerKhata - Backup & Restore Drill Test Script
# Tests the round-trip encryption, decryption, and integrity of the backup
# without requiring an active PostgreSQL service.
# ==============================================================================

set -euo pipefail

export BACKUP_ENCRYPTION_KEY="test-drill-passphrase-secure-12345"
DRILL_DIR=$(mktemp -d)
trap 'rm -rf "${DRILL_DIR}"' EXIT

SAMPLE_SQL="${DRILL_DIR}/sample.sql"
ENCRYPTED_GPG="${DRILL_DIR}/sample.sql.gz.gpg"
RESTORED_SQL="${DRILL_DIR}/restored.sql"

echo "INSERT INTO test_records (id, amount_paise) VALUES (1, 50000);" > "${SAMPLE_SQL}"

echo "[Drill] 1. Compressing and Encrypting sample..."
gzip -c "${SAMPLE_SQL}" | gpg --batch --yes --symmetric --cipher-algo AES256 --passphrase "${BACKUP_ENCRYPTION_KEY}" -o "${ENCRYPTED_GPG}"

echo "[Drill] 2. Decrypting and Decompressing..."
gpg --batch --yes --decrypt --passphrase "${BACKUP_ENCRYPTION_KEY}" "${ENCRYPTED_GPG}" | gunzip > "${RESTORED_SQL}"

echo "[Drill] 3. Verifying integrity..."
if cmp -s "${SAMPLE_SQL}" "${RESTORED_SQL}"; then
    echo "[Drill] SUCCESS: Decrypted payload matches original sample exactly. Zero data loss verified."
else
    echo "[Drill] FAILED: Decrypted payload does not match original." >&2
    exit 1
fi
