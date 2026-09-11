# Phase 2 Final Analytics Audit Report

**Date:** 2026-09-11
**Verdict:** **PASS**

## 1. Weather Join Validation
- **Logic Validated:** The SQL safely aggregates `fact_weather` to a daily grain (MAX temp, SUM rainfall) grouped by `mandi_num` and `date_str` BEFORE performing a `LEFT JOIN` onto `fact_arrivals`.
- **Many-to-Many Check:** No row multiplication occurs. The DailyWeather CTE contains 8,400 unique mandi/date combinations (down from 15,000 raw sensor readings).
- **Inflation Check:** Total arrivals in the raw fact table (`5,659,184.82 Qtl`) perfectly matches the total arrivals in the `vw_weather_impact` view (`5,659,184.82 Qtl`). No inflation.
- **Coverage:** 
  - 12,313 unique arrival days exist.
  - 6,312 arrival days successfully matched with weather data.
  - 6,001 arrival days had no weather data (retained with NULL weather).
  - 1,851 weather days had no arrivals (correctly excluded from arrival-centric impact view).

## 2. Arrival Metric Grain
- **Grain Check:** `vw_crop_summary` correctly aggregates at the `crop_name + date + mandi_id` level.
- **Uniqueness:** 0 duplicates at this grain.
- **Reconciliation:** Total volume matches the source table exactly (`5,659,184.82 Qtl`).

## 3. Price / MSP Validation
- **Data Completeness:** 12,000 total price records. 610 missing `modal_price` and 2,377 missing `msp` values. These propagate safely as `NULL` during calculations.
- **Crash Logic:** The `is_price_crash` flag evaluates to `1` strictly when `modal_price < msp`. This yielded 3,924 crash instances, confirmed perfectly against a boolean numerical check.

## 4. Transport Performance
- **Exclusion of Invalid Data:** 539 invalid trips (negative transit time) and ~1,000 missing transit times were explicitly excluded via `transit_hours_clean IS NOT NULL` across all route baselines and calculations.
- **Delay Threshold:** A robust 1.5x route-average multiplier was used.
- **Route Sufficiency:** 342 unique routes exist. The minimum sample size per route is 12 trips, ensuring no misleading 100% delay rates from single-trip routes.
- **Result:** 1,584 delayed trips detected out of 8,455 valid trips (18.68% overall delay rate).

## 5. Trends & Time-Series
- Daily (`YYYY-MM-DD`), Weekly (`YYYY-WW`), and Monthly (`YYYY-MM`) string aggregations evaluate correctly and strictly preserve chronological order for the dashboard.

## 6. Reconciliation Counts
- **fact_arrivals:** 25,000 rows
- **fact_prices:** 12,000 rows
- **fact_logistics:** 10,000 rows
- **fact_weather:** 15,000 rows
- **dim_mandi:** 57 rows
- **Unique Crops:** 6

**Conclusion:** The Phase 2 analytics layer is robust, mathematically sound, and ready to serve Phase 3 (Dashboard Development) with accurate data.
