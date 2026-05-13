# ingest-opportunities — Cloud Run Job

Ingests RPDE opportunity data into BigQuery (`openactive_analytics.opportunities`)
with incremental cursor tracking, superEvent/subEvent denormalization, and UK
postcode/boundary geolocation.

UK boundary GeoJSONs (`000-location-districts.geojson`,
`000-location-regions.geojson`) live in the **`volume-1` GCS bucket** under
`data-analysis/`. They are mounted into the container at runtime via a
Cloud Run **Cloud Storage volume** at `/mnt/volume-1`. The Python code reads
the path from the `INGEST_BOUNDARY_DIR` env var (set by the Dockerfile and
cloudbuild.yaml to `/mnt/volume-1/data-analysis`).

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Python 3.13 runtime; installs `requirements.txt` and sets `INGEST_BOUNDARY_DIR=/mnt/volume-1/data-analysis`. |
| `cloudbuild.yaml` | Cloud Build pipeline: build → push → `gcloud run jobs deploy`. |
| `.dockerignore` / `.gcloudignore` | Excludes `virt/`, `__pycache__`, `.env`, etc. |
| `.env.example` | Local development env vars. |

## Build / push

```bash
gcloud builds submit \
  --config=jobs/ingest-opportunities/cloudbuild.yaml \
  --substitutions=_JOB_NAME=ingest-opportunities,_REGION=europe-west2 \
  .
```

(Run from the repo root.)

---

## One-time setup in the GCP Web UI

Identical to the `opportunity-insights` setup. You only need to do this
**once**; subsequent Cloud Build deploys preserve volume / env / IAM.

### 1. Bucket

Cloud Storage → confirm bucket **`volume-1`** in `openactive-monitor` exists
and contains:

```
data-analysis/000-location-districts.geojson
data-analysis/000-location-regions.geojson
```

Region `europe-west2` (or multi-region `eu`) is preferred.

### 2. First deploy (creates the job)

Trigger Cloud Build once, or in the Console:

- **Cloud Run** → top tab **Jobs** → **Create job**
  - Image: `gcr.io/openactive-monitor/github.com/openactive-contrib/ingest-opportunities:<sha>`
  - Job name: `ingest-opportunities`
  - Region: `europe-west2`
  - **Memory: 8–16 GiB** (BigQuery merges + denormalisation can be heavy).
  - CPU: 2–4
  - Task timeout: e.g. **2h**
  - Environment variables (mirroring `.env.example` plus `INGEST_BOUNDARY_DIR`).

### 3. Mount the `volume-1` bucket

On the **Edit job** page:

1. **Volumes** tab → **Add volume**
   - Type: **Cloud Storage bucket**
   - Volume name: `volume-1`
   - Bucket: `volume-1`
   - Read-only: ✅
2. **Containers → Volume mounts** → **Mount volume**
   - Name: `volume-1`
   - Mount path: `/mnt/volume-1`
3. **Update**.

Cloud Storage FUSE handles the mount; `geopandas.read_file("/mnt/volume-1/data-analysis/...")` just works.

### 4. Service account & IAM

Grant the job's runtime service account:

| Resource | Role |
|----------|------|
| Bucket `volume-1` | `roles/storage.objectViewer` |
| Dataset `openactive_analytics` | `roles/bigquery.dataEditor` |
| Project | `roles/bigquery.jobUser` |

### 5. Trigger

- **Manual:** Cloud Run → Jobs → `ingest-opportunities` → **Execute**.
- **Workflow / Pub/Sub:** the existing `workflows/run-job.yaml` accepts a
  job name in the Pub/Sub message body, so publishing
  `ingest-opportunities` (base64-encoded) to the trigger topic runs it.
- **Scheduled:** Cloud Scheduler → HTTP target →
  `https://run.googleapis.com/v2/projects/openactive-monitor/locations/europe-west2/jobs/ingest-opportunities:run`,
  OAuth, SA needs `roles/run.invoker`.

---

## Subsequent deploys

Every push that triggers `jobs/ingest-opportunities/cloudbuild.yaml`:

1. Builds a new image tagged with `$COMMIT_SHA`.
2. Pushes to GCR.
3. `gcloud run jobs deploy ingest-opportunities --image=...` — only the
   image + env vars are updated; volume mount, IAM, args, memory and
   timeout configured in the Console are preserved.

