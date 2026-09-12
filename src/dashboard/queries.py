import os
import sqlite3
import pandas as pd
import streamlit as st

import contextlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "Dataset", "agritech_analytics.db")

def _get_db_path():
    """Return the database path, checking it exists."""
    if not os.path.exists(DB_PATH):
        return None
    return DB_PATH

def get_connection():
    """Create a fresh SQLite connection."""
    db_path = _get_db_path()
    if db_path is None:
        st.error(f"Database not found at {DB_PATH}")
        st.stop()
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        st.error(f"Failed to connect to database: {e}")
        st.stop()

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
