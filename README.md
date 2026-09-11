# AgriTech - Mandi-to-Market Supply Chain Optimizer

This project aims to build a data-driven platform for the State Agriculture Board to monitor daily crop arrivals at local Mandis, track prices against the Minimum Support Price (MSP), and correlate these metrics with weather data.

## Phase 1: Data Rescue & Engineering

We have completed the data rescue phase. The raw, chaotic datasets have been cleaned, standardized, and saved into query-ready formats.

### How to Run the Data Pipeline
To reproduce the data cleaning process, execute the Python script located in the `src/data_engineering/` folder from the root of the repository:

```bash
python src/data_engineering/clean_data.py
```

### Data Rescue Steps Taken
1. **Mandi Master Data**:
   - Standardized `mandi_id` format to `MANDI-XXX`.
   - Title Cased `district` and `state`. Replaced nulls with 'Unknown'.
   - Standardized `mandi_type` to `APMC`, `Private`, `Direct`, etc.

2. **Crop Arrivals**:
   - Mapped multilingual and messy crop names (e.g., 'गेहूं', 'Gehun', 'Kanak') to English canonical names ('Wheat').
   - Parsed mixed quantities and units (Tonnes, KG, Quintals) and converted everything to Quintals (`arrival_quantity_qtl`).
   - Parsed dates robustly to YYYY-MM-DD.

3. **Prices and MSP**:
   - Removed all currency symbols (₹, Rs., INR) and commas from price columns.
   - Cast prices to numeric formats.

4. **Logistics**:
   - Fixed impossible negative transit times by taking absolute values.
   - Standardized distance to Kilometers (`distance_km`).
   - Standardized vehicle registration numbers by stripping special characters.

5. **Weather Sensors**:
   - Converted UTC timestamps to Indian Standard Time (IST).
   - Converted Fahrenheit temperatures to Celsius (`temperature_c`).
   - Converted rainfall in inches to millimeters (`rainfall_mm`).

### Project Structure
- `Dataset/`: Contains the original raw dataset provided by the datathon.
- `Dataset/clean/`: Contains the clean, standardized CSV files ready for the Analytics Layer.
  - See `Dataset/clean/DATA_DICTIONARY.md` for column definitions.
- `src/data_engineering/clean_data.py`: The reproducible data rescue pipeline.
