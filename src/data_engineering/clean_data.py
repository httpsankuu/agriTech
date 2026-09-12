import os
import pandas as pd
import numpy as np
import re
import json
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

report_data = {}

def init_report(name, raw_count):
    report_data[name] = {
        'raw_rows': raw_count,
        'clean_rows': 0,
        'removed_rows': 0,
        'percentage_removed': 0.0,
        'duplicate_count_detected': 0,
        'missing_before': {},
        'missing_after': {},
        'invalid_counts': {},
        'standardized_fields': [],
        'recovered_values': {},
        'unresolved_missing': {},
        'important_decisions': [],
        'justification': ""
    }

def clean_mandi_id(m_id):
    if pd.isna(m_id):
        return m_id
    m_id_str = str(m_id)
    digits = re.sub(r'\D', '', m_id_str)
    if digits:
        return f"MANDI-{int(digits):03d}"
    return m_id_str

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

def clean_price(price_val):
    if pd.isna(price_val) or price_val == "":
        return np.nan
    p_str = str(price_val)
    p_clean = re.sub(r'[^\d.]', '', p_str)
    try:
        return float(p_clean)
    except (ValueError, TypeError):
        return np.nan

def clean_mandi_master(input_path, output_path):
    print("Cleaning Mandi Master...")
    df = pd.read_csv(input_path)
    ds_name = 'Mandi Master'
    raw_count = len(df)
    init_report(ds_name, raw_count)
    report_data[ds_name]['missing_before'] = df.isnull().sum().to_dict()
    
    dup_count = df.duplicated().sum()
    report_data[ds_name]['duplicate_count_detected'] = int(dup_count)
    if dup_count > 0:
        df = df.drop_duplicates()
        report_data[ds_name]['removed_rows'] = int(dup_count)
        report_data[ds_name]['justification'] = f"Removed {dup_count} exact duplicate rows as they were confirmed to be accidental redundant copies."
        report_data[ds_name]['important_decisions'].append("Applied drop_duplicates to remove exact row matches.")
    
    df['mandi_id'] = df['mandi_id'].apply(clean_mandi_id)
    report_data[ds_name]['standardized_fields'].append('mandi_id')
    
    df['district'] = df['district'].str.title()
    df['state'] = df['state'].str.title()
    df['mandi_type'] = df['mandi_type'].str.upper().replace({'PRIVATE': 'Private', 'DIRECT': 'Direct'})
    report_data[ds_name]['standardized_fields'].extend(['district', 'state', 'mandi_type'])
    df['total_area_acres'] = pd.to_numeric(df['total_area_acres'], errors='coerce')
    
    # Validations
    assert df.duplicated().sum() == 0, "Validation Failed: Exact duplicates remain in Mandi Master."
    assert df['mandi_id'].dropna().duplicated().sum() == 0, "Validation Failed: mandi_id is not unique in Mandi Master."
    assert raw_count == report_data[ds_name]['raw_rows'], "Validation Failed: Raw count changed."
    
    report_data[ds_name]['missing_after'] = df.isnull().sum().to_dict()
    report_data[ds_name]['unresolved_missing'] = {k: v for k, v in df.isnull().sum().to_dict().items() if v > 0}
    report_data[ds_name]['important_decisions'].append("Retained NULL values for district, state, and mandi_type instead of filling with 'Unknown'.")
    
    report_data[ds_name]['clean_rows'] = len(df)
    report_data[ds_name]['percentage_removed'] = (report_data[ds_name]['removed_rows'] / raw_count) * 100
    df.to_csv(output_path, index=False)
    
    return df

