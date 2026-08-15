# Normalization Component (TransformPipeline)

## Overview
The `TransformPipeline` translates raw JSON structures into standardized internal schemas before publishing to destination databases.

## Mapping & Type Coercion
- **Timestamps**: All date strings are converted to UTC ISO-8601 format (`YYYY-MM-DDTHH:MM:SSZ`).
- **Null Safety**: Missing optional fields are defaulted to explicit null values.
- **String Field Truncation**: Standard text fields are checked against maximum target column lengths.

## Common Transformation Rules
For Salesforce contact syncs:
- `FirstName` and `LastName` are merged into `full_name`.
- `Email` is mapped to `customer_email`.
- Source strings exceeding target column definitions trigger validation flags.
