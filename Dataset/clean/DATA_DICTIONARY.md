# Data Dictionary

## 1. track3_mandi_master_clean.csv
- **mandi_id**: Standardized identifier for the Mandi (e.g., MANDI-001).
- **mandi_name**: Name of the Mandi.
- **district**: District where the Mandi is located (Title Case, 'Unknown' if missing).
- **state**: State where the Mandi is located (Title Case, 'Unknown' if missing).
- **mandi_type**: Type of Mandi ('Private', 'Direct', 'APMC', or 'Unknown').
- **total_area_acres**: Total area of the Mandi in acres (numeric).

## 2. track3_mandi_arrivals_clean.csv
- **arrival_id**: Unique identifier for the arrival record.
- **date**: Date of arrival (YYYY-MM-DD format).
- **mandi_id**: Standardized Mandi ID (e.g., MANDI-001).
- **crop_name**: Standardized English canonical name of the crop (e.g., Wheat, Maize, Cotton, Mustard).
- **variety**: Crop variety.
- **farmer_count**: Number of farmers involved.
- **arrival_quantity_qtl**: Absolute quantity of arrivals standardized in Quintals (Qtl). All previous units (Tonne, KG) have been converted to Quintals.

## 3. track3_price_and_msp_clean.csv
- **record_id**: Unique identifier for the price record.
- **date**: Date of the price record (YYYY-MM-DD format).
- **mandi_id**: Standardized Mandi ID (e.g., MANDI-001).
- **district**: District name.
- **crop_name**: Standardized English canonical name of the crop.
- **min_price**: Minimum price in numeric format (currency symbols and commas removed).
- **max_price**: Maximum price in numeric format.
- **modal_price**: Modal (average/most frequent) price in numeric format.
- **msp**: Minimum Support Price (MSP) in numeric format.

## 4. track3_transport_logistics_clean.csv
- **trip_id**: Unique identifier for the transport trip.
- **mandi_id**: Standardized Mandi ID.
- **destination_warehouse**: Destination warehouse name.
- **departure_time**: Departure timestamp.
- **arrival_time**: Arrival timestamp.
- **transit_hours**: Original transit time in hours. Negative values are retained as invalid records and excluded from valid transit-time calculations.
- **transit_hours_clean**: Clean transit time in hours. Invalid negative transit times are set to null and excluded from valid transit-time calculations.
- **vehicle_no**: Standardized vehicle registration number (alphanumeric only, uppercase).
- **driver_id**: Driver identifier.
- **distance_km**: Distance converted strictly to Kilometers (miles were converted by multiplying by 1.60934).

## 5. track3_weather_sensors_clean.csv
- **sensor_id**: Unique identifier for the weather sensor.
- **timestamp**: Timestamp of the reading, standardized to Indian Standard Time (IST) without timezone offset (naive datetime).
- **humidity_percent**: Humidity percentage.
- **temperature_c**: Temperature converted strictly to Celsius (Fahrenheit values converted).
- **rainfall_mm**: Rainfall converted strictly to millimeters (inches multiplied by 25.4).
