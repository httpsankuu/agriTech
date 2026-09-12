"""
Agentic AI Query Engine for the Mandi Intelligence Dashboard.

Hybrid approach: regex pattern matching as default, optional LLM fallback.
Converts natural language queries into SQL + Plotly charts.
"""

import re
import os
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dataclasses import dataclass, field
from typing import Optional

# ── Design Tokens (kept in sync with charts.py) ──────────────────────────
COLORS = {
    "paper": "#F7F6F0",
    "ink": "#111111",
    "muted": "#E8E7E0",
    "green": "#2F6B3F",
    "red": "#B42318",
}

# ── Known entities ────────────────────────────────────────────────────────
KNOWN_CROPS = ["wheat", "maize", "rice", "cotton", "mustard", "sugarcane"]
KNOWN_METRICS = {
    "arrival": "arrival_quantity_qtl",
    "volume": "arrival_quantity_qtl",
    "price": "modal_price",
    "msp": "msp",
    "rainfall": "rainfall_mm",
    "temperature": "temperature_c",
    "transit": "transit_hours_clean",
    "delay": "delay_rate",
    "farmer": "farmer_count",
}

# ── Data classes ──────────────────────────────────────────────────────────

@dataclass
class ParsedQuery:
    """Structured representation of a parsed natural language query."""
    intent: str = "unknown"          # trend, comparison, distribution, correlation, top_n, summary, price_check
    metric: str = "arrival_quantity_qtl"
    crop: Optional[str] = None
    mandi: Optional[str] = None
    district: Optional[str] = None
    chart_type: str = "table"        # line, bar, hbar, scatter, table
    time_range: Optional[str] = None # "last_7_days", "last_30_days", "all"
    limit: int = 10
    raw_query: str = ""
    confidence: float = 0.0


@dataclass
class AgentResponse:
    """Result from the agent: text summary + optional chart + data table."""
    summary: str = ""
    chart: Optional[object] = None   # plotly figure
    data: Optional[pd.DataFrame] = None
    sql_query: str = ""
    error: Optional[str] = None


# ── Query Parser ──────────────────────────────────────────────────────────

def _extract_crop(text: str) -> Optional[str]:
    """Extract crop name from query text."""
    text_lower = text.lower()
    for crop in KNOWN_CROPS:
        if re.search(r'\b' + crop + r'\b', text_lower):
            return crop.title()
    # Hindi aliases
    hindi_map = {
        "गेहूं": "Wheat", "gehun": "Wheat", "kanak": "Wheat",
        "मक्का": "Maize", "makka": "Maize",
        "गन्ना": "Sugarcane", "ganna": "Sugarcane",
        "कपास": "Cotton", "narma": "Cotton",
        "सरसों": "Mustard", "sarson": "Mustard",
        "धान": "Rice", "चावल": "Rice", "dhaan": "Rice",
    }
    for alias, canonical in hindi_map.items():
        if alias in text:
            return canonical
    return None


def _extract_mandi(text: str) -> Optional[str]:
    """Extract mandi name from query text."""
    # Words that are NOT mandi names (crops, intents, common words)
    stop_words = {
        "The", "Show", "Plot", "Display", "What", "How", "Compare", "Total",
        "Average", "Top", "Give", "List", "Get", "Find", "Chart", "Graph",
        "Table", "Daily", "Monthly", "Weekly", "Last", "Past", "Recent",
        "All", "Price", "Arrival", "Weather", "Rain", "Crop", "Mandi",
        "Vs", "versus", "against", "Most", "Highest", "Lowest", "Best",
        "Worst", "Biggest", "Largest", "Trend", "Over", "Time", "Below",
        "Above", "Between", "And", "For", "With", "From", "This", "Past",
    }
    # Add all known crop names (case-insensitive) to stop words
    crop_stops = {c.title() for c in KNOWN_CROPS}
    stop_words.update(crop_stops)
    hindi_crops = {"Wheat", "Maize", "Sugarcane", "Cotton", "Mustard", "Rice"}
    stop_words.update(hindi_crops)

    # Look for patterns like "in Amritsar mandi" or "at Ludhiana"
    match = re.search(r'(?:in|at|from|of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:mandi)?', text)
    if match:
        candidate = match.group(1).strip()
        if candidate not in stop_words:
            return candidate
    # Also try standalone capitalized words that might be mandi names
    match = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
    if match:
        candidate = match.group(1).strip()
        if candidate not in stop_words:
            return candidate
    return None


