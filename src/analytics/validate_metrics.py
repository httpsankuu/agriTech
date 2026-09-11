import sqlite3
import os
import pandas as pd

def validate():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, "Dataset")
    DB_PATH = os.path.join(DATA_DIR, "agritech_analytics.db")
    
    conn = sqlite3.connect(DB_PATH)
    
    print("--- Analytics Validation Report ---\n")
    
    views = {
        'vw_crop_summary': "Total crop arrivals & Crop-wise distribution",
        'vw_mandi_performance': "Top Mandis by arrival volume",
        'vw_arrival_trends': "Daily/weekly/monthly arrival trends",
        'vw_price_vs_msp': "Wholesale modal price vs MSP & Price crashes",
        'vw_transit_delays': "Transport delay rate & Highest-delay routes",
        'vw_weather_impact': "Weather impact on crop arrivals (Rainfall vs Volume)"
    }
    
    for v, desc in views.items():
        try:
            count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM {v}", conn).iloc[0]['cnt']
            status = "PASSED" if count > 0 else "FAILED (Empty View)"
            print(f"- Metric: {desc}")
            print(f"  View Name: {v}")
            print(f"  Result Row Count: {count}")
            print(f"  Validation Status: {status}\n")
        except Exception as e:
            print(f"- Metric: {desc}")
            print(f"  View Name: {v}")
            print(f"  Validation Status: FAILED ({str(e)})\n")
    
    print("--- Specific Data Checks ---\n")
    
    # Price crashes
    crashes = pd.read_sql("SELECT SUM(is_price_crash) as total_crashes FROM vw_price_vs_msp", conn).iloc[0]['total_crashes']
    status = "PASSED" if crashes > 0 else "WARNING (No crashes found)"
    print(f"- Metric: Price crash instances")
    print(f"  Result: {crashes} crash days detected")
    print(f"  Validation Status: {status}\n")
    
    # Weather joined data
    weather_joined = pd.read_sql("SELECT COUNT(*) as cnt FROM vw_weather_impact WHERE total_rainfall_mm IS NOT NULL", conn).iloc[0]['cnt']
    status = "PASSED" if weather_joined > 0 else "FAILED (No weather data joined)"
    print(f"- Metric: Weather Impact Join Success")
    print(f"  Result: {weather_joined} arrival records successfully joined with weather data")
    print(f"  Validation Status: {status}\n")
    
    # Delay rates
    delays = pd.read_sql("SELECT SUM(delayed_trips) as total_delays, AVG(delay_rate) as avg_delay_rate FROM vw_transit_delays", conn).iloc[0]
    status = "PASSED" if delays['total_delays'] > 0 else "WARNING (No delays found)"
    print(f"- Metric: Transport Delay Rate")
    print(f"  Result: {delays['total_delays']} delayed trips detected. Average route delay rate: {delays['avg_delay_rate']:.2%}")
    print(f"  Validation Status: {status}\n")
    
    print("Assumptions Made:")
    print("- Delay Threshold: A trip is considered delayed if its transit time exceeds 1.5x the average transit time for that specific route (Mandi -> Warehouse). Invalid records (transit_time_invalid=True) were excluded.")
    print("- Weather Mapping: Sensors are mapped to Mandis via extracting the numeric ID (e.g., SEN047 -> MANDI-047). Weather records were aggregated to a daily grain before joining with arrivals.")
    
    conn.close()

if __name__ == "__main__":
    validate()
