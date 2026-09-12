# AgriTech - Mandi-to-Market Supply Chain Optimizer

A data-driven platform for the State Agriculture Board to monitor daily crop arrivals at local Mandis, track prices against the Minimum Support Price (MSP), and correlate these metrics with weather data. Transforms chaotic, messy raw data into an actionable executive dashboard.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the data cleaning pipeline
python src/data_engineering/clean_data.py

# 3. Build the analytics database
python src/analytics/build_model.py

# 4. Launch the dashboard
streamlit run src/dashboard/app.py
```

## Data at a Glance

| Dataset | Raw Rows | Clean Rows | Duplicates Removed |
|---------|----------|------------|-------------------|
| Mandi Master | 60 | 57 | 3 (5.0%) |
| Crop Arrivals | 25,750 | 25,000 | 750 (2.9%) |
| Prices & MSP | 12,000 | 12,000 | 0 |
| Transport Logistics | 10,400 | 10,000 | 400 (3.9%) |
| Weather Sensors | 15,000 | 15,000 | 0 |

**Coverage:** 57 active Mandis, 6 crops (Cotton, Maize, Mustard, Rice, Sugarcane, Wheat), date range Jan 1 – Sep 9, 2026.

## Key Analytics Metrics

| Metric | Value |
|--------|-------|
| Total Arrivals | 5,659,185 QTL |
| Price Crash Instances | 3,924 (modal price < MSP) |
| Total Trips Monitored | 8,455 |
| Delayed Trips | 1,584 (18.7% delay rate) |
| Weather-Matched Records | 52 of 3,328 arrival days |

## Phase 1: Data Rescue & Engineering

Raw, chaotic datasets were cleaned, standardized, and saved into query-ready formats. See `Dataset/clean/DATA_QUALITY_REPORT.md` for the full quality audit.

### Cleaning Steps

1. **Mandi Master** — Standardized `mandi_id` to `MANDI-XXX`. Title-cased `district`/`state`. Standardized `mandi_type` values.
2. **Crop Arrivals** — Mapped multilingual crop names (Hindi/English) to canonical English names. Converted all quantities to Quintals (`arrival_quantity_qtl`). Parsed dates to `YYYY-MM-DD`.
3. **Prices & MSP** — Stripped currency symbols and commas. Cast to numeric. Recovered 638 missing district values via mandi master join.
4. **Logistics** — Flagged 539 negative transit times. Standardized distance to kilometers. Cleaned vehicle registration numbers.
5. **Weather** — Converted temperatures to Celsius. Converted rainfall to millimeters. Standardized timestamps.

### How to Reproduce

```bash
python src/data_engineering/clean_data.py
```

## Phase 2: Analytics Layer

Builds the SQLite analytical database with 5 fact/dimension tables, 6 analytical views, and 4 performance indexes.

### Analytical Views

| View | Purpose |
|------|---------|
| `vw_crop_summary` | Daily crop arrivals aggregated by Mandi |
| `vw_mandi_performance` | Top Mandis ranked by arrival volume |
| `vw_arrival_trends` | Daily/weekly/monthly arrival time series |
| `vw_price_vs_msp` | Modal price vs MSP with crash detection |
| `vw_transit_delays` | Route-level delay rates (1.5× threshold) |
| `vw_weather_impact` | Rainfall & temperature correlated with arrivals |

### How to Build

```bash
python src/analytics/build_model.py
```

### Validation

```bash
python src/analytics/validate_metrics.py
```

## Phase 3: Executive Dashboard

An interactive Newsprint-style intelligence dashboard built with Streamlit and Plotly.

### Dashboard Sections

- **KPI Strip** — Total arrivals, price crashes, transport delay rate, routes monitored
- **Supply Intelligence** — Daily arrival trend chart + crop distribution bar chart + top Mandis table
- **Price Discovery** — Modal price vs MSP line chart + crash watch list with worst gaps
- **Logistics** — Routes under pressure (highest delay frequency)
- **Weather × Supply** — Rainfall vs arrivals scatter plot + weather coverage stats
- **Methodology** — Data transparency and assumptions expander

### Architecture

| File | Role |
|------|------|
| `app.py` | Dashboard orchestration, filters, layout |
| `components.py` | Reusable UI elements (KPI cards, section headers, masthead) |
| `charts.py` | Plotly visualization functions with Newsprint theme |
| `queries.py` | SQLite data access layer with Streamlit caching (1hr TTL) |
| `styles.css` | Centralized Newsprint styling (Playfair Display, JetBrains Mono, Inter) |

### How to Run

```bash
streamlit run src/dashboard/app.py
```

## Tech Stack

- **Data Engineering**: Python, Pandas, NumPy
- **Analytics**: SQLite, SQL views and indexes
- **Dashboard**: Streamlit, Plotly
- **Styling**: Custom CSS (Newsprint editorial theme)

## Project Structure

```
.
├── Dataset/
│   ├── *.csv, *.json, *.xlsx       # Raw datathon data
│   ├── clean/                       # Cleaned CSVs + data dictionary
│   └── agritech_analytics.db        # SQLite analytics database
├── src/
│   ├── data_engineering/
│   │   └── clean_data.py            # Data rescue pipeline
│   ├── analytics/
│   │   ├── build_model.py           # DB builder + view creator
│   │   └── validate_metrics.py      # View validation suite
│   └── dashboard/
│       ├── app.py                   # Streamlit dashboard
│       ├── charts.py                # Plotly chart functions
│       ├── components.py            # UI components
│       ├── queries.py               # Data access layer
│       └── styles.css               # Newsprint theme CSS
├── requirements.txt
└── README.md
```

