import os
import sqlite3
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "Dataset", "agritech_analytics.db")

@st.cache_resource
def get_connection():
    """Create and cache SQLite connection."""
    if not os.path.exists(DB_PATH):
        st.error(f"Database not found at {DB_PATH}")
        st.stop()
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(ttl=3600)
def get_crop_summary():
    """Load crop summary view."""
    conn = get_connection()
    return pd.read_sql("SELECT * FROM vw_crop_summary", conn)

@st.cache_data(ttl=3600)
def get_mandi_performance():
    """Load mandi performance view."""
    conn = get_connection()
    return pd.read_sql("SELECT * FROM vw_mandi_performance", conn)

@st.cache_data(ttl=3600)
def get_arrival_trends():
    """Load arrival trends view."""
    conn = get_connection()
    return pd.read_sql("SELECT * FROM vw_arrival_trends", conn)

@st.cache_data(ttl=3600)
def get_price_vs_msp():
    """Load price vs msp view."""
    conn = get_connection()
    return pd.read_sql("SELECT * FROM vw_price_vs_msp", conn)

@st.cache_data(ttl=3600)
def get_transit_delays():
    """Load transit delays view."""
    conn = get_connection()
    return pd.read_sql("SELECT * FROM vw_transit_delays", conn)

@st.cache_data(ttl=3600)
def get_weather_impact():
    """Load weather impact view."""
    conn = get_connection()
    return pd.read_sql("SELECT * FROM vw_weather_impact", conn)