def _extract_district(text: str, mandi: Optional[str] = None) -> Optional[str]:
    """Extract district name from query text. Skips if mandi already specified."""
    if mandi:
        return None  # mandi already uniquely identifies location
    match = re.search(r'(?:district|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
    if match:
        return match.group(1).strip()
    return None


def _extract_time_range(text: str) -> Optional[str]:
    """Extract time range from query text."""
    text_lower = text.lower()
    if re.search(r'last\s+(\d+)\s+day', text_lower):
        days = re.search(r'last\s+(\d+)\s+day', text_lower).group(1)
        return f"last_{days}_days"
    if re.search(r'past\s+(\d+)\s+day', text_lower):
        days = re.search(r'past\s+(\d+)\s+day', text_lower).group(1)
        return f"last_{days}_days"
    if "today" in text_lower:
        return "last_1_days"
    if "yesterday" in text_lower:
        return "last_2_days"
    if "this week" in text_lower or "current week" in text_lower:
        return "last_7_days"
    if "this month" in text_lower or "current month" in text_lower:
        return "last_30_days"
    if "this year" in text_lower:
        return "last_365_days"
    if re.search(r'last\s+month', text_lower):
        return "last_30_days"
    if re.search(r'last\s+week', text_lower):
        return "last_7_days"
    return None


def _extract_metric(text: str) -> str:
    """Extract the primary metric from query text."""
    text_lower = text.lower()
    for keyword, column in KNOWN_METRICS.items():
        if keyword in text_lower:
            return column
    return "arrival_quantity_qtl"


def _detect_intent(text: str) -> str:
    """Detect the query intent from natural language."""
    text_lower = text.lower()

    # Trend detection
    if any(w in text_lower for w in ["trend", "over time", "daily", "weekly", "monthly", "timeline", "change over", "history", "historical"]):
        return "trend"

    # Comparison detection
    if any(w in text_lower for w in ["compare", "vs", "versus", "against", "difference", "higher", "lower", "more than", "less than"]):
        return "comparison"

    # Price check / MSP
    if any(w in text_lower for w in ["price crash", "below msp", "msp", "price vs", "price comparison", "price drop"]):
        return "price_check"

    # Distribution / breakdown
    if any(w in text_lower for w in ["distribution", "breakdown", "share", "proportion", "split", "crop-wise", "by crop"]):
        return "distribution"

    # Correlation
    if any(w in text_lower for w in ["correlation", "relationship", "impact", "effect", "rainfall", "weather", "temperature"]):
        return "correlation"

    # Top N
    if any(w in text_lower for w in ["top", "highest", "most", "best", "worst", "lowest", "least", "biggest", "largest"]):
        return "top_n"

    # Summary / general
    if any(w in text_lower for w in ["summary", "overview", "total", "summarize", "sum up", "give me", "show me", "what is", "what are"]):
        return "summary"

    return "summary"


def _detect_chart_type(intent: str, text: str) -> str:
    """Map intent + query text to a chart type."""
    text_lower = text.lower()

    # Explicit chart requests
    if any(w in text_lower for w in ["bar chart", "bar graph", "barchart"]):
        return "bar"
    if any(w in text_lower for w in ["line chart", "line graph", "lineplot"]):
        return "line"
    if any(w in text_lower for w in ["scatter", "scatter plot", "correlation plot"]):
        return "scatter"
    if any(w in text_lower for w in ["pie", "pie chart", "donut"]):
        return "hbar"  # horizontal bar as pie alternative

    # Intent-based defaults
    chart_map = {
        "trend": "line",
        "comparison": "bar",
        "price_check": "line",
        "distribution": "hbar",
        "correlation": "scatter",
        "top_n": "hbar",
        "summary": "table",
    }
    return chart_map.get(intent, "table")


def _extract_limit(text: str) -> int:
    """Extract a numeric limit from the query."""
    match = re.search(r'top\s+(\d+)', text.lower())
    if match:
        return int(match.group(1))
    match = re.search(r'(\d+)\s+(?:most|highest|largest|biggest)', text.lower())
    if match:
        return int(match.group(1))
    return 10


def parse_query(text: str) -> ParsedQuery:
    """Parse a natural language query into a structured ParsedQuery."""
    intent = _detect_intent(text)
    crop = _extract_crop(text)
    mandi = _extract_mandi(text)
    district = _extract_district(text, mandi=mandi)
    metric = _extract_metric(text)
    chart_type = _detect_chart_type(intent, text)
    time_range = _extract_time_range(text)
    limit = _extract_limit(text)

    # Calculate confidence based on how many entities we extracted
    entities_found = sum(1 for x in [crop, mandi, district, time_range] if x)
    confidence = min(0.5 + entities_found * 0.15, 1.0)

    return ParsedQuery(
        intent=intent,
        metric=metric,
        crop=crop,
        mandi=mandi,
        district=district,
        chart_type=chart_type,
        time_range=time_range,
        limit=limit,
        raw_query=text,
        confidence=confidence,
    )


# ── SQL Generator ─────────────────────────────────────────────────────────

def _get_time_filter(alias: str, time_range: Optional[str]) -> str:
    """Generate SQL WHERE clause for time range."""
    if not time_range:
        return ""
    col = f"{alias}.date_str" if alias else "date_str"
    if time_range.startswith("last_"):
        days = int(time_range.split("_")[1])
        return f" AND {col} >= date('now', '-{days} days')"
    return ""


def _get_crop_filter(alias: str, crop: Optional[str]) -> str:
    """Generate SQL WHERE clause for crop."""
    if not crop:
        return ""
    col = f"{alias}.crop_name" if alias else "crop_name"
    return f" AND {col} = '{crop}'"


def _get_mandi_filter(alias: str, mandi: Optional[str]) -> str:
    """Generate SQL WHERE clause for mandi name."""
    if not mandi:
        return ""
    col = f"{alias}.mandi_name" if alias else "mandi_name"
    return f" AND {col} LIKE '%{mandi}%'"


def _get_district_filter(alias: str, district: Optional[str]) -> str:
    """Generate SQL WHERE clause for district."""
    if not district:
        return ""
    col = f"{alias}.district" if alias else "district"
    return f" AND {col} LIKE '%{district}%'"


def generate_sql(parsed: ParsedQuery) -> str:
    """Generate a SQL query from the parsed query intent."""
    crop_f = _get_crop_filter("a", parsed.crop)
    mandi_f = _get_mandi_filter("m", parsed.mandi)
    district_f = _get_district_filter("m", parsed.district)
    time_f = _get_time_filter("a", parsed.time_range)
    all_filters = f"WHERE 1=1{crop_f}{mandi_f}{district_f}{time_f}"

    if parsed.intent == "trend":
        return f"""
            SELECT a.date_str as date, SUM(a.arrival_quantity_qtl) as value
            FROM fact_arrivals a
            LEFT JOIN dim_mandi m ON a.mandi_id = m.mandi_id
            {all_filters}
            GROUP BY a.date_str
            ORDER BY a.date_str
        """

    elif parsed.intent == "comparison" and parsed.metric == "modal_price":
        return f"""
            SELECT a.date_str as date, p.modal_price as value, p.msp as msp_line
            FROM fact_prices p
            LEFT JOIN dim_mandi m ON p.mandi_id = m.mandi_id
            LEFT JOIN (SELECT DISTINCT date_str FROM fact_arrivals) a ON p.date_str = a.date_str
            WHERE 1=1{_get_crop_filter('p', parsed.crop)}{_get_mandi_filter('m', parsed.mandi)}{_get_district_filter('m', parsed.district)}{_get_time_filter('p', parsed.time_range)}
            ORDER BY p.date_str
        """

    elif parsed.intent == "price_check":
        return f"""
            SELECT p.date as date, p.mandi_name, p.crop_name,
                   p.modal_price as value, p.msp as msp_line,
                   (p.modal_price - p.msp) as price_deviation
            FROM vw_price_vs_msp p
            WHERE p.is_price_crash = 1
            {_get_crop_filter('p', parsed.crop)}
            {_get_mandi_filter('p', parsed.mandi)}
            {_get_district_filter('p', parsed.district)}
            ORDER BY p.date
            LIMIT {parsed.limit}
        """

    elif parsed.intent == "distribution":
        return f"""
            SELECT a.crop_name, SUM(a.arrival_quantity_qtl) as value
            FROM fact_arrivals a
            LEFT JOIN dim_mandi m ON a.mandi_id = m.mandi_id
            {all_filters}
            GROUP BY a.crop_name
            ORDER BY value DESC
        """

    elif parsed.intent == "correlation":
        metric_col = "rainfall_mm" if "rain" in parsed.raw_query.lower() else "temperature_c"
        return f"""
            SELECT w.date_str as date, SUM(a.arrival_quantity_qtl) as value,
                   w.{metric_col} as x_value
            FROM fact_arrivals a
            LEFT JOIN dim_mandi m ON a.mandi_id = m.mandi_id
            LEFT JOIN fact_weather w ON a.mandi_num = w.mandi_num AND a.date_str = w.date_str
            {all_filters} AND w.{metric_col} IS NOT NULL
            GROUP BY a.date_str, w.{metric_col}
            ORDER BY a.date_str
        """

    elif parsed.intent == "top_n":
        return f"""
            SELECT m.mandi_name as label, SUM(a.arrival_quantity_qtl) as value
            FROM fact_arrivals a
            LEFT JOIN dim_mandi m ON a.mandi_id = m.mandi_id
            {all_filters}
            GROUP BY m.mandi_name
            ORDER BY value DESC
            LIMIT {parsed.limit}
        """

    else:  # summary / fallback
        return f"""
            SELECT a.date_str as date, a.crop_name,
                   SUM(a.arrival_quantity_qtl) as total_arrivals,
                   COUNT(DISTINCT a.mandi_id) as mandis_active
            FROM fact_arrivals a
            LEFT JOIN dim_mandi m ON a.mandi_id = m.mandi_id
            {all_filters}
            GROUP BY a.date_str, a.crop_name
            ORDER BY a.date_str
            LIMIT 100
        """


# ── Chart Builder ─────────────────────────────────────────────────────────

def apply_theme(fig):
    """Apply the Newsprint theme to a plotly figure."""
    fig.update_layout(
        plot_bgcolor=COLORS["paper"],
        paper_bgcolor=COLORS["paper"],
        font=dict(family="Inter", color=COLORS["ink"], size=12),
        title_font=dict(family="Playfair Display", size=16, color=COLORS["ink"]),
        margin=dict(t=50, l=10, r=10, b=10),
        xaxis=dict(
            showgrid=False, zeroline=True,
            zerolinecolor=COLORS["ink"], zerolinewidth=1,
            linecolor=COLORS["ink"], linewidth=1,
            tickfont=dict(family="JetBrains Mono", size=10),
        ),
        yaxis=dict(
            showgrid=True, gridcolor=COLORS["muted"], gridwidth=1,
            zeroline=True, zerolinecolor=COLORS["ink"], zerolinewidth=1,
            linecolor=COLORS["ink"], linewidth=1,
            tickfont=dict(family="JetBrains Mono", size=10),
        ),
        hoverlabel=dict(
            bgcolor=COLORS["ink"], font_size=12,
            font_family="Inter", font_color=COLORS["paper"],
        ),
    )
    return fig


def build_chart(df: pd.DataFrame, parsed: ParsedQuery):
    """Build a Plotly chart from query results."""
    if df is None or df.empty:
        return None

    try:
        # Handle "date" columns — parse if present
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"]).sort_values("date")

        chart_type = parsed.chart_type
        title = _generate_title(parsed)

        if chart_type == "line":
            fig = go.Figure()
            if "msp_line" in df.columns:
                fig.add_trace(go.Scatter(
                    x=df["date"], y=df["msp_line"],
                    mode="lines", name="MSP",
                    line=dict(color=COLORS["green"], width=2, dash="dash"),
                ))
            fig.add_trace(go.Scatter(
                x=df["date"], y=df["value"],
                mode="lines+markers", name="Value",
                line=dict(color=COLORS["ink"], width=2),
                marker=dict(size=4),
            ))
            fig.update_layout(title=title, xaxis_title="DATE", yaxis_title="VALUE")
            return apply_theme(fig)

        elif chart_type == "bar":
            if "msp_line" in df.columns:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df["date"], y=df["value"],
                    name="Modal Price", marker_color=COLORS["ink"],
                ))
                fig.add_trace(go.Scatter(
                    x=df["date"], y=df["msp_line"],
                    mode="lines", name="MSP",
                    line=dict(color=COLORS["green"], width=2, dash="dash"),
                ))
                fig.update_layout(title=title, xaxis_title="DATE", yaxis_title="PRICE (INR)")
                return apply_theme(fig)
            fig = px.bar(df, x=df.columns[0], y="value", title=title)
            fig.update_traces(marker_color=COLORS["ink"])
            return apply_theme(fig)

        elif chart_type == "hbar":
            label_col = "crop_name" if "crop_name" in df.columns else df.columns[0]
            fig = px.bar(
                df, y=label_col, x="value", orientation="h",
                title=title,
                labels={label_col: "CATEGORY", "value": "VOLUME (QTL)"},
            )
            fig.update_traces(marker_color=COLORS["ink"])
            fig.update_layout(yaxis=dict(showgrid=False))
            return apply_theme(fig)

        elif chart_type == "scatter":
            if "x_value" in df.columns:
                fig = px.scatter(
                    df, x="x_value", y="value",
                    title=title, opacity=0.7,
                    labels={"x_value": "WEATHER VALUE", "value": "ARRIVALS (QTL)"},
                )
                fig.update_traces(
                    marker=dict(color=COLORS["ink"], size=8,
                                line=dict(width=1, color=COLORS["paper"])),
                )
                return apply_theme(fig)

        # Fallback: no chart, return None
        return None

    except Exception:
        return None


