# Phase 3 - Patterns

Based on the research and codebase analysis, the following files will be created or modified in this phase. Their roles, data flow, and closest existing patterns are detailed below.

## 1. `src/dashboard/app.py`
**Role:** Main Streamlit application file. Handles the UI layout, sidebar filters, KPI metrics rendering, and interactive charts.
**Data Flow:** 
- Imports data loading functions from `data_loader.py`.
- Receives user input from Streamlit widgets (filters).
- Reactively filters DataFrames based on user selections and passes the subsets to visualization components (KPIs and charts).
**Closest Existing Analog:** This is a new UI component, but it will follow the standard Python module entry point pattern seen in `src/analytics/build_model.py`.
**Code Excerpt (Pattern Example):**
```python
# Standard entry point pattern (from src/analytics/build_model.py)
if __name__ == "__main__":
    main()
```

## 2. `src/dashboard/data_loader.py`
**Role:** Dedicated data extraction module to keep the Streamlit app fast and clean.
**Data Flow:** Connects to the SQLite database `agritech_analytics.db`, reads the required analytical views using `pandas.read_sql`, caches the results using `@st.cache_data`, and returns DataFrames to `app.py`.
**Closest Existing Analog:** `src/analytics/build_model.py` and `src/data_engineering/clean_data.py` (both demonstrate the standard directory resolution and SQLite connection patterns used in this project).
**Code Excerpt (Pattern Example):**
```python
# Path resolution and database connection pattern (from src/analytics/build_model.py)
import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "Dataset")
DB_PATH = os.path.join(DATA_DIR, "agritech_analytics.db")

# Example usage with pandas
# conn = sqlite3.connect(DB_PATH)
# df = pd.read_sql("SELECT * FROM vw_crop_summary", conn)
```

## 3. `src/dashboard/__init__.py`
**Role:** Package initialization file to allow importing from the `dashboard` module.
**Data Flow:** N/A.
**Closest Existing Analog:** Standard Python package structure.
**Code Excerpt:**
*(Empty file)*
