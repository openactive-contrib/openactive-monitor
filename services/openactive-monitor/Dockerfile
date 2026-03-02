FROM python:3.11-slim

# Install system dependencies for geospatial libraries (geopandas, pyproj, shapely)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for Cloud Run (uses PORT env variable, defaults to 8080)
EXPOSE 8080

# Run Streamlit
CMD streamlit run main.py \
    --server.address=0.0.0.0 \
    --server.port=${PORT:-8080} \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --server.enableWebsocketCompression=false \
    --browser.gatherUsageStats=false
