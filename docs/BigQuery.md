# Big Query Developer Guide

## Clean up BigQuery Tables

To keep the schema but only delete the data, you can use the `TRUNCATE TABLE` statement. This will remove all rows from the specified table while keeping the structure intact.

```SQL
TRUNCATE TABLE `openactive-monitor.openactive_analytics.opportunities`;
```

```SQL
TRUNCATE TABLE `openactive-monitor.openactive_analytics.opportunity_ingestion`;
```