def clean_arrivals(input_path, output_path):
    print("Cleaning Arrivals...")
    df = pd.read_csv(input_path)
    ds_name = 'Mandi Arrivals'
    raw_count = len(df)
    init_report(ds_name, raw_count)
    report_data[ds_name]['missing_before'] = df.isnull().sum().to_dict()
    
    dup_count = df.duplicated().sum()
    report_data[ds_name]['duplicate_count_detected'] = int(dup_count)
    if dup_count > 0:
        df = df.drop_duplicates()
        report_data[ds_name]['removed_rows'] = int(dup_count)
        report_data[ds_name]['justification'] = f"Removed {dup_count} exact duplicate rows as they were confirmed to be accidental redundant copies."
        report_data[ds_name]['important_decisions'].append("Applied drop_duplicates to remove exact row matches.")
    
    df['mandi_id'] = df['mandi_id'].apply(clean_mandi_id)
    df['crop_name'] = df['crop_name'].apply(standardize_crop_name)
    report_data[ds_name]['standardized_fields'].extend(['mandi_id', 'crop_name'])
    
    df['arrival_quantity_qtl'] = df.apply(parse_quantity, axis=1)
    report_data[ds_name]['standardized_fields'].append('arrival_quantity_qtl')
    report_data[ds_name]['important_decisions'].append("Preserved original arrival_quantity and unit columns. Added standardized arrival_quantity_qtl.")
    
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Validations
    assert df.duplicated().sum() == 0, "Validation Failed: Exact duplicates remain in Mandi Arrivals."
    if 'arrival_id' in df.columns:
        assert df['arrival_id'].dropna().duplicated().sum() == 0, "Validation Failed: arrival_id is not unique in Mandi Arrivals."
    assert raw_count == report_data[ds_name]['raw_rows'], "Validation Failed: Raw count changed."
    
    report_data[ds_name]['missing_after'] = df.isnull().sum().to_dict()
    report_data[ds_name]['unresolved_missing'] = {k: v for k, v in df.isnull().sum().to_dict().items() if v > 0}
    
    report_data[ds_name]['clean_rows'] = len(df)
    report_data[ds_name]['percentage_removed'] = (report_data[ds_name]['removed_rows'] / raw_count) * 100
    df.to_csv(output_path, index=False)

def clean_price_msp(input_path, output_path, master_df):
    print("Cleaning Prices...")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    ds_name = 'Price and MSP'
    raw_count = len(df)
    init_report(ds_name, raw_count)
    report_data[ds_name]['missing_before'] = df.isnull().sum().to_dict()
    
    dup_count = df.duplicated().sum()
    report_data[ds_name]['duplicate_count_detected'] = int(dup_count)
    if dup_count > 0:
        df = df.drop_duplicates()
        report_data[ds_name]['removed_rows'] = int(dup_count)
    
    df['mandi_id'] = df['mandi_id'].apply(clean_mandi_id)
    df['crop_name'] = df['crop_name'].apply(standardize_crop_name)
    
    master_lookup = master_df.dropna(subset=['mandi_id', 'district']).groupby('mandi_id').first()['district'].to_dict()
    missing_dist_before = df['district'].isnull().sum()
    df['district'] = df.apply(lambda row: master_lookup.get(row['mandi_id'], row['district']) if pd.isna(row['district']) else row['district'], axis=1)
    missing_dist_after = df['district'].isnull().sum()
    recovered_dist = missing_dist_before - missing_dist_after
    
    report_data[ds_name]['recovered_values']['district'] = int(recovered_dist)
    report_data[ds_name]['important_decisions'].append(f"Recovered {recovered_dist} missing district values using mandi_master.")
    
    df['min_price'] = df['min_price'].apply(clean_price)
    df['max_price'] = df['max_price'].apply(clean_price)
    df['modal_price'] = df['modal_price'].apply(clean_price)
    df['msp'] = df['msp'].apply(clean_price)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    assert df.duplicated().sum() == 0, "Validation Failed: Exact duplicates remain in Price."
    assert raw_count == report_data[ds_name]['raw_rows'], "Validation Failed: Raw count changed."
    
    report_data[ds_name]['standardized_fields'].extend(['mandi_id', 'crop_name', 'min_price', 'max_price', 'modal_price', 'msp'])
    report_data[ds_name]['missing_after'] = df.isnull().sum().to_dict()
    report_data[ds_name]['unresolved_missing'] = {k: v for k, v in df.isnull().sum().to_dict().items() if v > 0}
    
    report_data[ds_name]['clean_rows'] = len(df)
    report_data[ds_name]['percentage_removed'] = (report_data[ds_name]['removed_rows'] / raw_count) * 100
    df.to_csv(output_path, index=False)

