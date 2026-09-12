import html as html_mod
import streamlit as st

def render_kpi(label, value, unit="", metadata=None, is_alert=False):
    """Render a KPI card in the Newsprint style."""
    color_class = "ed-red" if is_alert else "ink"
    
    label_esc = html_mod.escape(str(label))
    value_esc = html_mod.escape(str(value))
    unit_esc = html_mod.escape(str(unit))
    
    html_str = f'<div style="border: 1px solid var(--border-color); padding: 1.5rem; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">'
    html_str += f'<div style="font-family: \'JetBrains Mono\', monospace; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 1rem;">{label_esc}</div>'
    html_str += f'<div><span style="font-family: \'Playfair Display\', serif; font-size: 3rem; font-weight: 700; color: var(--{color_class}); line-height: 1;">{value_esc}</span>'
    html_str += f'<span style="font-family: \'JetBrains Mono\', monospace; font-size: 1rem; margin-left: 0.25rem;">{unit_esc}</span></div>'
    
    if metadata:
        meta_esc = html_mod.escape(str(metadata))
        html_str += f'<div style="font-family: \'Inter\', sans-serif; font-size: 0.85rem; margin-top: 1rem; color: var(--ink); border-top: 1px dashed var(--muted); padding-top: 0.5rem;">{meta_esc}</div>'
        
    html_str += '</div>'
    
    st.html(html_str)

def render_section_header(title):
    """Render a clear editorial section header."""
    title_esc = html_mod.escape(str(title))
    st.html(f'<div class="section-header">{title_esc}</div>')

def render_masthead():
    """Render the dashboard masthead."""
    markup = '<div class="masthead">'
    markup += '<h1 class="masthead-title">MANDI INTELLIGENCE</h1>'
    markup += '<div class="masthead-subtitle">AgriTech Mandi-to-Market Supply Chain Optimizer</div>'
    markup += '<div class="masthead-meta">'
    markup += '<span>AGRITECH • SUPPLY CHAIN INTELLIGENCE</span>'
    markup += '<span>DATA EDITION • 2026</span>'
    markup += '</div></div>'
    st.html(markup)
