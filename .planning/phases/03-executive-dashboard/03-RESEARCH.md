# Phase 3: Executive Dashboard - Research & Planning

## Objective
To plan the implementation of Phase 3 (Executive Dashboard) using Streamlit, answering "What do I need to know to PLAN this phase well?".

## 1. Data Foundation
The analytics layer (Phase 2) has successfully built a SQLite database (`Dataset/agritech_analytics.db`) which contains pre-computed analytical views optimized for our dashboard. We will query these views via `pandas.read_sql` and use Streamlit's caching mechanisms (`@st.cache_data`) for performance.

Relevant views available:
- `vw_crop_summary`: For crop-wise total arrivals and farmer count.
- `vw_arrival_trends`: For daily/weekly/monthly arrival trends.
- `vw_price_vs_msp`: For comparing wholesale modal price with MSP and identifying price crashes.
- `vw_weather_impact`: For correlating daily arrivals with temperature and rainfall.
- `dim_mandi`: For available Mandis for the filter.

## 2. Application Architecture
- **Framework**: Streamlit.
- **Location**: We will create a new directory and main application file at `src/dashboard/app.py`.
- **Data Loading**: We should implement a `data_loader.py` or use isolated cached functions in `app.py` to ensure the dashboard remains fast.

## 3. Dashboard Layout & UX
The layout should be clean, structured, and reactive to filters.

### Sidebar (Filters)
- **Date Range**: `st.date_input` to filter across a specific time period.
- **Mandi Filter**: `st.multiselect` for Mandi selection.
- **Crop Filter**: `st.multiselect` for Crop selection.

### Main Content Area
**Top Row: KPI Cards (`st.columns` + `st.metric`)**
- **Total Volume (Arrivals)**: Total quantity arrived based on filtered data.
- **Avg Price vs MSP**: Metric showing average modal price, with the deviation from MSP as the delta.
- **Weather / Delay Flags**: Highlight any weather anomalies (e.g. days with max rain).

**Middle Row: Interactive Charts**
- **Arrival Trends**: Line chart showing arrival volume over time (using `st.line_chart` or `plotly`).
- **Weather Correlations**: Scatter plot mapping `total_rainfall_mm` or `max_temp_c` against `daily_arrivals_qtl`.

**Bottom Row: Deep Dive**
- **Price Crashes**: A table or chart visualizing instances where modal price < MSP.

## 4. Addressing Specific Requirements
- **Interactivity & UX**: Addressed by sidebar filters. The dataframes will be reactively filtered based on these selections before rendering KPIs and charts.
- **Core KPIs & Storytelling**: The flow from high-level KPIs down to detailed trends to causal correlations tells a complete story of the agricultural supply chain.
- **Preparation for Phase 4 (Agentic AI)**: The Streamlit codebase should be written in a modular way (separating data extraction, filtering, and rendering) so the AI agent in Phase 4 can hook into these same dataframes for natural language querying.

## 5. Next Steps for Implementation
1. Create the `src/dashboard` package.
2. Build the data load functions to connect to SQLite.
3. Build the sidebar and the reactive data-filtering logic.
4. Render the `st.metric` KPIs.
5. Render the interactive charts.