def _generate_title(parsed: ParsedQuery) -> str:
    """Generate a descriptive chart title from the parsed query."""
    parts = []
    if parsed.intent == "trend":
        parts.append("TREND")
    elif parsed.intent == "comparison":
        parts.append("COMPARISON")
    elif parsed.intent == "price_check":
        parts.append("PRICE CRASH")
    elif parsed.intent == "distribution":
        parts.append("DISTRIBUTION")
    elif parsed.intent == "correlation":
        parts.append("CORRELATION")
    elif parsed.intent == "top_n":
        parts.append(f"TOP {parsed.limit}")
    else:
        parts.append("OVERVIEW")

    if parsed.crop:
        parts.append(parsed.crop.upper())
    if parsed.mandi:
        parts.append(f"IN {parsed.mandi.upper()}")

    return " — ".join(parts)


# ── Summary Generator ─────────────────────────────────────────────────────

def generate_summary(df: pd.DataFrame, parsed: ParsedQuery) -> str:
    """Generate a text summary of the query results."""
    if df is None or df.empty:
        return "No data found matching your query. Try adjusting the filters or rephrasing."

    lines = []

    if parsed.intent == "trend":
        total = df["value"].sum()
        avg = df["value"].mean()
        lines.append(f"**{parsed.crop or 'All crops'}** daily arrival trend:")
        lines.append(f"- Total arrivals: **{total:,.0f} QTL**")
        lines.append(f"- Daily average: **{avg:,.0f} QTL**")
        if len(df) > 1:
            first_val = df["value"].iloc[0]
            last_val = df["value"].iloc[-1]
            pct = ((last_val - first_val) / first_val * 100) if first_val > 0 else 0
            direction = "increased" if pct > 0 else "decreased"
            lines.append(f"- Overall: **{direction} {abs(pct):.1f}%**")

    elif parsed.intent == "price_check":
        n = len(df)
        lines.append(f"Found **{n}** price crash instances (modal price < MSP).")
        if "crop_name" in df.columns:
            crop_counts = df["crop_name"].value_counts()
            top_crop = crop_counts.index[0]
            lines.append(f"- Most affected crop: **{top_crop}** ({crop_counts.iloc[0]} crashes)")
        if "price_deviation" in df.columns:
            avg_dev = df["price_deviation"].mean()
            lines.append(f"- Average deviation from MSP: **₹{avg_dev:,.0f}**")

    elif parsed.intent == "correlation":
        lines.append(f"**Weather × Arrivals correlation**:")
        lines.append(f"- Data points: **{len(df)}**")
        if "x_value" in df.columns and "value" in df.columns:
            corr = df["x_value"].corr(df["value"])
            if abs(corr) > 0.5:
                strength = "strong" if abs(corr) > 0.7 else "moderate"
                direction = "positive" if corr > 0 else "negative"
                lines.append(f"- Correlation: **{strength} {direction}** (r={corr:.2f})")
            else:
                lines.append(f"- Correlation: **weak** (r={corr:.2f})")

    elif parsed.intent == "distribution":
        lines.append("**Crop-wise arrival distribution:**")
        for _, row in df.head(5).iterrows():
            crop = row.iloc[0]
            val = row["value"]
            lines.append(f"- {crop}: **{val:,.0f} QTL**")

    elif parsed.intent == "top_n":
        lines.append(f"**Top {parsed.limit}** by arrival volume:")
        for i, (_, row) in enumerate(df.head(parsed.limit).iterrows()):
            label = row.get("label", row.iloc[0])
            val = row["value"]
            lines.append(f"- {i+1}. {label}: **{val:,.0f} QTL**")

    else:
        total = df["total_arrivals"].sum() if "total_arrivals" in df.columns else df["value"].sum()
        lines.append(f"**Summary:** Total arrivals: **{total:,.0f} QTL** across **{len(df)}** records.")

    if parsed.time_range:
        time_label = parsed.time_range.replace("last_", "Last ").replace("_days", " days")
        lines.append(f"\n*Time range: {time_label}*")

    return "\n".join(lines)


