# IntegrationOps Platform Architecture

## Overview
IntegrationOps is a distributed data synchronization platform designed to ingest, transform, and publish operational data across heterogeneous enterprise systems.

## Core System Components

### 1. IngestEngine
The `IngestEngine` component is responsible for authenticating with source systems (such as Salesforce, ServiceNow, and GitHub) and pulling raw payload data via REST, GraphQL, or Webhooks.

### 2. TransformPipeline
The `TransformPipeline` normalizes incoming raw JSON records into canonical domain schemas. It enforces data type casting, string truncation rules, and field renaming.

### 3. Publisher
The `Publisher` validates transformed payloads against target destination table definitions (such as PostgreSQL or BigQuery) and executes bulk upsert operations.

### 4. JobRunner & State Store
The `JobRunner` orchestrates pipeline execution lifecycle, updates job status (`RUNNING`, `SUCCESS`, `FAILED`), and records audit metrics in the state store.