def clean_logistics(input_path, output_path):
    print("Cleaning Logistics...")
    df = pd.read_csv(input_path)
    ds_name = 'Transport Logistics'
    raw_count = len(df)
    init_report(ds_name, raw_count)
    report_data[ds_name]['missing_before'] = df.isnull().sum().to_dict()
    
    dup_count = df.duplicated().sum()
    report_data[ds_name]['duplicate_count_detected'] = int(dup_count)
    if dup_count > 0:
        df = df.drop_duplicates()
        report_data[ds_name]['removed_rows'] = int(dup_count)
        report_data[ds_name]['justification'] = f"Removed {dup_count} exact duplicate rows as they were confirmed to be accidental redundant copies."
        report_data[ds_name]['important_decisions'].append("Applied drop_duplicates to remove exact row matches.")
    
    if 'mandi_id' in df.columns:
        df['mandi_id'] = df['mandi_id'].apply(clean_mandi_id)
        
    if 'transit_hours' in df.columns:
        df['transit_hours'] = pd.to_numeric(df['transit_hours'], errors='coerce')
        df['transit_time_invalid'] = df['transit_hours'] < 0
        invalid_count = df['transit_time_invalid'].sum()
        report_data[ds_name]['invalid_counts']['transit_hours_negative'] = int(invalid_count)
        
        df['transit_hours_clean'] = df['transit_hours'].apply(lambda x: np.nan if x < 0 else x)
        report_data[ds_name]['important_decisions'].append(f"Identified {invalid_count} negative transit_hours. Kept original column, added transit_time_invalid flag, and created transit_hours_clean with negative values set to NaN.")
        report_data[ds_name]['standardized_fields'].append('transit_hours_clean')

    if 'distance' in df.columns and 'distance_unit' in df.columns:
        def convert_dist(row):
            d = pd.to_numeric(row['distance'], errors='coerce')
            u = str(row['distance_unit']).lower()
            if 'mile' in u:
                return d * 1.60934
            return d
        df['distance_km'] = df.apply(convert_dist, axis=1)
        report_data[ds_name]['standardized_fields'].append('distance_km')
        report_data[ds_name]['important_decisions'].append("Preserved original distance and distance_unit columns. Added standardized distance_km.")

    if 'vehicle_no' in df.columns:
        df['vehicle_no'] = df['vehicle_no'].str.upper().str.replace(r'[^A-Z0-9]', '', regex=True)
        report_data[ds_name]['standardized_fields'].append('vehicle_no')

    assert df.duplicated().sum() == 0, "Validation Failed: Exact duplicates remain in Transport."
    if 'trip_id' in df.columns:
        assert df['trip_id'].dropna().duplicated().sum() == 0, "Validation Failed: trip_id is not unique in Transport Logistics."
    assert raw_count == report_data[ds_name]['raw_rows'], "Validation Failed: Raw count changed."

    report_data[ds_name]['missing_after'] = df.isnull().sum().to_dict()
    report_data[ds_name]['unresolved_missing'] = {k: v for k, v in df.isnull().sum().to_dict().items() if v > 0}
    
    report_data[ds_name]['clean_rows'] = len(df)
    report_data[ds_name]['percentage_removed'] = (report_data[ds_name]['removed_rows'] / raw_count) * 100
    df.to_csv(output_path, index=False)

def clean_weather(input_path, output_path):
    print("Cleaning Weather...")
    df = pd.read_excel(input_path)
    ds_name = 'Weather Sensors'
    raw_count = len(df)
    init_report(ds_name, raw_count)
    report_data[ds_name]['missing_before'] = df.isnull().sum().to_dict()
    
    dup_count = df.duplicated().sum()
    report_data[ds_name]['duplicate_count_detected'] = int(dup_count)
    if dup_count > 0:
        df = df.drop_duplicates()
        report_data[ds_name]['removed_rows'] = int(dup_count)
        
    if 'timestamp' in df.columns:
        df['timestamp'] = df['timestamp'].astype(str).str.replace(' IST', '').str.replace(' UTC', '').replace('nan', '')
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
    if 'temperature' in df.columns and 'temp_unit' in df.columns:
        def conv_temp(row):
            t = pd.to_numeric(row['temperature'], errors='coerce')
            u = str(row['temp_unit']).lower()
            if 'f' in u or 'fahrenheit' in u:
                return (t - 32) * 5.0/9.0
            return t
        df['temperature_c'] = df.apply(conv_temp, axis=1)
        report_data[ds_name]['standardized_fields'].append('temperature_c')
        report_data[ds_name]['important_decisions'].append("Preserved original temperature and temp_unit. Added standardized temperature_c.")
    
    if 'rainfall' in df.columns and 'rain_unit' in df.columns:
        def conv_rain(row):
            r = pd.to_numeric(row['rainfall'], errors='coerce')
            u = str(row['rain_unit']).lower()
            if 'inch' in u:
                return r * 25.4
            return r
        df['rainfall_mm'] = df.apply(conv_rain, axis=1)
        report_data[ds_name]['standardized_fields'].append('rainfall_mm')
        report_data[ds_name]['important_decisions'].append("Preserved original rainfall and rain_unit. Added standardized rainfall_mm.")

    assert df.duplicated().sum() == 0, "Validation Failed: Exact duplicates remain in Weather."
    assert raw_count == report_data[ds_name]['raw_rows'], "Validation Failed: Raw count changed."

    report_data[ds_name]['missing_after'] = df.isnull().sum().to_dict()
    report_data[ds_name]['unresolved_missing'] = {k: v for k, v in df.isnull().sum().to_dict().items() if v > 0}
    
    report_data[ds_name]['clean_rows'] = len(df)
    report_data[ds_name]['percentage_removed'] = (report_data[ds_name]['removed_rows'] / raw_count) * 100
    df.to_csv(output_path, index=False)

