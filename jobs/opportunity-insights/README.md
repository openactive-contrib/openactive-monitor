# opportunity-insights — Cloud Run Job

BigQuery-based analysis job that reads from `openactive_analytics.opportunities`
and writes per-feed and aggregate metrics into the `insight_*` tables, plus a
per-feed data-quality assessment into `feed_quality`.

## Data quality assessment

After the regular insight tables are written, the job assesses each feed's
data quality and writes one row per `(dataset_url, feed_id)` to `feed_quality`
(full overwrite per run — current state only, no history). The QA logic lives
under `quality/` and is driven by the same `--reference-date` as the rest of
the run.

For each feed it records:

| Column | Source |
|--------|--------|
| `status` | `OK` / `WARNING` / `ERROR`. Derived from latest `opportunity_ingestion.status`, an HTTP probe of `feed_url` for ERROR-state feeds, and presence of required fields. |
| `warnings`, `errors` | JSON arrays of human-readable messages. |
| `missing_required_fields` | JSON object keyed by opportunity kind (e.g. `SessionSeries`) listing required fields absent from **all** of up to 10 random `json_data` samples for that kind in the last 5 days. Required fields per kind are defined in `quality/required_fields.py` and follow the [OpenActive Modelling Opportunity Data](https://openactive.io/modelling-opportunity-data/) spec. |
| `location_completeness`, `start_date_completeness`, `end_date_completeness`, `activities_completeness`, `facilities_completeness` | Percentage (0–100) of opportunities updated in the last 5 days where each top-level column is populated and non-empty. |
| `num_future_opportunity_items` | Carried over from the in-memory `feed_insights` row built earlier in the same run. |
| `grade` | `Gold` / `Silver` / `Bronze` / `None` per the rules in `quality/assess.py` — driven by future-event volume, completeness thresholds, and missing-required-fields. |

To skip the QA step (e.g. when iterating on the analytic queries), pass
`--skip-quality`. To create the `feed_quality` table on first run, pass
`--init-tables` (existing behaviour).

This job needs read access to a few static reference files (UK boundary
GeoJSONs and the Sport-England mapping CSVs) that live in the **`volume-1`
GCS bucket** under `data-analysis/`. They are mounted into the container at
runtime via a Cloud Run **Cloud Storage volume**.

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Builds the runtime image (Python 3.13 + geopandas/shapely). Sets `INSIGHTS_GEO_DIR=/volume-1/data-analysis`. |
| `cloudbuild.yaml` | Cloud Build pipeline: build → push → `gcloud run jobs deploy`. |
| `.dockerignore` / `.gcloudignore` | Excludes `virt/`, `__pycache__`, `.env`, etc. |
| `.env.example` | Local development env vars. |

## Local build / push (optional)

```bash
gcloud builds submit \
  --config=jobs/opportunity-insights/cloudbuild.yaml \
  --substitutions=_JOB_NAME=opportunity-insights,_REGION=europe-west2 \
  .
```

(Run from the repo root so the build context can read `jobs/opportunity-insights`.)

---

## One-time setup in the GCP Web UI

These steps create the job, mount the `volume-1` bucket, and grant IAM. You
only need to do them **once**; subsequent Cloud Build deploys keep the
volume / env vars / IAM intact.

### 1. Make sure the bucket exists

Cloud Storage → Buckets → confirm a bucket literally named **`volume-1`**
exists in project `openactive-monitor`. It must contain:

```
data-analysis/000-location-regions.geojson
data-analysis/000-location-districts.geojson
data-analysis/000-location-nhstrusts.geojson
data-analysis/000-SE-sport-and-discipline.csv
data-analysis/000-OA-SE-mapping.csv
```

If the bucket is in a different region than `europe-west2`, prefer making it
`europe-west2` (or multi-region `eu`) to avoid egress.

### 2. First deploy (to create the job)

Trigger Cloud Build once with the config above, or in the Console:

- **Cloud Run** → top tab **Jobs** → **Create job**
  - Container image URL:
    `gcr.io/openactive-monitor/github.com/openactive-contrib/opportunity-insights:<sha>`
  - Job name: `opportunity-insights`
  - Region: `europe-west2`
  - **Container, Variables & Secrets**:
    - Memory: at least **4 GiB** (geopandas + BigQuery result frames). Bump
      to 8–16 GiB if you see OOMs against the 8M-row `opportunities` table.
    - CPU: 2
    - Task timeout: e.g. **1h**
    - Environment variables (same list as `.env.example`, plus
      `INSIGHTS_GEO_DIR=/volume-1/data-analysis`).

### 3. Mount the `volume-1` bucket

Still on the **Create / Edit job** page:

1. Open the **Volumes** tab → **Add volume**.
   - Volume type: **Cloud Storage bucket**
   - Volume name: `volume-1`
   - Bucket: `volume-1`
   - Read-only: ✅ (recommended)
2. Open the **Containers → Volume mounts** tab → **Mount volume**.
   - Name: `volume-1`
   - Mount path: `/volume-1`
3. Click **Create / Update**.

Cloud Run uses Cloud Storage FUSE under the hood; no code changes needed —
`geopandas.read_file("/volume-1/data-analysis/...geojson")` just works.

### 4. Service account & IAM

The job runs as a service account (default: the Compute Engine default SA,
`PROJECT_NUMBER-compute@developer.gserviceaccount.com`, unless you picked
another). Grant it:

| Resource | Role | Why |
|----------|------|-----|
| Bucket `volume-1` | **Storage Object Viewer** (`roles/storage.objectViewer`) | Read GeoJSON / CSV reference data |
| Project `openactive-monitor` | **BigQuery Data Editor** (`roles/bigquery.dataEditor`) on dataset `openactive_analytics` | Read `opportunities`, write `insight_*` tables |
| Project `openactive-monitor` | **BigQuery Job User** (`roles/bigquery.jobUser`) | Run query jobs |

Grant on the bucket:
- **Cloud Storage** → bucket `volume-1` → **Permissions** → **Grant access**
  → principal = the job’s service account → role
  `Storage Object Viewer`.

Grant on BigQuery:
- **BigQuery** → dataset `openactive_analytics` → **Sharing → Permissions**
  → add the service account with `BigQuery Data Editor`.
- **IAM & Admin → IAM** → grant the same SA `BigQuery Job User` at project
  level.

### 5. (Optional) First-run table creation

The job has a `--init-tables` flag. To pass CLI args from the Console:

- Cloud Run → Jobs → `opportunity-insights` → **Edit & deploy new revision**
  → Container → **Container command / args**:
  - Command: leave default (uses Dockerfile `ENTRYPOINT`)
  - Arguments: `--init-tables`

Run once, then remove the arg.

### 6. Trigger

- **Manual:** Cloud Run → Jobs → `opportunity-insights` → **Execute**.
- **Scheduled:** Cloud Scheduler → Create job → target = HTTP →
  `https://run.googleapis.com/v2/projects/openactive-monitor/locations/europe-west2/jobs/opportunity-insights:run`
  with OAuth (SA needs `roles/run.invoker` on the job).
- **Workflow / Pub/Sub:** the existing `workflows/run-job.yaml` already
  accepts a job name in the Pub/Sub message body, so publishing
  `opportunity-insights` (base64-encoded) to its trigger topic will run it.

---

## Subsequent deploys

After the initial setup, every push that triggers
`jobs/opportunity-insights/cloudbuild.yaml` will:

1. Build a new image tagged with `$COMMIT_SHA`.
2. Push to GCR.
3. `gcloud run jobs deploy opportunity-insights --image=...` — this only
   updates the image + env vars; **the volume mount, IAM, args, memory and
   timeout settings configured in the Console are preserved.**

If you ever recreate the job from scratch, redo step 3 (volume mount) and
step 4 (IAM).

