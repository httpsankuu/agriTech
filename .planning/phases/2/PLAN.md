# Phase 2: Analytics Layer and Data Modeling

## Context
This phase focuses on transforming our clean, rescued datasets into a query-ready structured data model. We will load the data into a local SQLite database (`Dataset/analytics.db`) to enable efficient querying for both the Executive Dashboard (Phase 3) and the Agentic Graph AI (Phase 4).

## Requirements
- All clean datasets from `Dataset/clean/` must be ingested into SQLite tables.
- Core business metrics (Total arrivals, Price vs MSP, Weather correlations) should be modeled as SQL Views.
- A Python validation script must assert that the tables are populated and the views yield expected structural results.

## Execution Plan

### Task 1: Tracer Slice (Database Init & Core Tables) [checkpoint:decision]
**Description**: Initialize the SQLite database and ingest the primary entities (`mandi_master` and `mandi_arrivals`).
**Files to create/modify**:
- `src/analytics/build_model.py`
- `Dataset/analytics.db` (Output)
**Steps**:
1. Create `src/analytics/build_model.py`.
2. Connect to SQLite database at `Dataset/analytics.db`.
3. Read `Dataset/clean/track3_mandi_master_clean.csv` and ingest as table `dim_mandi`.
4. Read `Dataset/clean/track3_mandi_arrivals_clean.csv` and ingest as table `fact_arrivals`.
5. Verify the tables are created successfully.

### Task 2: Ingest Remaining Fact Tables
**Description**: Load prices, logistics, and weather data into the database.
**Files to create/modify**:
- `src/analytics/build_model.py`
**Steps**:
1. Add logic to load `track3_price_and_msp_clean.csv` as `fact_prices`.
2. Add logic to load `track3_transport_logistics_clean.csv` as `fact_logistics`.
3. Add logic to load `track3_weather_sensors_clean.csv` as `fact_weather`.
4. Run the script and verify all 5 tables exist in `analytics.db`.

### Task 3: Create Analytical Views
**Description**: Define SQL views for the core business metrics to abstract complex joins for the dashboard and AI agent.
**Files to create/modify**:
- `src/analytics/build_model.py`
**Steps**:
1. Create view `vw_price_vs_msp`: Joins `fact_prices` and `dim_mandi` to calculate price crash instances (`modal_price < msp`) and average price deviation.
2. Create view `vw_transit_performance`: Aggregates `fact_logistics` to compute average transit time and delay rates by destination warehouse.
3. Create view `vw_mandi_daily_summary`: Joins arrivals and weather to expose daily volume alongside rainfall and temperature (enabling weather impact analysis).
4. Create view `vw_crop_summary`: Aggregates total arrival volume by crop and mandi.

### Task 4: Data Validation Checks
**Description**: Write a test script to validate the data model.
**Files to create/modify**:
- `src/analytics/validate_metrics.py`
**Steps**:
1. Write a script that connects to `analytics.db`.
2. Run `SELECT COUNT(*)` on all tables and views to ensure data is present.
3. Assert that `vw_price_vs_msp` contains columns for price crashes.
4. Output a summary report of the validation to the console.
