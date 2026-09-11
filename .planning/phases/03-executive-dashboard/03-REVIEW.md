---
status: clean
files_reviewed: 6
critical: 0
warning: 4
info: 5
total: 9
---
# Code Review: Executive Dashboard

## Summary
The dashboard codebase is well-structured, modular, and utilizes Streamlit's caching mechanisms effectively. The separation of concerns between queries, layout/components, and charts is commendable. However, there are a few areas requiring attention, particularly regarding error handling for missing data, potential HTML injection, and UI styling stability.

## Findings

### Critical
*(None)*

### Warnings
1. **Fragile CSS Selectors** (`src/dashboard/styles.css`): Hardcoding Streamlit internal emotion cache classes (e.g., `.st-emotion-cache-10trblm`) is fragile because these hashes change across Streamlit versions. This will unexpectedly break typography overrides when Streamlit is updated. Stick to stable element selectors or Streamlit's officially supported theming options.
2. **Missing `dropna()` on Date Aggregation** (`src/dashboard/app.py`): When determining `min_date` and `max_date` from `all_dates`, calling `.min().date()` will raise an exception if `all_dates` contains `NaT` (Not a Time) values (e.g., missing data from SQL). Use `all_dates.dropna().min().date()` to prevent potential crashes on dirty data.
3. **Potential XSS Vulnerability in Custom Components** (`src/dashboard/components.py`): The `render_kpi` and `render_section_header` functions directly interpolate variables into raw HTML strings using f-strings. If database values or user inputs are eventually passed to these functions, it could enable Cross-Site Scripting (XSS). Use `html.escape()` from the standard library for interpolated variables.
4. **Hardcoded Column Assumptions** (`src/dashboard/charts.py`): `create_weather_impact_chart` expects columns named `daily_arrivals_qtl` and `total_rainfall_mm`. If the database view `vw_weather_impact` uses different names or if these columns are missing, it will throw a `KeyError`. Verify that these column names exactly match the SQLite view definition.

### Info / Best Practices
1. **Redundant Date Parsing** (`src/dashboard/app.py`, `src/dashboard/queries.py`): Dates are parsed using `pd.to_datetime()` on every single Streamlit rerun in `app.py`. For large datasets, this causes unnecessary lag on each UI interaction. It is more efficient to specify the `parse_dates` parameter directly in `pd.read_sql` within the `@st.cache_data` functions in `queries.py` so the overhead happens only once.
2. **Data Filtering Memory Overhead** (`src/dashboard/app.py`): The `filter_df` function calls `.copy()` on the entire DataFrame before applying filters. For large agricultural datasets, this unnecessarily spikes memory usage. It is more efficient to evaluate the boolean masks and slice the original DataFrame directly.
3. **Global Database Connection Handling** (`src/dashboard/queries.py`): Caching a single `sqlite3` connection globally with `check_same_thread=False` works for simple reads, but SQLite handles concurrency poorly in a multi-user context. Consider opening and closing connections within each data-fetching function or using SQLAlchemy.
4. **Streamlit Version Compatibility** (`src/dashboard/app.py`, `src/dashboard/components.py`): The use of `st.html()` requires Streamlit version >= 1.37. If you intend to deploy on older infrastructure, consider reverting to `st.markdown(..., unsafe_allow_html=True)`.
5. **External Font Dependencies** (`src/dashboard/styles.css`): Loading Google Fonts via `@import` introduces a third-party network request on load. For isolated, air-gapped deployments, or strict GDPR compliance, consider bundling the font files locally.
