# Error Handling and Recovery Guide

## Error Classification

### 1. Transient Connection Errors (`EX_NETWORK_TIMEOUT`)
- **Cause**: Temporary network blip or API rate limiting (HTTP 429 / 503).
- **Remediation**: Automatic exponential backoff retry (up to 3 retries over 15 minutes).

### 2. Authentication Failures (`EX_AUTH_EXPIRED`)
- **Cause**: OAuth refresh token revoked or expired (HTTP 401).
- **Remediation**: Requires updating stored integration credentials via admin portal.

### 3. Schema Validation Failures (`EX_SCHEMA_VALIDATION_ERROR`)
- **Cause**: Column length overflow or datatype mismatch between source payload and destination table (e.g., `customer_email` exceeding VARCHAR length).
- **Remediation**:
  1. Inspect error log for affected job ID.
  2. Alter destination PostgreSQL column size (`ALTER TABLE salesforce_contacts ALTER COLUMN customer_email TYPE VARCHAR(255);`).
  3. Trigger manual re-run of failed job.
