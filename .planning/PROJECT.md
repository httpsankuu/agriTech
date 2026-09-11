# Project: AgriTech - Mandi-to-Market Supply Chain Optimizer

## Vision
A data-driven platform for the State Agriculture Board to monitor daily crop arrivals at local Mandis, track prices against the Minimum Support Price (MSP), and correlate these metrics with weather data. The solution transforms chaotic, messy raw data into an actionable executive dashboard and includes a natural language AI agent for dynamic charting.

## Objectives
- **Data Rescue**: Cleanse datasets with mixed languages (English/Hindi crop names), inconsistent units (Quintals vs. KGs), and timezone mismatches.
- **Analytics Layer**: Establish structured models and metrics for daily arrivals, price trends, and weather correlations.
- **Dashboarding**: Build an interactive Streamlit dashboard for executives to monitor Mandi operations.
- **Agentic AI (Bonus)**: Develop an LLM-powered agent to answer natural language queries (e.g., "Plot the daily arrival trend of Wheat in Amritsar mandi vs MSP for the last 30 days") by generating and rendering the correct charts (Bar, Line, Scatter) along with text summaries.

## Core Audience
- State Agriculture Board Executives
- Mandi Administrators

## Tech Stack (Proposed)
- **Data Engineering**: Python, Pandas, DuckDB or SQL.
- **Dashboard**: Streamlit, Plotly.
- **AI Agent**: LangChain/LlamaIndex, OpenAI API / Local LLM, Plotly.
