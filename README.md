# 🌾 AgriTech - Mandi-to-Market Supply Chain Optimizer

An AgriTech decision-support platform for analyzing crop arrivals, price discovery, transportation efficiency, and weather impact across the Mandi-to-Market supply chain. 

Developed for the TransOrg AgentIQ Datathon — Track 3.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red) ![SQLite](https://img.shields.io/badge/SQLite-3-green)

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/httpsankuu/agriTech.git
cd agriTech

# Install dependencies
pip install -r requirements.txt
```

### Running the Pipeline

```bash
# Step 1: Clean the raw data
python src/data_engineering/clean_data.py

# Step 2: Build the analytics database
python src/analytics/build_model.py

# Step 3: Validate the analytics views
python src/analytics/validate_metrics.py

# Step 4: Launch the dashboard
streamlit run src/dashboard/app.py
```
The dashboard will open locally in your browser.

---

## Data Overview

The project processes 5 core datasets covering the full supply chain, translating raw datathon records into a standardized structure. 

*Note: Dataset redistribution is subject to the datathon's data-sharing terms.*

| Dataset | Rows (Raw) | Rows (Cleaned) | Key Cleaning Actions |
|---------|-----------|----------------|---------------------|
| Mandi Master | 60 | 57 | Standardized IDs, title-cased names |
| Crop Arrivals | 25,750 | 25,000 | Mapped crop names, converted units to Quintals |
| Prices & MSP | 12,000 | 12,000 | Stripped currency symbols |
| Transport Logistics | 10,400 | 10,000 | Excluded invalid negative transit records, standardized distances |
| Weather Sensors | 15,000 | 15,000 | Converted Fahrenheit to Celsius, inches to millimeters |

Full column definitions and cleaning rationale are documented in:
- [`Dataset/clean/DATA_DICTIONARY.md`](Dataset/clean/DATA_DICTIONARY.md)

---

## Validated Analytics Metrics

The following metrics were validated against the analytics layer database:

- **Cleaned Arrivals Rows:** 25,000
- **Total Arrivals:** 5,659,184.82 QTL
- **Active Mandis:** 57
- **Crops Tracked:** 6
- **Price Records:** 12,000
- **Price Crashes:** 3,924
- **Missing Modal Prices:** 610
- **Missing MSP Values:** 2,377
- **Transport Records:** 10,000
- **Invalid Negative Transit Records:** 539
- **Valid Trips:** 8,455
- **Routes:** 342
- **Delayed Trips:** 1,584
- **Transport Delay Rate:** 18.68%
- **Weather Records:** 15,000
- **Weather-Matched Arrival Days:** 6,345
- **Weather-Unmatched Arrival Days:** 6,001

### Delay Methodology
A trip is considered delayed when its valid transit time is greater than 1.5× the average valid transit time for its specific Mandi → Warehouse route. Invalid/negative transit records are excluded from the baseline calculation.

### Weather Methodology
Weather records are aggregated to daily grain before being joined with arrival data. The weather join must not inflate arrival totals. Metrics represent an association/correlation with arrival volumes, not a direct causal relationship.

---

## Dashboard

An interactive intelligence dashboard built with Streamlit and Plotly, styled with a custom Newsprint-inspired editorial theme.

### Sections
- **KPI Strip:** Total arrivals, price crashes, delay rate, routes monitored
- **Supply Intelligence:** Daily arrival trend, crop distribution, top Mandis by volume
- **Price Discovery:** Modal price vs MSP over time, worst crash instances
- **Logistics:** Routes with highest delay frequency
- **Weather × Supply:** Rainfall vs arrivals correlation, weather coverage

### Interactive Filters
- Date Range
- Crop
- Mandi
- District

---

## AI Query Agent

An integrated natural-language interface allowing users to interact with the agricultural analytics data using plain English questions. It operates on top of the analytics layer.

**Workflow:**
1. **Interpret:** Parses the user's question via regex pattern matching to extract intents (crop, mandi, metric, time range).
2. **Query:** Dynamically generates and executes SQL queries against the underlying SQLite analytics views.
3. **Visualize:** Selects an appropriate visualization (line, bar, scatter) based on the context.
4. **Summarize:** Provides a concise text summary of the queried statistics.

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data Engineering | Python, Pandas, NumPy |
| Database | SQLite with analytical views |
| Dashboard | Streamlit, Plotly |
| AI Agent | Regex pattern matching and SQL generation |
| Styling | Custom CSS, Newsprint-inspired theme |

---

## Project Structure

```text
agriTech/
├── Dataset/
│   ├── clean/
│   │   └── DATA_DICTIONARY.md
│   └── agritech_analytics.db
├── src/
│   ├── analytics/
│   │   ├── build_model.py
│   │   └── validate_metrics.py
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── app.py
│   │   ├── charts.py
│   │   ├── components.py
│   │   ├── queries.py
│   │   └── styles.css
│   └── data_engineering/
│       └── clean_data.py
├── .gitignore
├── .streamlit/
│   └── config.toml
├── README.md
└── requirements.txt
```
