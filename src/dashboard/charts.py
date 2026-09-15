import logging
import plotly.express as px
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

# Design Tokens — kept in sync with styles.css
COLORS = {
    "paper": "#F7F6F0",
    "ink": "#111111",
    "muted": "#E8E7E0",
    "green": "#2F6B3F",
    "red": "#B42318",
}

def apply_newsprint_theme(fig):
    """Apply the newsprint editorial theme to a plotly figure."""
    fig.update_layout(
        plot_bgcolor=COLORS["paper"],
        paper_bgcolor=COLORS["paper"],
        font=dict(family="Inter", color=COLORS["ink"], size=12),
        title_font=dict(family="Playfair Display", size=18, color=COLORS["ink"]),
        margin=dict(t=40, l=10, r=10, b=10),
        xaxis=dict(
            showgrid=False,
            zeroline=True,
            zerolinecolor=COLORS["ink"],
            zerolinewidth=1,
            linecolor=COLORS["ink"],
            linewidth=1,
            tickfont=dict(family="JetBrains Mono", size=10)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS["muted"],
            gridwidth=1,
            zeroline=True,
            zerolinecolor=COLORS["ink"],
            zerolinewidth=1,
            linecolor=COLORS["ink"],
            linewidth=1,
            tickfont=dict(family="JetBrains Mono", size=10)
        ),
        hoverlabel=dict(
            bgcolor=COLORS["ink"],
            font_size=12,
            font_family="Inter",
            font_color=COLORS["paper"]
        )
    )
    return fig

def create_arrival_trend_chart(df):
    """Create a daily arrival trend line chart."""
    if df is None or df.empty:
        return None
    
    try:
        df = df.sort_values('day_date')
        fig = px.line(
            df, 
            x='day_date', 
            y='daily_total_qtl',
            title="FIG. 01 — DAILY ARRIVAL VOLUME",
            labels={'day_date': 'DATE', 'daily_total_qtl': 'ARRIVAL VOLUME (QTL)'}
        )
        
        fig.update_traces(line=dict(color=COLORS["ink"], width=2))
        fig.update_traces(fill='tozeroy', fillcolor='rgba(17, 17, 17, 0.05)')
        return apply_newsprint_theme(fig)
    except Exception:
        logger.exception("Failed to create arrival trend chart")
        return None

def create_crop_distribution_chart(df):
    """Create a horizontal bar chart of arrivals by crop."""
    if df is None or df.empty:
        return None
    
    try:
        crop_totals = df.groupby('crop_name')['total_arrival_qtl'].sum().reset_index()
        crop_totals = crop_totals.sort_values('total_arrival_qtl', ascending=True)
        
        fig = px.bar(
            crop_totals, 
            y='crop_name', 
            x='total_arrival_qtl',
            orientation='h',
            title="FIG. 02 — CROP DISTRIBUTION",
            labels={'crop_name': 'CROP', 'total_arrival_qtl': 'TOTAL VOLUME (QTL)'}
        )
        
        fig.update_traces(marker_color=COLORS["ink"], marker_line_color=COLORS["ink"], marker_line_width=1)
        fig = apply_newsprint_theme(fig)
        fig.update_layout(yaxis=dict(showgrid=False))
        return fig
    except Exception:
        logger.exception("Failed to create crop distribution chart")
        return None

def create_price_vs_msp_chart(df):
    """Create a chart comparing modal price to MSP."""
    if df is None or df.empty:
        return None
    
    try:
        df = df.sort_values('date')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['modal_price'],
            mode='lines',
            name='MODAL PRICE',
            line=dict(color=COLORS["ink"], width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['msp'],
            mode='lines',
            name='MSP',
            line=dict(color=COLORS["green"], width=2, dash='dash')
        ))
        
        fig.update_layout(
            title="FIG. 03 — PRICE DISCOVERY (MODAL VS MSP)",
            xaxis_title="DATE",
            yaxis_title="PRICE (INR)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(family="JetBrains Mono", size=10)
            )
        )
        
        return apply_newsprint_theme(fig)
    except Exception:
        logger.exception("Failed to create price vs MSP chart")
        return None

def create_weather_impact_chart(df):
    """Create a scatter plot for weather vs arrivals."""
    if df is None or df.empty or 'total_rainfall_mm' not in df.columns or 'daily_arrivals_qtl' not in df.columns or df['total_rainfall_mm'].isna().all():
        return None
    
    try:
        plot_df = df.dropna(subset=['total_rainfall_mm', 'daily_arrivals_qtl'])
        
        fig = px.scatter(
            plot_df,
            x='total_rainfall_mm',
            y='daily_arrivals_qtl',
            title="FIG. 04 — OBSERVED RELATIONSHIP: RAINFALL × ARRIVALS",
            labels={'total_rainfall_mm': 'TOTAL RAINFALL (MM)', 'daily_arrivals_qtl': 'DAILY ARRIVALS (QTL)'},
            opacity=0.7
        )
        
        fig.update_traces(marker=dict(color=COLORS["ink"], size=8, line=dict(width=1, color=COLORS["paper"])))
        return apply_newsprint_theme(fig)
    except Exception:
        logger.exception("Failed to create weather impact chart")
        return None
