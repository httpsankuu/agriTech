# Requirements

## 1. Data Engineering & Rescue
- **Missing Values & Duplicates**: Intelligently impute or fix missing data without losing massive amounts of records.
- **Standardization**:
  - Translate/map Hindi and English crop names to a unified naming convention.
  - Convert mixed quantity units (e.g., KGs to Quintals or vice versa) to a standard unit.
  - Normalize timezone mismatches in weather sensor logs.
- **Reproducibility**: The data cleaning script/pipeline must be fully reproducible from top to bottom.

## 2. Analytics Layer
- **Metrics**: Daily arrival volumes, average prices, MSP comparison (price deviation), weather impact correlations.
- **Data Model**: Clean, structured, query-ready tables (e.g., Fact_Arrivals, Dim_Mandi, Dim_Crop, Fact_Weather).

## 3. Executive Dashboard
- **Interactivity & UX**: Clean layout, actionable filters (Mandi, Crop, Date range).
- **Core KPIs**: Total Arrivals, Average Price vs MSP, Weather anomaly flags.
- **Storytelling**: Clear visual narrative answering the core business problem (tracking arrivals, prices, and weather).

## 4. Excellence & AI Bonus
- **Code Elegance**: Modular Python functions, clear pipeline structure, well-documented code (Data Dictionary, README.md).
- **Agentic Graph AI**:
  - Understand natural language questions.
  - Automatically select the correct chart type (Bar vs Line vs Scatter).
  - Provide a text summary alongside the generated graph.
