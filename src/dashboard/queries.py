import os
import sqlite3
import pandas as pd
import streamlit as st

import contextlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "Dataset", "agritech_analytics.db")

def get_connection():
    """Create a fresh SQLite connection."""
    if not os.path.exists(DB_PATH):
        st.error(f"Database not found at {DB_PATH}")
        st.stop()
    return sqlite3.connect(DB_PATH)

@st.cache_data(ttl=3600)
def get_crop_summary():
    """Load crop summary view."""
    with contextlib.closing(get_connection()) as conn:
        return pd.read_sql("SELECT * FROM vw_crop_summary", conn, parse_dates=['date'])

@st.cache_data(ttl=3600)
def get_mandi_performance():
    """Load mandi performance view."""
    with contextlib.closing(get_connection()) as conn:
        return pd.read_sql("SELECT * FROM vw_mandi_performance", conn)

@st.cache_data(ttl=3600)
def get_arrival_trends():
    """Load arrival trends view."""
    with contextlib.closing(get_connection()) as conn:
        return pd.read_sql("SELECT * FROM vw_arrival_trends", conn, parse_dates=['day_date'])

@st.cache_data(ttl=3600)
def get_price_vs_msp():
    """Load price vs msp view."""
    with contextlib.closing(get_connection()) as conn:
        return pd.read_sql("SELECT * FROM vw_price_vs_msp", conn, parse_dates=['date'])

@st.cache_data(ttl=3600)
def get_transit_delays():
    """Load transit delays view."""
    with contextlib.closing(get_connection()) as conn:
        return pd.read_sql("SELECT * FROM vw_transit_delays", conn)

@st.cache_data(ttl=3600)
def get_weather_impact():
    """Load weather impact view."""
    with contextlib.closing(get_connection()) as conn:
        return pd.read_sql("SELECT * FROM vw_weather_impact", conn, parse_dates=['date'])
