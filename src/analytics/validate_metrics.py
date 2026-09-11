import sqlite3
import os
import pandas as pd

def validate():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, "Dataset")
    DB_PATH = os.path.join(DATA_DIR, "agritech_analytics.db")
    
    conn = sqlite3.connect(DB_PATH)
    
    print("--- Data Model Validation ---")
    
    tables = ['dim_mandi', 'fact_arrivals', 'fact_prices', 'fact_logistics', 'fact_weather']
    for t in tables:
        count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM {t}", conn).iloc[0]['cnt']
        print(f"Table '{t}': {count} rows")
        assert count > 0, f"Table {t} is empty!"
        
    views = ['vw_price_vs_msp', 'vw_transit_performance', 'vw_crop_summary', 'vw_mandi_daily_summary']
    for v in views:
        count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM {v}", conn).iloc[0]['cnt']
        print(f"View '{v}': {count} rows")
        assert count > 0, f"View {v} is empty!"
        
    print("\nValidating Price Crashes...")
    crashes = pd.read_sql("SELECT SUM(is_price_crash) as total_crashes FROM vw_price_vs_msp", conn).iloc[0]['total_crashes']
    print(f"Total price crashes (Modal < MSP) detected: {crashes}")
    
    print("\nValidating Weather Joined Data...")
    weather_joined = pd.read_sql("SELECT COUNT(*) as cnt FROM vw_mandi_daily_summary WHERE total_rainfall_mm IS NOT NULL", conn).iloc[0]['cnt']
    print(f"Daily summaries with weather data attached: {weather_joined}")
    
    conn.close()
    print("\nAll validations passed successfully!")

if __name__ == "__main__":
    validate()
