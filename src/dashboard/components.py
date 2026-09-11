import streamlit as st

def render_kpi(label, value, unit="", metadata=None, is_alert=False):
    """Render a KPI card in the Newsprint style."""
    color_class = "ed-red" if is_alert else "ink"
    
    html = f'<div style="border: 1px solid var(--border-color); padding: 1.5rem; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">'
    html += f'<div style="font-family: \'JetBrains Mono\', monospace; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 1rem;">{label}</div>'
    html += f'<div><span style="font-family: \'Playfair Display\', serif; font-size: 3rem; font-weight: 700; color: var(--{color_class}); line-height: 1;">{value}</span>'
    html += f'<span style="font-family: \'JetBrains Mono\', monospace; font-size: 1rem; margin-left: 0.25rem;">{unit}</span></div>'
    
    if metadata:
        html += f'<div style="font-family: \'Inter\', sans-serif; font-size: 0.85rem; margin-top: 1rem; color: var(--ink); border-top: 1px dashed var(--muted); padding-top: 0.5rem;">{metadata}</div>'
        
    html += '</div>'
    
    st.html(html)

def render_section_header(title):
    """Render a clear editorial section header."""
    st.html(f'<div class="section-header">{title}</div>')

def render_masthead():
    """Render the dashboard masthead."""
    html = '<div class="masthead">'
    html += '<h1 class="masthead-title">MANDI INTELLIGENCE</h1>'
    html += '<div class="masthead-subtitle">AgriTech Mandi-to-Market Supply Chain Optimizer</div>'
    html += '<div class="masthead-meta">'
    html += '<span>AGRITECH • SUPPLY CHAIN INTELLIGENCE</span>'
    html += '<span>DATA EDITION • 2026</span>'
    html += '</div></div>'
    st.html(html)
