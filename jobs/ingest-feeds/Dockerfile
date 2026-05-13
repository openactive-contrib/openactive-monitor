FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt-get/lists/*

WORKDIR /app

# Copy requirements from the current directory (ingest-feeds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the ingest-feeds code
COPY . .

# Run the script
CMD ["python", "main.py"]