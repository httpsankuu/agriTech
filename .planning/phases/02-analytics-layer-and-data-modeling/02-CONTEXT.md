# Phase 2 Context: Analytics Layer and Data Modeling

**Date:** 2026-09-11
**Phase:** 2 - Analytics Layer and Data Modeling
**Goal:** Build the core analytics layer required by the Track 3 problem statement based on the cleaned datasets.

## <domain>
Data Engineering / Analytics / SQL Modeling
</domain>

## <canonical_refs>
- \.planning/codebase/ARCHITECTURE.md\
- \src/analytics/build_model.py\
</canonical_refs>

## <decisions>

### 1. Analytics Scope & Metrics
- **Total crop arrivals in Quintals:** Aggregate rrival_quantity_qtl from Arrivals.
- **Crop-wise arrival distribution:** Group arrivals by crop_name.
- **Top Mandis by arrival volume:** Rank mandis by total rrival_quantity_qtl.
- **Daily/weekly/monthly arrival trends:** Time-series aggregation of arrivals.
- **Wholesale modal price vs MSP:** Compare modal_price to msp in Price dataset.
- **Price crash instances:** Flag records where modal_price < msp.
- **Average transit time by warehouse:** Average 	ransit_hours_clean grouped by destination_warehouse.
- **Transport delay rate & Routes with highest delay frequency:** Requires defining a delay threshold (e.g., transit_hours > expected) to calculate frequency by route.
- **Weather impact on crop arrivals:** Join Arrivals and Weather on mandi_num and date_str, correlating ainfall_mm with rrival_quantity_qtl.

### 2. Implementation Rules
- **Data Source:** Use ONLY the cleaned datasets from \Dataset/clean/\.
- **Reproducibility:** Keep analytics code reproducible and strictly separated from the data cleaning pipeline.
- **Validation:** Do not build the final dashboard or AI agent until this analytics layer is validated.
</decisions>

## <code_context>
- \src/analytics/build_model.py\: Currently implements partial logic (ingestion, views for price crashes, weather). Needs extension for delay rates and explicit trend views.
- \src/analytics/validate_metrics.py\: Used for asserting the correctness of the analytical views.
</code_context>
