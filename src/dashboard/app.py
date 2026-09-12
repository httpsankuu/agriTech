import os
import sys
import streamlit as st
import pandas as pd

# Ensure src/dashboard is on the path for sibling imports
sys.path.insert(0, os.path.dirname(__file__))

from queries import (
    get_crop_summary, get_mandi_performance, get_arrival_trends,
    get_price_vs_msp, get_transit_delays, get_weather_impact
)
import components as ui
import charts
import agent

# Page config
st.set_page_config(
    page_title="Mandi Intelligence | AgriTech",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    load_css()
    
    # Render Masthead
    ui.render_masthead()
    
    # Load Data
    with st.spinner("Loading intelligence data..."):
        df_crop = get_crop_summary()
        df_mandi = get_mandi_performance()
        df_trends = get_arrival_trends()
        df_price = get_price_vs_msp()
        df_delays = get_transit_delays()
        df_weather = get_weather_impact()

    # Global date conversion is now handled in queries.py via parse_dates
        
    # Minimum and Maximum dates across datasets
    all_dates = pd.concat([
        df_trends['day_date'] if not df_trends.empty else pd.Series(dtype='datetime64[ns]'),
        df_price['date'] if not df_price.empty else pd.Series(dtype='datetime64[ns]')
    ])
    
    min_date = all_dates.dropna().min().date() if not all_dates.dropna().empty else None
    max_date = all_dates.dropna().max().date() if not all_dates.dropna().empty else None

    # Sidebar Filters
    st.sidebar.html("<div style='font-family: Playfair Display; font-size: 1.5rem; font-weight: bold; border-bottom: 2px solid var(--ink); padding-bottom: 0.5rem; margin-bottom: 1rem;'>FILTERS</div>")
    
    # 1. Date Range
    if min_date and max_date:
        date_range = st.sidebar.date_input("DATE RANGE", [min_date, max_date], min_value=min_date, max_value=max_date)
    else:
        date_range = None
        
    # 2. Crop
    available_crops = df_crop['crop_name'].dropna().unique().tolist() if not df_crop.empty else []
    selected_crops = st.sidebar.multiselect("CROP", available_crops)
    
    # 3. Mandi
    available_mandis = df_crop['mandi_name'].dropna().unique().tolist() if not df_crop.empty else []
    selected_mandis = st.sidebar.multiselect("MANDI", available_mandis)

    # 4. District
    available_districts = df_mandi['district'].dropna().unique().tolist() if not df_mandi.empty else []
    selected_districts = st.sidebar.multiselect("DISTRICT", available_districts)

    if st.sidebar.button("RESET FILTERS"):
        st.rerun()

    # Apply Filters
    def filter_df(df, date_col=None, crop_col=None, mandi_col=None, district_col=None):
        mask = pd.Series(True, index=df.index)
        if date_range and len(date_range) == 2 and date_col and date_col in df.columns:
            start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            mask = mask & (df[date_col] >= start_date) & (df[date_col] <= end_date)
        if selected_crops and crop_col and crop_col in df.columns:
            mask = mask & (df[crop_col].isin(selected_crops))
        if selected_mandis and mandi_col and mandi_col in df.columns:
            mask = mask & (df[mandi_col].isin(selected_mandis))
        if selected_districts and district_col and district_col in df.columns:
            mask = mask & (df[district_col].isin(selected_districts))
        return df[mask]

    f_crop = filter_df(df_crop, date_col='date', crop_col='crop_name', mandi_col='mandi_name')
    # trends only has day_date, can't easily filter by crop/mandi without re-aggregating, but we use views
    f_trends = filter_df(df_trends, date_col='day_date') 
    f_price = filter_df(df_price, date_col='date', crop_col='crop_name', mandi_col='mandi_name', district_col='district')
    # For delays, we can filter by mandi if selected
    f_delays = df_delays.copy()
    if selected_mandis and 'mandi_id' in f_delays.columns and 'mandi_id' in df_mandi.columns:
        valid_mandi_ids = df_mandi[df_mandi['mandi_name'].isin(selected_mandis)]['mandi_id'].tolist()
        f_delays = f_delays[f_delays['mandi_id'].isin(valid_mandi_ids)]
        
    f_weather = filter_df(df_weather, date_col='date', mandi_col='mandi_name')

    # Executive KPI Strip
    total_arrivals = f_crop['total_arrival_qtl'].sum() if not f_crop.empty else 0
    price_crashes = f_price['is_price_crash'].sum() if not f_price.empty else 0
    
    total_trips = f_delays['total_trips'].sum() if not f_delays.empty else 0
    delayed_trips = f_delays['delayed_trips'].sum() if not f_delays.empty else 0
    delay_rate = (delayed_trips / total_trips * 100) if total_trips > 0 else 0
    routes_monitored = len(f_delays) if not f_delays.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        ui.render_kpi("TOTAL ARRIVALS", f"{total_arrivals:,.2f}", "QTL", "Sum of arrival_quantity_qtl")
    with col2:
        ui.render_kpi("PRICE CRASHES", f"{price_crashes:,}", "INSTANCES", "Where modal_price < msp", is_alert=(price_crashes > 0))
    with col3:
        ui.render_kpi("TRANSPORT DELAY RATE", f"{delay_rate:.1f}", "%", f"{delayed_trips:,} delayed trips", is_alert=(delay_rate > 15))
    with col4:
        ui.render_kpi("ROUTES MONITORED", f"{routes_monitored:,}", "ROUTES", "Mandi → Warehouse")
    
    st.html("<br>")
    
    # Supply Intelligence
    ui.render_section_header("SUPPLY INTELLIGENCE")
    
    col_supply_left, col_supply_right = st.columns([2, 1])
    
    with col_supply_left:
        trend_fig = charts.create_arrival_trend_chart(f_trends)
        if trend_fig:
            st.plotly_chart(trend_fig, use_container_width=True)
        else:
            st.info("NO DATA FOR SELECTED FILTERS")
            
    with col_supply_right:
        dist_fig = charts.create_crop_distribution_chart(f_crop)
        if dist_fig:
            st.plotly_chart(dist_fig, use_container_width=True)
            
        st.html("<div class='figure-caption'>TOP MANDIS BY ARRIVAL VOLUME</div>")
        if not f_crop.empty:
            top_mandis = f_crop.groupby('mandi_name')['total_arrival_qtl'].sum().reset_index()
            top_mandis = top_mandis.sort_values('total_arrival_qtl', ascending=False).head(5)
            top_mandis.columns = ['Mandi', 'Arrival Volume (Qtl)']
            top_mandis['Rank'] = range(1, len(top_mandis) + 1)
            st.dataframe(top_mandis[['Rank', 'Mandi', 'Arrival Volume (Qtl)']], hide_index=True, use_container_width=True)

    # Price Intelligence
    ui.render_section_header("PRICE DISCOVERY")
    
    col_price_left, col_price_right = st.columns([2, 1])
    with col_price_left:
        # Group by date to average out for the chart to be readable
        if not f_price.empty:
            daily_price = f_price.groupby('date')[['modal_price', 'msp']].mean().reset_index()
            price_fig = charts.create_price_vs_msp_chart(daily_price)
            if price_fig:
                st.plotly_chart(price_fig, use_container_width=True)
    
    with col_price_right:
        st.html("<h3 style='font-family: Playfair Display; margin-top: 0; color: var(--ed-red); border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;'>PRICE CRASH WATCH</h3>")
        st.html(f"<p><b>{price_crashes:,}</b> recorded instances where wholesale modal price fell below Minimum Support Price (MSP).</p>")
        
        if price_crashes > 0:
            crashes_df = f_price[f_price['is_price_crash'] == 1]
            st.html("<b>WORST GAPS (INR):</b>")
            worst_gaps = crashes_df.sort_values('price_deviation').head(5)
            worst_gaps = worst_gaps[['date', 'mandi_name', 'crop_name', 'price_deviation']]
            worst_gaps['date'] = worst_gaps['date'].dt.strftime('%Y-%m-%d')
            st.dataframe(worst_gaps, hide_index=True, use_container_width=True)
        
    # Logistics Intelligence
    ui.render_section_header("LOGISTICS")
    
    st.html("<div class='figure-caption'>ROUTES UNDER PRESSURE (HIGHEST DELAY FREQUENCY)</div>")
    if not f_delays.empty:
        # Merge mandi name for display
        delays_disp = pd.merge(f_delays, df_mandi[['mandi_id', 'mandi_name']].drop_duplicates(), on='mandi_id', how='left')
        bad_routes = delays_disp[delays_disp['total_trips'] >= 12].sort_values('delay_rate', ascending=False).head(10)
        
        if not bad_routes.empty:
            bad_routes['delay_rate_pct'] = (bad_routes['delay_rate'] * 100).map('{:.1f}%'.format)
            bad_routes['avg_transit_hours'] = bad_routes['avg_transit_hours'].map('{:.1f}'.format)
            disp_cols = ['mandi_name', 'destination_warehouse', 'total_trips', 'delayed_trips', 'delay_rate_pct', 'avg_transit_hours']
            bad_routes = bad_routes[disp_cols]
            bad_routes.columns = ['Mandi', 'Warehouse', 'Valid Trips', 'Delayed Trips', 'Delay Rate', 'Avg Transit (Hrs)']
            st.dataframe(bad_routes, hide_index=True, use_container_width=True)
        else:
            st.info("NO ROUTES FOUND WITH AT LEAST 12 TRIPS")
            
    # Weather Impact
    ui.render_section_header("WEATHER × SUPPLY")
    st.html("<p style='font-family: Inter; font-size: 0.9rem;'>Daily rainfall and temperature are compared with crop arrival volumes where weather observations are available.</p>")
    
    col_wthr_left, col_wthr_right = st.columns([2, 1])
    with col_wthr_left:
        wthr_fig = charts.create_weather_impact_chart(f_weather)
        if wthr_fig:
            st.plotly_chart(wthr_fig, use_container_width=True)
        else:
            st.info("WEATHER DATA NOT AVAILABLE FOR THIS PERIOD")
            
    with col_wthr_right:
        matched_days = df_weather['total_rainfall_mm'].notna().sum()
        total_days = len(df_weather)
        unmatched = total_days - matched_days
        
        wthr_html = "<div style='border: 1px solid var(--border-color); padding: 1.5rem;'>"
        wthr_html += "<b>WEATHER COVERAGE</b><hr style='margin: 0.5rem 0; border-top: 1px solid var(--border-color);'>"
        wthr_html += f"<span style='font-family: JetBrains Mono; font-size: 1.5rem;'>{matched_days:,}</span><br><span style='font-size:0.8rem;'>WEATHER-MATCHED ARRIVAL DAYS</span><br><br>"
        wthr_html += f"<span style='font-family: JetBrains Mono; font-size: 1.5rem;'>{unmatched:,}</span><br><span style='font-size:0.8rem;'>UNMATCHED DAYS RETAINED</span>"
        wthr_html += "</div>"
        st.html(wthr_html)
        
    # ── AI Agent ──────────────────────────────────────────────────────
    ui.render_section_header("AI QUERY AGENT")
    st.html("<p style='font-family: Inter; font-size: 0.9rem;'>Ask questions about the supply chain data in plain English. The agent converts your query into SQL and generates charts automatically.</p>")

    # Suggested queries
    with st.expander("SUGGESTED QUERIES", expanded=False):
        for sq in agent.SUGGESTED_QUERIES:
            if st.button(sq, key=f"sq_{sq[:30]}", use_container_width=True):
                st.session_state["agent_query"] = sq
                st.rerun()

    # Custom Query Input (Highlighted)
    st.markdown("""
        <div style="background-color: var(--agri-green); padding: 2px; border-radius: 4px; margin-top: 1rem; margin-bottom: 1rem;">
            <div style="background-color: var(--paper); padding: 1rem; border-radius: 2px;">
                <h4 style="margin-top: 0; color: var(--agri-green);">ASK A CUSTOM QUESTION</h4>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form(key='ai_query_form', clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_query = st.text_input("Query", label_visibility="collapsed", placeholder="E.g., What is the average price of Wheat in Pune?")
        with col_btn:
            submit_btn = st.form_submit_button("ASK AGENT", type="primary", use_container_width=True)
            
        if submit_btn and user_query:
            st.session_state["agent_query"] = user_query

    # Process query from session state (buttons or chat input)
    if "agent_query" in st.session_state and st.session_state["agent_query"]:
        query = st.session_state["agent_query"]
        st.session_state["agent_query"] = None  # consume the query

        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent.run_agent(query)

            if response.error:
                st.error(response.error)
            else:
                st.markdown(response.summary)
                if response.chart:
                    st.plotly_chart(response.chart, use_container_width=True)
                if response.data is not None and not response.data.empty:
                    with st.expander("VIEW DATA TABLE"):
                        st.dataframe(response.data, hide_index=True, use_container_width=True)
                with st.expander("VIEW SQL QUERY"):
                    st.code(response.sql_query, language="sql")

    # Footer / Methodology
    ui.render_section_header("METHODOLOGY & DATA TRANSPARENCY")
    with st.expander("VIEW METHODOLOGY"):
        st.markdown("""
        - **SOURCE**: Cleaned datathon datasets
        - **ANALYTICS**: SQLite analytical views (Phase 2 validated)
        - **INVALID TRANSPORT RECORDS**: Excluded from transit performance calculations
        - **PRICE CRASH**: Instances where `modal_price < msp`
        - **WEATHER**: Daily aggregation before joining to arrivals
        - **DELAY THRESHOLD**: `transit_hours_clean > 1.5 × route average`
        """)

if __name__ == "__main__":
    main()
