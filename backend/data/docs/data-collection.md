# Data Collection Component (IngestEngine)

## Overview
The `IngestEngine` connects to external SaaS APIs and internal relational databases to extract updated records since the last successful sync timestamp.

## Authentication & API Connection
- **Salesforce CRM**: Uses OAuth 2.0 Client Credentials flow. API rate limits are enforced at 100,000 requests per day.
- **ServiceNow ITSM**: Uses basic HTTP auth / OAuth refresh tokens to retrieve incident logs.
- **GitHub Enterprise**: Uses Personal Access Tokens (PAT) to read audit logs.

## Checkpoint Management
The `IngestEngine` maintains high-watermark timestamps in the state store (`last_sync_timestamp`). Extraction queries request records where `updated_at > last_sync_timestamp`.
