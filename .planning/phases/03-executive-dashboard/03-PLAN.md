# Phase 3: Executive Dashboard

> Implements the executive dashboard using Streamlit to visualize analytics data.

## Must Haves
- Streamlit application running on `agritech_analytics.db`.
- KPIs, Charts, and Sidebar filters implemented.

## Execution Plan

### Wave 1: Initialization & Data Layer
**Task 3.1.1: Initialize Streamlit application & data loader**
- **Description:** Set up the package structure, main application file, and the data access layer connecting to SQLite.
- **files_modified:** `src/dashboard/__init__.py`, `src/dashboard/app.py`, `src/dashboard/data_loader.py`
- `<action>` Create `src/dashboard/__init__.py`.
- `<action>` Implement `src/dashboard/data_loader.py` with `@st.cache_data` functions to load data from `Dataset/agritech_analytics.db`.
- `<action>` Initialize basic `src/dashboard/app.py` page layout.
- `<automated>` `python -m py_compile src/dashboard/app.py src/dashboard/data_loader.py`

### Wave 2: UI Layout & Interactive Elements
**Task 3.2.1: Build filters and KPI cards**
- **Description:** Add sidebar filters for Date, Mandi, and Crop, and implement top-row KPI metrics.
- **files_modified:** `src/dashboard/app.py`
- `<action>` Add `st.sidebar` filters (`st.date_input`, `st.multiselect`).
- `<action>` Filter dataframes reactively based on selection.
- `<action>` Render KPI cards using `st.columns` and `st.metric` for Volume and Price vs MSP.
- `<automated>` `python -m py_compile src/dashboard/app.py`

**Task 3.2.2: Build interactive charts and deep-dive tables**
- **Description:** Implement the line charts for trends and scatter plots for weather correlations.
- **files_modified:** `src/dashboard/app.py`
- `<action>` Render Arrival Trends chart using `st.line_chart`.
- `<action>` Render Weather Correlations scatter plot.
- `<action>` Render Price Crashes deep-dive table.
- `<automated>` `python -m py_compile src/dashboard/app.py`
