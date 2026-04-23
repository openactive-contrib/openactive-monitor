# Big Query Developer Guide

## Clean up BigQuery Tables

To keep the schema but only delete the data, you can use the `TRUNCATE TABLE` statement. This will remove all rows from the specified table while keeping the structure intact.

```SQL
TRUNCATE TABLE `openactive-monitor.openactive_analytics.opportunities`;
```

```SQL
TRUNCATE TABLE `openactive-monitor.openactive_analytics.opportunity_ingestion`;
```
## Add Clustering to an Existing Table

To improve query performance, you can add clustering to an existing table. This will reorganize the data based on the specified columns, which can speed up queries that filter on those columns.

```SQL
CREATE OR REPLACE TABLE `openactive-monitor.openactive_analytics.opportunities`
CLUSTER BY dataset_url, feed_id, id
AS
SELECT * FROM `openactive-monitor.openactive_analytics.opportunities`;
```

## Add new column to an existing table

Example: Add `afterChangeNumber` nullable integer column to the ingestion table:

```SQL
ALTER TABLE `openactive-monitor.openactive_analytics.opportunity_ingestion`
ADD COLUMN IF NOT EXISTS afterChangeNumber INT64;
```

After running these, you may still continue seeing old data in the tables due to caching. To ensure you see the latest data, you can run a simple query to refresh the cache:

```SQL
SELECT * FROM `openactive-monitor.openactive_analytics.opportunities` LIMIT 100;
```