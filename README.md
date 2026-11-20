# Burger Town Business Analytics Dashboard

A Streamlit dashboard built for the Software Developer Intern technical assessment. It analyses the supplied 300,000-row order-line dataset and provides interactive business metrics, charts, filters and CSV export.

## Live application
Add the deployed application URL here after deployment.

## Features
- KPI cards: revenue, unique orders, items sold, average order value and line-item count.
- Interactive date, outlet, menu category, order type and payment/settlement filters.
- Revenue trend, category revenue, order-type mix and outlet revenue charts.
- Top-item and payment/settlement summary tables.
- Download filtered data as CSV.
- Cached data loading to avoid re-reading and reprocessing the dataset on every interaction.

## Dataset and metric definitions
The source workbook contains 300,000 rows and 10 columns. Each row represents an order line item; a single bill can therefore appear on multiple rows.

- **Line revenue:** `Price × Quantity`.
- **Total revenue:** sum of line revenue across the filtered rows.
- **Orders:** distinct count of `BillNo`, not row count.
- **Items sold:** sum of `Quantity`.
- **Average order value:** total revenue divided by distinct orders.
- **Line items:** number of rows remaining after filters.

Dataset profile observed during development:
- 300,000 line-item records.
- 110,478 distinct bill numbers in the complete dataset.
- 6 outlets and 1 brand.
- 7 menu groups and 45 distinct items.
- Date range: 17 June 2025 to 16 June 2026.
- No missing values in the supplied columns.

## Architecture and data handling
This is a deliberately lightweight single-application architecture:

1. The supplied Excel workbook was converted to a compressed CSV (`data.csv.gz`) for deployment. CSV is simpler to read in the hosted environment and gzip reduces the repository payload.
2. Streamlit loads the compressed dataset with Pandas.
3. The data-loading function is cached with `st.cache_data`, so filter interactions reuse the loaded DataFrame rather than re-reading the file.
4. Pandas performs filtering and group-by aggregations on the selected rows.
5. Plotly renders interactive charts in the browser.

A separate database was not introduced. For this assessment's single-user/read-only analytical workflow, the dataset is static and fits comfortably in memory; a database would add setup and operational complexity without a clear benefit for the requested features. If the application needed concurrent users, frequent updates, row-level access control or much larger data, a database such as PostgreSQL would be a sensible next step. For an evolving production pipeline, ingestion, validation and scheduled refresh could be separated into an ETL process.

## Performance considerations and trade-offs
- Compressed CSV reduces the size of the deployed data file.
- Cached loading prevents repeated disk reads and parsing.
- Aggregations are performed after filters are applied.
- The dashboard does not render all 300,000 raw rows in a table by default.
- The design prioritises understandable calculations and a small deployment footprint over introducing unnecessary infrastructure.

## Run locally
Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The app opens at the local URL printed by Streamlit (usually `http://localhost:8501`).

## Deploy on Streamlit Community Cloud
1. Create a public GitHub repository and upload `app.py`, `requirements.txt`, `data.csv.gz` and this README.
2. Sign in to Streamlit Community Cloud using GitHub.
3. Create a new app, select the repository and branch, and set the main file path to `app.py`.
4. Deploy. Copy the live app URL into the Live application section above.

## Assumptions and limitations
- The supplied workbook's `Price` is treated as unit price and multiplied by `Quantity` to calculate line revenue, as described in the assessment.
- `BillNo` is treated as the order identifier.
- A filter applies to line items. If one bill contains line items that fall into different categories, selecting one category includes only the matching line items, while the distinct order count counts the bill once in that filtered result.
- The supplied data contains one brand, so a brand filter was not added.
- No authentication or write-back functionality is included because the assessment focuses on read-only analytics.

## Project structure
```text
california_burrito_dashboard/
├── app.py
├── data.csv.gz
├── requirements.txt
└── README.md
```
