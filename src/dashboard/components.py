import html as html_mod
import streamlit as st

def render_kpi(label, value, unit="", metadata=None, is_alert=False):
    """Render a KPI card in the Newsprint style."""
    color_class = "ed-red" if is_alert else "ink"
    
    label_esc = html_mod.escape(str(label))
    value_esc = html_mod.escape(str(value))
    unit_esc = html_mod.escape(str(unit))
    
    # Adaptive font size: smaller for longer numbers
    num_len = len(value_esc.replace(',', '').replace('.', ''))
    if num_len > 7:
        val_size = '26px'
    elif num_len > 5:
        val_size = '32px'
    else:
        val_size = '42px'

    html_str = '<div style="border: 1px solid var(--border-color); padding: 1.2rem 1.5rem; min-height: 170px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: center;">'
    html_str += f'<div style="font-family: JetBrains Mono, monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 0.8rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{label_esc}</div>'
    html_str += f'<div><span style="font-family: Playfair Display, serif; font-size: {val_size}; font-weight: 700; color: var(--{color_class}); line-height: 1.1; display: block; overflow-wrap: anywhere; word-break: break-word; max-width: 100%;">{value_esc}</span>'
    html_str += f'<span style="font-family: JetBrains Mono, monospace; font-size: 13px; margin-left: 4px;">{unit_esc}</span></div>'
    
    if metadata:
        meta_esc = html_mod.escape(str(metadata))
        html_str += f'<div style="font-family: Inter, sans-serif; font-size: 12px; margin-top: 0.8rem; color: var(--ink); border-top: 1px dashed var(--muted); padding-top: 0.5rem;">{meta_esc}</div>'
        
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
