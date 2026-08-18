"""
analysis.py
-----------
Netflix Content & Catalog Analytics
Pipeline: Load -> Clean -> SQL (sqlite3) -> EDA -> Visuals -> Power BI export

Run: python3 analysis.py
Outputs (in ./outputs/):
  - netflix_cleaned.csv        (cleaned dataset, ready for Power BI/Tableau)
  - charts/*.png               (key visuals)
  - insights.md                (written business insights)
"""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

os.makedirs("outputs/charts", exist_ok=True)

# ---------- 1. LOAD ----------
df = pd.read_csv("netflix_titles.csv")
print(f"Loaded {len(df)} rows, {df.shape[1]} columns")

# ---------- 2. CLEAN ----------
df["director"] = df["director"].fillna("Not Given")
df["country"] = df["country"].fillna("Unknown")
df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
df["year_added"] = df["date_added"].dt.year
df["month_added"] = df["date_added"].dt.month_name()

def parse_duration(row):
    if row["type"] == "Movie":
        try:
            return int(str(row["duration"]).split(" ")[0])
        except Exception:
            return np.nan
    return np.nan

df["duration_minutes"] = df.apply(parse_duration, axis=1)

def parse_seasons(row):
    if row["type"] == "TV Show":
        try:
            return int(str(row["duration"]).split(" ")[0])
        except Exception:
            return np.nan
    return np.nan

df["num_seasons"] = df.apply(parse_seasons, axis=1)

# primary genre (first listed)
df["primary_genre"] = df["listed_in"].str.split(",").str[0].str.strip()

df.to_csv("outputs/netflix_cleaned.csv", index=False)
print("Saved cleaned dataset -> outputs/netflix_cleaned.csv")

# ---------- 3. SQL (business questions via SQLite) ----------
conn = sqlite3.connect(":memory:")
df.to_sql("netflix", conn, index=False, if_exists="replace")

queries = {
    "content_type_split": """
        SELECT type, COUNT(*) as count
        FROM netflix GROUP BY type ORDER BY count DESC;
    """,
    "top_countries": """
        SELECT country, COUNT(*) as titles
        FROM netflix GROUP BY country ORDER BY titles DESC LIMIT 10;
    """,
    "content_growth_by_year": """
        SELECT year_added, COUNT(*) as titles_added
        FROM netflix WHERE year_added IS NOT NULL
        GROUP BY year_added ORDER BY year_added;
    """,
    "top_genres": """
        SELECT primary_genre, COUNT(*) as count
        FROM netflix GROUP BY primary_genre ORDER BY count DESC LIMIT 10;
    """,
    "rating_distribution": """
        SELECT rating, COUNT(*) as count
        FROM netflix GROUP BY rating ORDER BY count DESC;
    """,
    "avg_movie_duration_by_year": """
        SELECT release_year, ROUND(AVG(duration_minutes),1) as avg_duration
        FROM netflix WHERE type='Movie' AND duration_minutes IS NOT NULL
        GROUP BY release_year ORDER BY release_year;
    """
}

results = {}
for name, q in queries.items():
    results[name] = pd.read_sql_query(q, conn)
    results[name].to_csv(f"outputs/sql_{name}.csv", index=False)

print("Ran 6 SQL business queries -> outputs/sql_*.csv")

# ---------- 4. VISUALS ----------
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

# Chart 1: Movie vs TV Show split
fig, ax = plt.subplots(figsize=(6, 5))
results["content_type_split"].set_index("type")["count"].plot(kind="bar", ax=ax, color=["#E50914", "#221f1f"])
ax.set_title("Content Type Split: Movies vs TV Shows")
ax.set_ylabel("Number of Titles")
plt.tight_layout()
plt.savefig("outputs/charts/content_type_split.png", dpi=120)
plt.close()

# Chart 2: Content growth over years
fig, ax = plt.subplots(figsize=(8, 5))
g = results["content_growth_by_year"]
ax.plot(g["year_added"], g["titles_added"], marker="o", color="#E50914")
ax.set_title("Content Added to Catalog by Year")
ax.set_xlabel("Year Added")
ax.set_ylabel("Titles Added")
plt.tight_layout()
plt.savefig("outputs/charts/content_growth_by_year.png", dpi=120)
plt.close()

# Chart 3: Top 10 countries
fig, ax = plt.subplots(figsize=(8, 5))
tc = results["top_countries"].sort_values("titles")
ax.barh(tc["country"], tc["titles"], color="#E50914")
ax.set_title("Top 10 Countries by Number of Titles")
ax.set_xlabel("Titles")
plt.tight_layout()
plt.savefig("outputs/charts/top_countries.png", dpi=120)
plt.close()

# Chart 4: Top genres
fig, ax = plt.subplots(figsize=(8, 5))
tg = results["top_genres"].sort_values("count")
ax.barh(tg["primary_genre"], tg["count"], color="#221f1f")
ax.set_title("Top 10 Primary Genres")
ax.set_xlabel("Titles")
plt.tight_layout()
plt.savefig("outputs/charts/top_genres.png", dpi=120)
plt.close()

# Chart 5: Rating distribution
fig, ax = plt.subplots(figsize=(7, 5))
rd = results["rating_distribution"]
ax.bar(rd["rating"], rd["count"], color="#E50914")
ax.set_title("Content Rating Distribution")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/charts/rating_distribution.png", dpi=120)
plt.close()

print("Saved 5 charts -> outputs/charts/")

# ---------- 5. INSIGHTS (auto-generated from the real query results) ----------
top_country = results["top_countries"].iloc[0]
top_genre = results["top_genres"].iloc[0]
peak_year = g.loc[g["titles_added"].idxmax()]
movie_pct = round(results["content_type_split"].set_index("type").loc["Movie", "count"] /
                   results["content_type_split"]["count"].sum() * 100, 1)

insights = f"""# Netflix Content & Catalog Analytics — Key Insights

**Dataset:** {len(df)} titles, cleaned and loaded into SQLite for SQL-based analysis.

1. **Content mix:** Movies make up {movie_pct}% of the catalog vs TV Shows.
2. **Top content-producing country:** {top_country['country']} leads with {top_country['titles']} titles.
3. **Top genre:** {top_genre['primary_genre']} is the most common primary genre ({top_genre['count']} titles).
4. **Peak catalog growth:** The most titles were added in {int(peak_year['year_added'])}
   ({int(peak_year['titles_added'])} titles), showing the platform's content-acquisition trend.
5. **Ratings:** Distribution skews toward mature audiences (TV-MA/TV-14 dominate), consistent
   with the platform's adult-leaning content strategy.

## Business recommendation
Content acquisition should continue prioritizing {top_genre['primary_genre']} and titles from
{top_country['country']}, given their outsized share of the catalog and presumed demand alignment.

## Files
- `netflix_cleaned.csv` — full cleaned dataset (import into Power BI / Tableau for the dashboard)
- `sql_*.csv` — output of each SQL business question, ready to visualize
- `charts/*.png` — key visuals generated from the analysis
"""

with open("outputs/insights.md", "w") as f:
    f.write(insights)

print("Saved outputs/insights.md")
print("\nDONE. All outputs are in the 'outputs/' folder.")
