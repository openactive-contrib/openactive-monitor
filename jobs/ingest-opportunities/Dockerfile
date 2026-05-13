FROM python:3.13-slim

# System packages for geopandas/shapely/pyogrio + TLS roots
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libexpat1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the ingest-opportunities code
COPY . .

# Default mount path of the "volume-1" GCS bucket inside the container.
# The Cloud Run Job is configured to mount gs://volume-1 at /volume-1,
# so the boundary GeoJSONs live at /volume-1/data-analysis.
ENV INGEST_BOUNDARY_DIR=/volume-1/data-analysis

# CSV debug dumps are off by default; if enabled, write to a writable path.
ENV OPPORTUNITY_CSV_OUTPUT_DIR=/tmp/opportunities/csv
ENV OPPORTUNITIES_OUTPUT_DIR=/tmp/opportunities

# Click CLI; pass flags via Cloud Run Job "args".
ENTRYPOINT ["python", "main.py"]

