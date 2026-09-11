import sqlite3
import pandas as pd
import os

def build_model():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, "Dataset")
    CLEAN_DIR = os.path.join(DATA_DIR, "clean")
    DB_PATH = os.path.join(DATA_DIR, "agritech_analytics.db")
    
    print(f"Connecting to database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    
    # Task 1 & 2: Ingest Tables
    tables_to_ingest = {
        'dim_mandi': 'track3_mandi_master_clean.csv',
        'fact_arrivals': 'track3_mandi_arrivals_clean.csv',
        'fact_prices': 'track3_price_and_msp_clean.csv',
        'fact_logistics': 'track3_transport_logistics_clean.csv',
        'fact_weather': 'track3_weather_sensors_clean.csv'
    }
    
    for table_name, file_name in tables_to_ingest.items():
        file_path = os.path.join(CLEAN_DIR, file_name)
        print(f"Ingesting {file_name} into {table_name}...")
        df = pd.read_csv(file_path)
        
        # Add helper columns for faster joins
        if 'mandi_id' in df.columns and table_name != 'dim_mandi':
            df['mandi_num'] = pd.to_numeric(df['mandi_id'].str.replace(r'\D', '', regex=True), errors='coerce')
        if 'sensor_id' in df.columns:
            df['mandi_num'] = pd.to_numeric(df['sensor_id'].str.replace(r'\D', '', regex=True), errors='coerce')
        if 'date' in df.columns:
            df['date_str'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        if 'timestamp' in df.columns:
            df['date_str'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')
            
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
    # Task 3: Create Analytical Views
    print("Creating views and indexes...")
    
    cursor = conn.cursor()
    
    # Add indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_arr_date ON fact_arrivals(date_str)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_arr_mandi ON fact_arrivals(mandi_num)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_wthr_date ON fact_weather(date_str)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_wthr_mandi ON fact_weather(mandi_num)")
    
    # View 1: Price vs MSP
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS vw_price_vs_msp AS
        SELECT 
            p.date,
            p.mandi_id,
            m.mandi_name,
            m.district,
            p.crop_name,
            p.modal_price,
            p.msp,
            (p.modal_price - p.msp) AS price_deviation,
            CASE WHEN p.modal_price < p.msp THEN 1 ELSE 0 END AS is_price_crash
        FROM fact_prices p
        LEFT JOIN dim_mandi m ON p.mandi_id = m.mandi_id
    """)
    
    # View 2: Transit Performance
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS vw_transit_performance AS
        SELECT 
            mandi_id,
            destination_warehouse,
            AVG(transit_hours) AS avg_transit_hours,
            AVG(distance_km) AS avg_distance_km,
            COUNT(trip_id) AS total_trips
        FROM fact_logistics
        GROUP BY mandi_id, destination_warehouse
    """)
    
    # View 3: Crop Summary
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS vw_crop_summary AS
        SELECT 
            a.date,
            a.mandi_id,
            m.mandi_name,
            a.crop_name,
            SUM(a.arrival_quantity_qtl) AS total_arrival_qtl,
            SUM(a.farmer_count) AS total_farmers
        FROM fact_arrivals a
        LEFT JOIN dim_mandi m ON a.mandi_id = m.mandi_id
        GROUP BY a.date, a.mandi_id, m.mandi_name, a.crop_name
    """)
    
    # View 4: Mandi Daily Summary (Joining Arrivals and Weather)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS vw_mandi_daily_summary AS
        SELECT 
            a.date,
            a.mandi_id,
            m.mandi_name,
            m.district,
            SUM(a.arrival_quantity_qtl) AS total_daily_arrivals,
            MAX(w.temperature_c) AS max_temp_c,
            SUM(w.rainfall_mm) AS total_rainfall_mm
        FROM fact_arrivals a
        LEFT JOIN dim_mandi m ON a.mandi_id = m.mandi_id
        LEFT JOIN fact_weather w ON a.mandi_num = w.mandi_num 
             AND a.date_str = w.date_str
        GROUP BY a.date, a.mandi_id, m.mandi_name, m.district
    """)
    
    conn.commit()
    conn.close()
    print("Database build complete.")

if __name__ == "__main__":
    build_model()