# ── Main Agent Runner ─────────────────────────────────────────────────────

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "Dataset", "agritech_analytics.db",
)


def run_agent(query: str) -> AgentResponse:
    """
    Run the full agent pipeline: parse → SQL → execute → chart → summary.
    Returns an AgentResponse with text, chart, and data.
    """
    try:
        # 1. Parse the query
        parsed = parse_query(query)

        # 2. Generate SQL
        sql = generate_sql(parsed)

        # 3. Execute SQL
        if not os.path.exists(DB_PATH):
            return AgentResponse(error=f"Database not found at {DB_PATH}")

        conn = sqlite3.connect(DB_PATH)
        try:
            df = pd.read_sql(sql, conn)
        finally:
            conn.close()

        if df.empty:
            return AgentResponse(
                summary="No data found matching your query. Try rephrasing or use one of the suggested queries below.",
                sql_query=sql.strip(),
                data=df,
            )

        # 4. Build chart
        chart = build_chart(df, parsed)

        # 5. Generate summary
        summary = generate_summary(df, parsed)

        return AgentResponse(
            summary=summary,
            chart=chart,
            data=df,
            sql_query=sql.strip(),
        )

    except Exception as e:
        return AgentResponse(error=f"Agent error: {str(e)}")


# ── Suggested Queries ─────────────────────────────────────────────────────

SUGGESTED_QUERIES = [
    "Show me the daily arrival trend of Wheat",
    "What are the top 5 mandis by arrival volume?",
    "Plot price vs MSP for Rice",
    "Show price crashes for Cotton in the last 30 days",
    "Compare arrival distribution across all crops",
    "What is the correlation between rainfall and arrivals?",
    "Show me the arrival trend in Amritsar mandi",
    "Top 10 mandis with highest delays",
    "Show monthly arrival trends for the last 3 months",
    "What crops have the most price crashes?",
]
