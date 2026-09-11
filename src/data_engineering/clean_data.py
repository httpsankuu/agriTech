import os
import pandas as pd
import numpy as np
import re
import json

def clean_mandi_id(m_id):
    if pd.isna(m_id):
        return m_id
    m_id_str = str(m_id)
    digits = re.sub(r'\D', '', m_id_str)
    if digits:
        return f"MANDI-{int(digits):03d}"
    return m_id_str

def clean_mandi_master(input_path, output_path):
    print(f"Cleaning Mandi Master...")
    df = pd.read_csv(input_path)
    df['mandi_id'] = df['mandi_id'].apply(clean_mandi_id)
    df['district'] = df['district'].str.title().fillna('Unknown')
    df['state'] = df['state'].str.title().fillna('Unknown')
    df['mandi_type'] = df['mandi_type'].str.upper().replace({'PRIVATE': 'Private', 'DIRECT': 'Direct'})
    df['mandi_type'] = df['mandi_type'].fillna('Unknown')
    df['total_area_acres'] = pd.to_numeric(df['total_area_acres'], errors='coerce')
    df.to_csv(output_path, index=False)

def standardize_crop_name(name):
    if pd.isna(name):
        return name
    name = str(name).strip().lower()
    MAPPING = {
        'गेहूं': 'Wheat', 'gehun': 'Wheat', 'kanak': 'Wheat', 'wheat': 'Wheat',
        'maize': 'Maize', 'corn': 'Maize', 'मक्का': 'Maize', 'makka': 'Maize', 'makki': 'Maize',
        'ganne': 'Sugarcane', 'sugarcane': 'Sugarcane', 'ganna': 'Sugarcane', 'गन्ना': 'Sugarcane',
        'kapas': 'Cotton', 'cotton': 'Cotton', 'कपास': 'Cotton', 'narma': 'Cotton',
        'sarso': 'Mustard', 'sarson': 'Mustard', 'mustard': 'Mustard', 'सरसों': 'Mustard',
        'basmati': 'Rice', 'paddy': 'Rice', 'chawal': 'Rice', 'धान': 'Rice', 'चावल': 'Rice', 'rice': 'Rice', 'dhaan': 'Rice'
    }
    return MAPPING.get(name, name.title())

def parse_quantity(row):
    qty = row['arrival_quantity']
    unit = row['unit']
    
    qty_str = str(qty).lower().strip()
    
    match = re.match(r'([-\d.]+)\s*([a-z]+)?', qty_str)
    num = np.nan
    u = unit
    if match:
        num = float(match.group(1))
        if match.group(2):
            u = match.group(2)
            
    if pd.isna(u):
        u = ''
    u_str = str(u).lower().strip()
    
    if u_str in ['qtl', 'q', 'quintals', 'quintal']:
        multiplier = 1.0
    elif u_str in ['t', 'tonnes', 'tonne', 'mt']:
        multiplier = 10.0
    elif u_str in ['kg', 'kgs', 'kilo']:
        multiplier = 0.01
    else:
        multiplier = 1.0
        
    return abs(num) * multiplier

def clean_arrivals(input_path, output_path):
    print(f"Cleaning Arrivals...")
    df = pd.read_csv(input_path)
    df['mandi_id'] = df['mandi_id'].apply(clean_mandi_id)
    df['crop_name'] = df['crop_name'].apply(standardize_crop_name)
    df['arrival_quantity_qtl'] = df.apply(parse_quantity, axis=1)
    df['date'] = pd.to_datetime(df['date'], errors='coerce', format='mixed')
    
    df = df.drop(columns=['arrival_quantity', 'unit'])
    df.to_csv(output_path, index=False)

def clean_price(price_val):
    if pd.isna(price_val) or price_val == "":
        return np.nan
    p_str = str(price_val)
    p_clean = re.sub(r'[^\d.]', '', p_str)
    try:
        return float(p_clean)
    except:
        return np.nan

