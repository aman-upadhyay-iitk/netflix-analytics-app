"""
app.py
------
Streamlit app: Netflix Content & Catalog Analytics — interactive
dashboard + live SQL Insights tab.

Run locally:
    pip install streamlit pandas matplotlib
    streamlit run app.py
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Netflix Analytics Dashboard", page_icon="🎬", layout="wide")

st.title("🎬 Netflix Content & Catalog Analytics")
st.write(
    "Interactive dashboard exploring Netflix's content catalog, plus a live "
    "SQL Insights tab for business-question queries (SQLite engine)."
)

@st.cache_data
def load_data():
    return pd.read_csv("netflix_cleaned.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("netflix_cleaned.csv not found. Run `python3 analysis.py` first.")
    st.stop()

tab1, tab2 = st.tabs(["📊 Dashboard", "🗄️ SQL Insights"])

# ============================================================
# TAB 1: DASHBOARD (filters + charts)
# ============================================================
with tab1:
    st.sidebar.header("Filters")

    types = st.sidebar.multiselect("Content Type", options=sorted(df["type"].dropna().unique()),
                                    default=sorted(df["type"].dropna().unique()))

    countries = st.sidebar.multiselect(
        "Country", options=sorted(df["country"].dropna().unique())[:30],
        default=[]
    )

    year_min, year_max = int(df["release_year"].min()), int(df["release_year"].max())
    year_range = st.sidebar.slider("Release Year", year_min, year_max, (year_min, year_max))

    filtered = df[df["type"].isin(types)]
    if countries:
        filtered = filtered[filtered["country"].isin(countries)]
    filtered = filtered[
        (filtered["release_year"] >= year_range[0]) & (filtered["release_year"] <= year_range[1])
    ]

    st.sidebar.metric("Titles matching filters", len(filtered))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Titles", len(filtered))
    col2.metric("Movies", int((filtered["type"] == "Movie").sum()))
    col3.metric("TV Shows", int((filtered["type"] == "TV Show").sum()))
    top_country = filtered["country"].value_counts().idxmax() if len(filtered) else "N/A"
    col4.metric("Top Country", top_country)

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Content Growth by Year Added")
        growth = filtered.groupby("year_added").size()
        fig, ax = plt.subplots()
        ax.plot(growth.index, growth.values, marker="o", color="#E50914")
        ax.set_xlabel("Year Added")
        ax.set_ylabel("Titles")
        st.pyplot(fig)

    with c2:
        st.subheader("Top 10 Genres")
        top_genres = filtered["primary_genre"].value_counts().head(10).sort_values()
        fig, ax = plt.subplots()
        ax.barh(top_genres.index, top_genres.values, color="#221f1f")
        st.pyplot(fig)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Top 10 Countries")
        top_c = filtered["country"].value_counts().head(10).sort_values()
        fig, ax = plt.subplots()
        ax.barh(top_c.index, top_c.values, color="#E50914")
        st.pyplot(fig)

    with c4:
        st.subheader("Rating Distribution")
        rd = filtered["rating"].value_counts()
        fig, ax = plt.subplots()
        ax.bar(rd.index, rd.values, color="#221f1f")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    st.divider()
    st.subheader("Browse Titles")
    st.dataframe(
        filtered[["title", "type", "country", "release_year", "rating", "listed_in"]].head(200),
        use_container_width=True
    )

# ============================================================
# TAB 2: SQL INSIGHTS (runs real SQL queries live, via SQLite)
# ============================================================
with tab2:
    st.subheader("Live SQL Business Queries")
    st.write(
        "These queries run **live** against the dataset using SQL (SQLite engine) — "
        "the same queries are also in `netflix_queries.sql` for use in any SQL tool."
    )

    conn = sqlite3.connect(":memory:")
    df.to_sql("netflix", conn, index=False, if_exists="replace")

    queries = {
        "Content type split": """
            SELECT type, COUNT(*) AS count FROM netflix GROUP BY type ORDER BY count DESC;
        """,
        "Top 10 countries": """
            SELECT country, COUNT(*) AS titles FROM netflix GROUP BY country
            ORDER BY titles DESC LIMIT 10;
        """,
        "Content growth by year added": """
            SELECT year_added, COUNT(*) AS titles_added FROM netflix
            WHERE year_added IS NOT NULL GROUP BY year_added ORDER BY year_added;
        """,
        "Top 10 genres": """
            SELECT primary_genre, COUNT(*) AS count FROM netflix
            GROUP BY primary_genre ORDER BY count DESC LIMIT 10;
        """,
        "Rating distribution": """
            SELECT rating, COUNT(*) AS count FROM netflix GROUP BY rating ORDER BY count DESC;
        """,
        "Avg movie duration by release year": """
            SELECT release_year, ROUND(AVG(duration_minutes), 1) AS avg_duration
            FROM netflix WHERE type='Movie' AND duration_minutes IS NOT NULL
            GROUP BY release_year ORDER BY release_year;
        """,
    }

    query_choice = st.selectbox("Choose a business question", list(queries.keys()))
    result = pd.read_sql_query(queries[query_choice], conn)

    st.code(queries[query_choice].strip(), language="sql")
    st.dataframe(result, use_container_width=True)

    if result.shape[1] == 2 and result.shape[0] > 1:
        st.bar_chart(result.set_index(result.columns[0])[result.columns[1]])

st.divider()
st.caption(
    "Built as a portfolio project — see the GitHub repo for the full "
    "analysis pipeline (data cleaning, SQL business queries)."
)
