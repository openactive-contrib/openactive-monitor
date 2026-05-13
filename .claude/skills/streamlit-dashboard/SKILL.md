---
name: streamlit-dashboard
description: Use this skill when modifying the Streamlit dashboard, adding new pages, or migrating the UI from pickle-based data to BigQuery.
---

# Skill: Streamlit Dashboard

## When to use
Use this skill when modifying the Streamlit dashboard in `services/openactive-monitor/`.

## Key files
- `services/openactive-monitor/main.py` — App entry point, session state initialization
- `services/openactive-monitor/navigation/overview.py` — Overview page
- `services/openactive-monitor/navigation/details.py` — Details page
- `services/openactive-monitor/style.css` — Custom CSS

## Current state
- The dashboard currently reads from **legacy pickle files** (not BigQuery)
- It loads feeds, aggregate analysis, and sample items from pickle files at startup
- Uses `st.session_state` for caching across reruns
- Uses Seaborn for chart theming

## Future migration
The dashboard will need to be migrated to read from BigQuery tables (`feeds`, `opportunities`) instead of pickle files. When doing this:
- Use `google-cloud-bigquery` client (already in requirements)
- Cache BigQuery results using `@st.cache_data` or `st.session_state`
- Maintain the existing page structure (Overview, Details)

## Conventions
- `st.set_page_config()` must be the first Streamlit command
- Load CSS early to avoid visual flickering
- Use `st.navigation` + `st.Page` for multi-page layout

