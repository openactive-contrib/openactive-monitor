# Big Query Developer Guide

## Clean up BigQuery Tables

To keep the schema but only delete the data, you can use the `TRUNCATE TABLE` statement. This will remove all rows from the specified table while keeping the structure intact.

```SQL
TRUNCATE TABLE `openactive-monitor.openactive_analytics.opportunities`;
```

```SQL
TRUNCATE TABLE `openactive-monitor.openactive_analytics.opportunity_ingestion`;
```
## Add Clustering while creating a new table (opportunities)

1- Go to your dataset and click Create Table.

2- Under Schema, define your columns (or use "Auto-detect").

3- Scroll down to Partition and cluster settings.

4- In the Cluster columns field, type your three columns in order: dataset_url, feed_id, id.

Note: The order matters! Put the column you filter by most frequently first.

5- Click Create Table.

Opportunities table schema:

```json
[
  {
    "name": "dataset_url",
    "mode": "NULLABLE",
    "type": "STRING",
    "description": "Dataset URL.",
    "fields": []
  },
  {
    "name": "feed_id",
    "mode": "NULLABLE",
    "type": "STRING",
    "description": "Feed identifier (normalised feed url)",
    "fields": []
  },
  {
    "name": "id",
    "mode": "NULLABLE",
    "type": "STRING",
    "description": "ID from the RPDE feed",
    "fields": []
  },
  {
    "name": "data_id",
    "mode": "NULLABLE",
    "type": "STRING",
    "description": "Data ID from the RPDE feed, which may differ from the RPDE item ID",
    "fields": []
  },
  {
    "name": "kind",
    "mode": "NULLABLE",
    "type": "STRING",
    "description": "Kind of the opportunity, e.g. Event, FacilityUse, etc.",
    "fields": []
  },
  {
    "name": "modified",
    "mode": "NULLABLE",
    "type": "INTEGER",
    "description": "Modified timestamp from the RPDE feed",
    "fields": []
  },
  {
    "name": "json_data",
    "mode": "NULLABLE",
    "type": "JSON",
    "description": "Opportunity data as ingested from the feed, without any transformations or normalizations",
    "fields": []
  },
  {
    "name": "inherited_data",
    "mode": "NULLABLE",
    "type": "JSON",
    "description": "",
    "fields": []
  },
  {
    "name": "activity",
    "mode": "NULLABLE",
    "type": "JSON",
    "description": "Activity labels associated with the opportunity",
    "fields": []
  },  
  {
    "name": "facility",
    "mode": "NULLABLE",
    "type": "JSON",
    "description": "Facility label associated with the opportunity",
    "fields": []
  },
  {
    "name": "location",
    "mode": "NULLABLE",
    "type": "JSON",
    "description": "Geographical location of the opportunity",
    "fields": []
  },
  {
    "name": "startDate",
    "mode": "NULLABLE",
    "type": "TIMESTAMP",
    "description": "Opportunity start date and time",
    "fields": []
  },
  {
    "name": "endDate",
    "mode": "NULLABLE",
    "type": "TIMESTAMP",
    "description": "Opportunity end date and time",
    "fields": []
  },
  {
    "name": "ageRange",
    "mode": "NULLABLE",
    "type": "JSON",
    "description": "Age range for the opportunity.",
    "fields": []
  },
  {
    "name": "level",
    "mode": "NULLABLE",
    "type": "JSON",
    "description": "Difficulty level of the opportunity.",
    "fields": []
  },
  {
    "name": "has_superEvent",
    "mode": "NULLABLE",
    "type": "JSON",
    "description": "SuperEvent URL or inplace superEvent data for the opportunity",
    "fields": []
  },
  {
    "name": "has_subEvent",
    "mode": "NULLABLE",
    "type": "JSON",
    "description": "SubEvent URLs or inplace subEvent data for the opportunity",
    "fields": []
  }
]
```

## Add new column to an existing table

Example: Add `afterChangeNumber` nullable integer column to the ingestion table:

```SQL
ALTER TABLE `openactive-monitor.openactive_analytics.opportunity_ingestion`
ADD COLUMN IF NOT EXISTS afterChangeNumber INT64;
```

Add `is_regular` to the feeds table (for opportunity-insights):

```SQL
ALTER TABLE `openactive-monitor.openactive_analytics.feeds`
ADD COLUMN IF NOT EXISTS is_regular BOOL;
```

After the next `ingest_feeds` run the column is populated for every feed. Prior rows remain `NULL` until they are touched again.

After running these, you may still continue seeing old data in the tables due to caching. To ensure you see the latest data, you can run a simple query to refresh the cache:

```SQL
SELECT * FROM `openactive-monitor.openactive_analytics.opportunities` LIMIT 100;
```