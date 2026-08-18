"""
app.py
------
Streamlit app: Netflix Content & Catalog Analytics — interactive dashboard.

Run locally:
    pip install streamlit pandas matplotlib
    streamlit run app.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Netflix Analytics Dashboard", page_icon="🎬", layout="wide")

st.title("🎬 Netflix Content & Catalog Analytics")
st.write(
    "Interactive dashboard exploring Netflix's content catalog — filter by "
    "country, genre, and year to explore content mix, growth trends, and ratings."
)

@st.cache_data
def load_data():
    return pd.read_csv("netflix_cleaned.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("netflix_cleaned.csv not found. Run `python3 analysis.py` first.")
    st.stop()

# ---------- Sidebar filters ----------
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

# ---------- KPI row ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Titles", len(filtered))
col2.metric("Movies", int((filtered["type"] == "Movie").sum()))
col3.metric("TV Shows", int((filtered["type"] == "TV Show").sum()))
top_country = filtered["country"].value_counts().idxmax() if len(filtered) else "N/A"
col4.metric("Top Country", top_country)

st.divider()

# ---------- Charts ----------
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

st.divider()
st.caption(
    "Built as a portfolio project — see the GitHub repo for the full "
    "analysis pipeline (data cleaning, SQL business queries)."
)