def generate_report(output_path):
    with open(output_path, 'w') as f:
        f.write("# Data Quality & Validation Report\n\n")
        for ds, data in report_data.items():
            f.write(f"## {ds}\n")
            f.write(f"- **Raw Row Count:** {data['raw_rows']}\n")
            f.write(f"- **Duplicate Rows Detected:** {data['duplicate_count_detected']}\n")
            f.write(f"- **Duplicate Rows Removed:** {data['removed_rows']}\n")
            f.write(f"- **Final Cleaned Row Count:** {data['clean_rows']}\n")
            f.write(f"- **Percentage of Rows Removed:** {data['percentage_removed']:.2f}%\n")
            
            if data['justification']:
                f.write(f"- **Justification:** {data['justification']}\n")
            
            f.write("\n### Missing Values Before\n")
            for col, count in data['missing_before'].items():
                if count > 0: f.write(f"- {col}: {count}\n")
                
            f.write("\n### Missing Values After\n")
            for col, count in data['missing_after'].items():
                if count > 0: f.write(f"- {col}: {count}\n")
                
            if data['recovered_values']:
                f.write("\n### Recovered Values (Master Joins)\n")
                for k, v in data['recovered_values'].items():
                    f.write(f"- {k}: {v} values recovered\n")
                    
            if data['invalid_counts']:
                f.write("\n### Invalid Values Detected\n")
                for k, v in data['invalid_counts'].items():
                    f.write(f"- {k}: {v}\n")
                    
            f.write("\n### Important Cleaning Decisions\n")
            for dec in data['important_decisions']:
                f.write(f"- {dec}\n")
            f.write("\n---\n\n")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, "Dataset")
    CLEAN_DIR = os.path.join(DATA_DIR, "clean")
    
    os.makedirs(CLEAN_DIR, exist_ok=True)
    
    master_df = clean_mandi_master(
        os.path.join(DATA_DIR, "track3_mandi_master.csv"),
        os.path.join(CLEAN_DIR, "track3_mandi_master_clean.csv")
    )
    clean_arrivals(
        os.path.join(DATA_DIR, "track3_mandi_arrivals.csv"),
        os.path.join(CLEAN_DIR, "track3_mandi_arrivals_clean.csv")
    )
    clean_price_msp(
        os.path.join(DATA_DIR, "track3_price_and_msp.json"),
        os.path.join(CLEAN_DIR, "track3_price_and_msp_clean.csv"),
        master_df
    )
    clean_logistics(
        os.path.join(DATA_DIR, "track3_transport_logistics.csv"),
        os.path.join(CLEAN_DIR, "track3_transport_logistics_clean.csv")
    )
    clean_weather(
        os.path.join(DATA_DIR, "track3_weather_sensors.xlsx"),
        os.path.join(CLEAN_DIR, "track3_weather_sensors_clean.csv")
    )
    
    report_path = os.path.join(CLEAN_DIR, "DATA_QUALITY_REPORT.md")
    generate_report(report_path)
    print(f"Data Quality Report generated at {report_path}")
