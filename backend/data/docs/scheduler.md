# Integration Scheduler Specification

## Overview
The Integration Scheduler triggers data synchronization jobs based on cron schedules or real-time event webhooks.

## Schedule Types

### 1. Cron-based Polling
Batch synchronization jobs run on defined cron schedules (e.g., `0 */2 * * *` for bi-hourly syncs). The Scheduler evaluates active cron expressions every 60 seconds.

### 2. Event-Driven Webhooks
Real-time integrations (such as Stripe payments) bypass the polling scheduler and trigger immediate `JobRunner` execution upon receiving verified webhook payloads.

## Concurrent Execution Rules
- A single integration pipeline cannot run more than 1 concurrent job instance.
- If a scheduled job triggers while a previous job is still `RUNNING`, the new run is marked as `SKIPPED`.
