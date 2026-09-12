import sqlite3
import pandas as pd
import os

def build_model():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, "Dataset")
    CLEAN_DIR = os.path.join(DATA_DIR, "clean")
    DB_PATH = os.path.join(DATA_DIR, "agritech_analytics.db")
    
    print(f"Connecting to database at {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        print(f"ERROR: Could not connect to database: {e}")
        return
    
    try:
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
        
        # Drop stale views before recreating
        cursor.execute("DROP VIEW IF EXISTS vw_crop_summary")
        cursor.execute("DROP VIEW IF EXISTS vw_mandi_performance")
        cursor.execute("DROP VIEW IF EXISTS vw_arrival_trends")
        cursor.execute("DROP VIEW IF EXISTS vw_price_vs_msp")
        cursor.execute("DROP VIEW IF EXISTS vw_transit_delays")
        cursor.execute("DROP VIEW IF EXISTS vw_weather_impact")
        
        # Add indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_arr_date ON fact_arrivals(date_str)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_arr_mandi ON fact_arrivals(mandi_num)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_wthr_date ON fact_weather(date_str)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_wthr_mandi ON fact_weather(mandi_num)")
    
        # 1. Total arrivals & Crop-wise distribution
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS vw_crop_summary AS
            SELECT 
                a.date_str as date,
                a.mandi_id,
                m.mandi_name,
                a.crop_name,
                SUM(a.arrival_quantity_qtl) AS total_arrival_qtl,
                SUM(a.farmer_count) AS total_farmers
            FROM fact_arrivals a
            LEFT JOIN dim_mandi m ON a.mandi_id = m.mandi_id
            GROUP BY a.date_str, a.mandi_id, m.mandi_name, a.crop_name
        ''')

        # 2. Top Mandis by arrival volume
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS vw_mandi_performance AS
            SELECT 
                a.mandi_id,
                m.mandi_name,
                m.district,
                m.state,
                SUM(a.arrival_quantity_qtl) AS total_arrival_volume_qtl
            FROM fact_arrivals a
            LEFT JOIN dim_mandi m ON a.mandi_id = m.mandi_id
            GROUP BY a.mandi_id, m.mandi_name, m.district, m.state
            ORDER BY total_arrival_volume_qtl DESC
        ''')

        # 3. Daily/weekly/monthly arrival trends
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS vw_arrival_trends AS
            SELECT 
                strftime('%Y-%m-%d', a.date_str) as day_date,
                strftime('%Y-%W', a.date_str) as week_str,
                strftime('%Y-%m', a.date_str) as month_str,
                SUM(a.arrival_quantity_qtl) as daily_total_qtl
            FROM fact_arrivals a
            GROUP BY a.date_str
        ''')

        # 4. Wholesale modal price vs MSP & Price crash instances
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS vw_price_vs_msp AS
            SELECT 
                p.date_str as date,
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
        ''')

        # 5. Average transit time by warehouse & Transport delay rate & Highest-delay routes
        # Assumption: A trip is delayed if its transit time is > 1.5x the average transit time for that specific route.
        # Excludes invalid transit records.
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS vw_transit_delays AS
            WITH RouteStats AS (
                SELECT 
                    mandi_id, 
                    destination_warehouse, 
                    AVG(transit_hours_clean) as avg_transit_hours
                FROM fact_logistics
                WHERE transit_hours_clean IS NOT NULL
                GROUP BY mandi_id, destination_warehouse
            )
            SELECT 
                l.mandi_id,
                l.destination_warehouse,
                r.avg_transit_hours,
                COUNT(l.trip_id) as total_trips,
                SUM(CASE WHEN l.transit_hours_clean > r.avg_transit_hours * 1.5 THEN 1 ELSE 0 END) as delayed_trips,
                CAST(SUM(CASE WHEN l.transit_hours_clean > r.avg_transit_hours * 1.5 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(l.trip_id) as delay_rate
            FROM fact_logistics l
            JOIN RouteStats r ON l.mandi_id = r.mandi_id AND l.destination_warehouse = r.destination_warehouse
            WHERE l.transit_hours_clean IS NOT NULL
            GROUP BY l.mandi_id, l.destination_warehouse, r.avg_transit_hours
        ''')

        # 6. Weather impact on crop arrivals (Rainfall vs arrival-volume relationship)
        # Joining Arrivals and Weather on mandi_num (extracted digits) and date string.
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS vw_weather_impact AS
            WITH DailyWeather AS (
                SELECT 
                    mandi_num,
                    date_str,
                    MAX(temperature_c) as max_temp_c,
                    SUM(rainfall_mm) as total_rainfall_mm
                FROM fact_weather
                GROUP BY mandi_num, date_str
            )
            SELECT 
                a.date_str as date,
                a.mandi_id,
                m.mandi_name,
                SUM(a.arrival_quantity_qtl) AS daily_arrivals_qtl,
                w.max_temp_c,
                w.total_rainfall_mm
            FROM fact_arrivals a
            LEFT JOIN dim_mandi m ON a.mandi_id = m.mandi_id
            LEFT JOIN DailyWeather w ON a.mandi_num = w.mandi_num AND a.date_str = w.date_str
            GROUP BY a.date_str, a.mandi_id, m.mandi_name, w.max_temp_c, w.total_rainfall_mm
        ''')
    
        conn.commit()
        print("Database build complete.")
    except Exception as e:
        print(f"ERROR: Build failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    build_model()
