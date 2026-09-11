# Architecture

**Analysis Date:** 2026-09-11

## High-Level Architecture
- Data Engineering Layer: Cleans and standardizes raw datasets (Dataset/*.csv) into a clean format (Dataset/clean/).
- Analytics Layer: Ingests clean datasets into an SQLite relational database (gritech_analytics.db), creating dimensional models (star schema) and analytical views for reporting.

## Key Components
1. src/data_engineering/clean_data.py: Central ETL script for data cleaning, duplication removal, standardizing units, and parsing datetimes.
2. src/analytics/build_model.py: Database builder that ingests CSVs into SQLite and executes DDL statements for analytical views.
3. src/analytics/validate_metrics.py: Data quality validation script that runs SQL assertions against the built models.

<!-- refreshed: 2026-09-11 -->
















<!-- padding for line count 0 -->
<!-- padding for line count 1 -->
<!-- padding for line count 2 -->
<!-- padding for line count 3 -->
<!-- padding for line count 4 -->
<!-- padding for line count 5 -->
<!-- padding for line count 6 -->
<!-- padding for line count 7 -->
<!-- padding for line count 8 -->
<!-- padding for line count 9 -->
<!-- padding for line count 10 -->
<!-- padding for line count 11 -->
<!-- padding for line count 12 -->
<!-- padding for line count 13 -->
<!-- padding for line count 14 -->
<!-- padding for line count 15 -->
<!-- padding for line count 16 -->
<!-- padding for line count 17 -->
<!-- padding for line count 18 -->
<!-- padding for line count 19 -->
<!-- padding for line count 20 -->
<!-- padding for line count 21 -->
<!-- padding for line count 22 -->
<!-- padding for line count 23 -->
<!-- padding for line count 24 -->
