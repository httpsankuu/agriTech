# AgriTech — Mandi-to-Market Supply Chain Optimizer

A data platform that monitors daily crop arrivals at Mandis, tracks prices against MSP, and correlates with weather data. Built for the State Agriculture Board to turn chaotic, multilingual datasets into actionable intelligence.

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

The dashboard will open at `http://localhost:8501`.

---

## Data Overview

The project works with 5 datasets covering the full supply chain — from Mandi infrastructure to crop arrivals, pricing, logistics, and weather.

| Dataset | Rows (Raw) | Rows (Cleaned) | Key Cleaning Actions |
|---------|-----------|----------------|---------------------|
| Mandi Master | 60 | 57 | Standardized IDs, title-cased names, removed 3 duplicates |
| Crop Arrivals | 25,750 | 25,000 | Mapped Hindi/English crop names, converted units to Quintals, removed 750 duplicates |
| Prices & MSP | 12,000 | 12,000 | Stripped currency symbols, recovered 638 missing districts via join |
| Transport Logistics | 10,400 | 10,000 | Flagged 539 negative transit times, standardized distances, removed 400 duplicates |
| Weather Sensors | 15,000 | 15,000 | Converted Fahrenheit to Celsius, inches to millimeters |

**Coverage:** 57 Mandis, 6 crops (Wheat, Rice, Cotton, Maize, Mustard, Sugarcane), Jan – Sep 2026.

Full column definitions are in [`Dataset/clean/DATA_DICTIONARY.md`](Dataset/clean/DATA_DICTIONARY.md).
Cleaning decisions and rationale are documented in [`Dataset/clean/DATA_QUALITY_REPORT.md`](Dataset/clean/DATA_QUALITY_REPORT.md).

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Total Arrivals | 5,659,185 QTL |
| Price Crashes (below MSP) | 3,924 instances |
| Transport Delay Rate | 18.7% (1,584 of 8,455 trips) |
| Active Mandis | 57 |
| Crops Tracked | 6 |

---

## Dashboard

An interactive intelligence dashboard built with Streamlit and Plotly, styled with a custom Newsprint editorial theme.

### Sections

| Section | Description |
|---------|-------------|
| **KPI Strip** | Total arrivals, price crashes, delay rate, routes monitored |
| **Supply Intelligence** | Daily arrival trend, crop distribution, top Mandis by volume |
| **Price Discovery** | Modal price vs MSP over time, worst crash instances |
| **Logistics** | Routes with highest delay frequency |
| **Weather × Supply** | Rainfall vs arrivals correlation, weather coverage |
| **AI Query Agent** | Ask questions in plain English, get charts automatically |

### Interactive Filters

- **Date Range** — narrow any chart to a specific time window
- **Crop** — filter by Wheat, Rice, Cotton, Maize, Mustard, or Sugarcane
- **Mandi** — filter by a specific Mandi
- **District** — filter by district

---

## AI Query Agent

Ask questions in natural language and get instant charts and summaries.

**Examples:**
- *"Show me the daily arrival trend of Wheat"*
- *"What are the top 5 mandis by arrival volume?"*
- *"Show price crashes for Cotton"*
- *"What is the correlation between rainfall and arrivals?"*

### How It Works

1. **Parse** — extracts intent, crop, mandi, and time range from your question
2. **Query** — generates SQL against the analytics database
3. **Visualize** — selects the best chart type (line, bar, scatter) and renders it
4. **Summarize** — provides a text summary with key statistics

| Query Type | Example | Chart |
|-----------|---------|-------|
| Trend | "arrival trend of Wheat" | Line |
| Top N | "top 5 mandis" | Horizontal bar |
| Price Crash | "price crashes for Cotton" | Line with MSP |
| Distribution | "distribution across crops" | Bar |
| Correlation | "rainfall vs arrivals" | Scatter |

---

## Project Structure

```
agriTech/
├── Dataset/
│   ├── *.csv, *.json, *.xlsx          # Raw data
│   ├── clean/
│   │   ├── *.csv                      # Cleaned data
│   │   ├── DATA_DICTIONARY.md         # Column definitions
│   │   └── DATA_QUALITY_REPORT.md     # Cleaning audit
│   └── agritech_analytics.db          # Analytics database
├── src/
│   ├── data_engineering/
│   │   └── clean_data.py              # Data cleaning pipeline
│   ├── analytics/
│   │   ├── build_model.py             # Database builder
│   │   └── validate_metrics.py        # View validation
│   └── dashboard/
│       ├── app.py                     # Main dashboard
│       ├── charts.py                  # Chart functions
│       ├── components.py              # UI components
│       ├── agent.py                   # AI query engine
│       ├── queries.py                 # Data access layer
│       └── styles.css                 # Theme styles
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data Engineering | Python, Pandas, NumPy |
| Database | SQLite with indexed views |
| Dashboard | Streamlit, Plotly |
| AI Agent | Pattern matching with optional LLM integration |
| Styling | Custom CSS (Newsprint theme) |

