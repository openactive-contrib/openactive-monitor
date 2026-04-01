# Developer Guide

Checkout the project and run the following command to setup the project structure:

```bash
make all
```

## Services

### Open Active Monitor

To start the frontend application, run the following command:

```bash
streamlit run main.py
```

## Jobs

### Authenticate locally

To be able to connect BigQuery from your local machine, you need to authenticate with Google Cloud.

Run this command in your terminal. It will open a browser to log you in and save a local credential file that Python will find automatically:

```
gcloud auth application-default login
```

### Ingest Feeds

### Ingest Opportunities