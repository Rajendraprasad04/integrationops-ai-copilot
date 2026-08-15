# Publishing Component Specification

## Overview
The `Publisher` component writes transformed data batches into destination datastores (e.g., PostgreSQL, BigQuery, Kafka).

## Pre-Publish Schema Validation
Before executing SQL bulk upserts, the `Publisher` queries the destination table metadata to verify column existence, data types, and length constraints.

### Schema Mismatch Errors
If a record contains a value exceeding target column specifications (for example, a string length of 82 in a `VARCHAR(50)` column like `customer_email`), validation fails:
- Error Code: `EX_SCHEMA_VALIDATION_ERROR`
- Error Message: `Destination validation failed: target table schema mismatch on column 'customer_email'`
- The job status transitions to `FAILED` and rejected records are routed to the error log.

## Bulk Upsert Execution
For PostgreSQL destinations, `Publisher` uses `INSERT INTO target_table ON CONFLICT (id) DO UPDATE` with batch sizes of 500 records per transaction.
