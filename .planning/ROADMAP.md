# Roadmap

## Phase 1: Data Exploration and Cleaning (Data Rescue)
- [ ] Inspect raw datasets (crop arrivals, prices, MSP, weather).
- [ ] Implement data standardizers (unit conversion, language mapping, timezone fixes).
- [ ] Handle missing values and duplicate records.
- [ ] Save cleaned datasets and write data dictionary.

## Phase 2: Analytics Layer and Data Modeling
- [ ] Define and calculate core metrics.
- [ ] Build a structured data model (e.g., SQL tables or clean Pandas DataFrames).
- [ ] Implement data validation checks.

## Phase 3: Executive Dashboard
- [ ] Initialize Streamlit application.
- [ ] Build KPI cards (Total Volume, Price vs MSP).
- [ ] Build interactive charts (Arrival trends, Weather correlations).
- [ ] Add filters for Crop, Mandi, and Date ranges.

## Phase 4: Agentic Graph AI Integration
- [ ] Integrate LLM (LangChain/LlamaIndex).
- [ ] Build text-to-SQL or text-to-Pandas engine for chart generation.
- [ ] Implement logic to choose correct chart type.
- [ ] Add Agent UI to the Streamlit dashboard.
