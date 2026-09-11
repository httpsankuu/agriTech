# Phase 1: Data Exploration and Cleaning (Data Rescue)

## Context
This phase focuses on taking the messy datasets provided in the `Dataset` folder and producing clean, standardized, query-ready datasets in a new `Dataset/clean` folder. It also includes generating a data dictionary.

## Requirements
- Missing Values & Duplicates intelligently handled.
- Standardizations applied to dates, quantities, languages, currency strings, and units (temperature, distance, rainfall).
- Fully reproducible script `src/data_engineering/clean_data.py`.
- Generates `DATA_DICTIONARY.md`.

## Execution Plan

### Task 1: Tracer Slice (Mandi Master Data Rescue) [checkpoint:decision]
**Description**: Start by rescuing the central entity table (`track3_mandi_master.csv`). Standardize the `mandi_id` format and handle missing districts.
**Files to create/modify**:
- `src/data_engineering/clean_data.py`
- `Dataset/clean/track3_mandi_master_clean.csv` (Output)
**Steps**:
1. Initialize the Python project and `src/data_engineering/clean_data.py`.
2. Load `track3_mandi_master.csv`.
3. Standardize `mandi_id` to a single uniform format (e.g., `MANDI-XXX`).
4. Fill missing districts or handle inconsistent types.
5. Create `Dataset/clean/` directory and export the clean master CSV.
6. Verify the script runs end-to-end and creates the clean dataset.

### Task 2: Arrival & Price Data Rescue
**Description**: Clean the `mandi_arrivals` and `price_and_msp` datasets.
**Files to create/modify**:
- `src/data_engineering/clean_data.py`
- `Dataset/clean/track3_mandi_arrivals_clean.csv` (Output)
- `Dataset/clean/track3_price_and_msp_clean.csv` (Output)
**Steps**:
1. Add logic to load `track3_mandi_arrivals.csv` and `track3_price_and_msp.json`.
2. Standardize `mandi_id` in both tables to match the master format.
3. Standardize crop names to English equivalents (mapping "गेहूं", "Gehun" to "Wheat").
4. Convert mixed units (KG, Tonnes) to Quintals in arrivals (1 Tonne = 10 Qtl, 1 Qtl = 100 KG).
5. Parse and clean date columns.
6. Clean price strings (remove ₹, Rs., INR, commas) and convert to numeric.
7. Output clean CSVs.

### Task 3: Logistics & Weather Data Rescue
**Description**: Clean `transport_logistics` and `weather_sensors` data.
**Files to create/modify**:
- `src/data_engineering/clean_data.py`
- `Dataset/clean/track3_transport_logistics_clean.csv` (Output)
- `Dataset/clean/track3_weather_sensors_clean.csv` (Output)
**Steps**:
1. Load `track3_transport_logistics.csv` and `track3_weather_sensors.xlsx`.
2. Standardize `mandi_id` formats.
3. Logistics: Handle negative transit times (convert to positive or flag as errors), convert Miles to KM, standardize vehicle registration numbers.
4. Weather: Convert UTC timestamps to IST, convert Fahrenheit to Celsius, convert inches to mm.
5. Export clean datasets.

### Task 4: Documentation (Data Dictionary)
**Description**: Write a README.md and DATA_DICTIONARY.md.
**Files to create/modify**:
- `Dataset/clean/DATA_DICTIONARY.md`
- `README.md`
**Steps**:
1. Document every field in the 5 clean datasets in `DATA_DICTIONARY.md`.
2. Write `README.md` explaining how to run the data cleaning script and detailing the steps taken to fix the data.
