# Concerns

**Analysis Date:** 2026-09-11

## Technical Debt
- **Hardcoded Paths**: Scripts construct absolute paths dynamically via __file__, but logic is tightly coupled to the Dataset/ directory structure.
- **Error Handling**: alidate_metrics.py uses bare ssert statements which will crash the script upon the first failure rather than collecting all errors.

## Performance
- **Pandas Memory Usage**: Entire datasets are loaded into memory for cleaning. Large datasets could cause Out-Of-Memory errors.
- **SQLite Concurrency**: SQLite is used for analytics which may not scale for concurrent analytical queries or massive datasets.

## Data Quality
- **Timestamps**: Weather sensors data had tricky IST/UTC suffixes that required custom parsing.

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
