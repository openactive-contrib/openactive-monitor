FROM python:3.13-slim

# System packages required by geopandas/shapely/pyogrio + TLS roots
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libexpat1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the opportunity-insights code
COPY . .

# Default mount path of the "volume-1" GCS bucket inside the container.
# The Cloud Run Job is configured to mount gs://volume-1 at /mnt/volume-1
# so geojson/CSV reference data lives at /mnt/volume-1/data-analysis.
ENV INSIGHTS_GEO_DIR=/mnt/volume-1/data-analysis

# Run the Click CLI; flags can be appended via Cloud Run Job "args".
ENTRYPOINT ["python", "main.py"]