def clean_price_msp(input_path, output_path):
    print("Cleaning Prices...")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['mandi_id'] = df['mandi_id'].apply(clean_mandi_id)
    df['crop_name'] = df['crop_name'].apply(standardize_crop_name)
    df['min_price'] = df['min_price'].apply(clean_price)
    df['max_price'] = df['max_price'].apply(clean_price)
    df['modal_price'] = df['modal_price'].apply(clean_price)
    df['msp'] = df['msp'].apply(clean_price)
    df['date'] = pd.to_datetime(df['date'], errors='coerce', format='mixed')
    df.to_csv(output_path, index=False)

def clean_logistics(input_path, output_path):
    print("Cleaning Logistics...")
    df = pd.read_csv(input_path)
    if 'mandi_id' in df.columns:
        df['mandi_id'] = df['mandi_id'].apply(clean_mandi_id)
    if 'transit_hours' in df.columns:
        df['transit_hours'] = pd.to_numeric(df['transit_hours'], errors='coerce').abs()
    if 'distance' in df.columns and 'distance_unit' in df.columns:
        def convert_dist(row):
            d = pd.to_numeric(row['distance'], errors='coerce')
            u = str(row['distance_unit']).lower()
            if 'mile' in u:
                return d * 1.60934
            return d
        df['distance_km'] = df.apply(convert_dist, axis=1)
        df = df.drop(columns=['distance', 'distance_unit'])
    if 'vehicle_no' in df.columns:
        df['vehicle_no'] = df['vehicle_no'].str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)
    df.to_csv(output_path, index=False)

def clean_weather(input_path, output_path):
    print("Cleaning Weather...")
    df = pd.read_excel(input_path)
    
    if 'timestamp' in df.columns:
        # Some are strings like '2026-04-06 00:00:00 UTC', some are aware datetime.
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', utc=True)
        # Convert to IST (Asia/Kolkata)
        df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
        
    if 'temperature' in df.columns and 'temp_unit' in df.columns:
        def conv_temp(row):
            t = pd.to_numeric(row['temperature'], errors='coerce')
            u = str(row['temp_unit']).lower()
            if 'f' in u or 'fahrenheit' in u:
                return (t - 32) * 5.0/9.0
            return t
        df['temperature_c'] = df.apply(conv_temp, axis=1)
        df = df.drop(columns=['temperature', 'temp_unit'])
    
    if 'rainfall' in df.columns and 'rain_unit' in df.columns:
        def conv_rain(row):
            r = pd.to_numeric(row['rainfall'], errors='coerce')
            u = str(row['rain_unit']).lower()
            if 'inch' in u:
                return r * 25.4
            return r
        df['rainfall_mm'] = df.apply(conv_rain, axis=1)
        df = df.drop(columns=['rainfall', 'rain_unit'])

    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, "Dataset")
    CLEAN_DIR = os.path.join(DATA_DIR, "clean")
    
    os.makedirs(CLEAN_DIR, exist_ok=True)
    
    clean_mandi_master(
        os.path.join(DATA_DIR, "track3_mandi_master.csv"),
        os.path.join(CLEAN_DIR, "track3_mandi_master_clean.csv")
    )
    clean_arrivals(
        os.path.join(DATA_DIR, "track3_mandi_arrivals.csv"),
        os.path.join(CLEAN_DIR, "track3_mandi_arrivals_clean.csv")
    )
    clean_price_msp(
        os.path.join(DATA_DIR, "track3_price_and_msp.json"),
        os.path.join(CLEAN_DIR, "track3_price_and_msp_clean.csv")
    )
    clean_logistics(
        os.path.join(DATA_DIR, "track3_transport_logistics.csv"),
        os.path.join(CLEAN_DIR, "track3_transport_logistics_clean.csv")
    )
    clean_weather(
        os.path.join(DATA_DIR, "track3_weather_sensors.xlsx"),
        os.path.join(CLEAN_DIR, "track3_weather_sensors_clean.csv")
    )
