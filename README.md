# Netflix Content & Catalog Analytics

An end-to-end data analytics project: cleaning, SQL-based business
querying, and dashboard-ready exports for Netflix's content catalog.

## What this does
- Cleans raw title data (nulls, dates, parsed durations/seasons)
- Runs 6 business-relevant SQL queries (via SQLite) — content mix,
  top countries, genre trends, catalog growth by year, ratings, duration trends
- Generates 5 visual charts summarizing the findings
- Exports a clean CSV ready to plug into **Power BI / Tableau** for an
  interactive dashboard
- Auto-generates a written insights summary from the real query results

## How to run
```bash
pip install pandas numpy matplotlib
python3 generate_data.py   # creates netflix_titles.csv (synthetic, for testing)
python3 analysis.py        # runs the full pipeline -> outputs/
```

## ⚠️ Before you use this for your resume/portfolio
`generate_data.py` creates a **synthetic** dataset so you can test the
whole pipeline right now. For a real, credible project:
1. Download the actual Kaggle dataset: **"Netflix Movies and TV Shows"**
   → https://www.kaggle.com/datasets/shivamb/netflix-shows
2. Save it as `netflix_titles.csv` in this folder (same column names, so no code changes needed)
3. Re-run `python3 analysis.py`
4. Open `outputs/netflix_cleaned.csv` in Power BI, build 3-4 visuals
   (the chart PNGs in `outputs/charts/` show you what to build), and
   take a screenshot of your dashboard for your resume/GitHub

## What to write on your resume
> Analyzed Netflix's content catalog using Python (Pandas) and SQL;
> cleaned and queried 8,800+ titles to surface content-mix, genre, and
> regional trends, and built an interactive Power BI dashboard
> presenting catalog growth and content strategy insights.

## Folder structure
```
netflix_project/
├── generate_data.py       # synthetic data generator (swap for real Kaggle CSV)
├── analysis.py            # full pipeline: clean -> SQL -> charts -> insights
├── README.md
└── outputs/
    ├── netflix_cleaned.csv
    ├── insights.md
    ├── sql_*.csv           (6 files, one per business question)
    └── charts/             (5 PNG visuals)
```

## SQL Analysis
Includes standalone SQL queries (`netflix_queries.sql`) covering business questions like content growth trends and country-genre breakdowns.
