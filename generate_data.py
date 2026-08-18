"""
generate_data.py
-----------------
Generates a realistic synthetic Netflix titles dataset that mirrors the
schema of the popular Kaggle dataset "Netflix Movies and TV Shows"
(show_id, type, title, director, cast, country, date_added, release_year,
rating, duration, listed_in, description).

NOTE: This synthetic data is for you to test the pipeline end-to-end
immediately. For your real resume/portfolio submission, download the
actual dataset from Kaggle:
https://www.kaggle.com/datasets/shivamb/netflix-shows
and drop netflix_titles.csv in this same folder, then just re-run
analysis.py -- no other code changes needed since the schema matches.
"""

import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

countries = ["United States", "India", "United Kingdom", "Canada", "France",
             "Japan", "South Korea", "Spain", "Germany", "Australia",
             "Brazil", "Mexico", "Nigeria", "Italy", "Turkey"]

genres = ["Dramas", "Comedies", "Documentaries", "Action & Adventure",
          "International Movies", "Children & Family Movies", "Thrillers",
          "Romantic Movies", "Horror Movies", "Crime TV Shows",
          "Kids' TV", "Anime Series", "Reality TV", "Stand-Up Comedy",
          "Sci-Fi & Fantasy"]

ratings_movie = ["TV-MA", "TV-14", "TV-PG", "R", "PG-13", "PG", "TV-Y7", "TV-G"]

adjectives = ["Last", "Hidden", "Silent", "Broken", "Golden", "Lost", "Dark",
              "Endless", "Secret", "Final", "Forgotten", "Rising", "Wild"]
nouns = ["Kingdom", "Shadows", "Horizon", "Legacy", "Journey", "City",
         "Storm", "Empire", "Chronicles", "Dreams", "Heist", "Signal"]

n = 4000
rows = []
for i in range(1, n + 1):
    ttype = np.random.choice(["Movie", "TV Show"], p=[0.68, 0.32])
    release_year = np.random.choice(range(2000, 2026),
                                     p=np.array([1.02 ** y for y in range(26)]) /
                                       sum(1.02 ** y for y in range(26)))
    added_year = min(2026, release_year + np.random.randint(0, 4))
    added_month = np.random.randint(1, 13)
    country = np.random.choice(countries, p=[0.32, 0.10, 0.08, 0.06, 0.05,
                                              0.06, 0.05, 0.05, 0.04, 0.04,
                                              0.04, 0.04, 0.03, 0.02, 0.02])
    genre_count = np.random.randint(1, 3)
    listed_in = ", ".join(np.random.choice(genres, size=genre_count, replace=False))
    title = f"{np.random.choice(adjectives)} {np.random.choice(nouns)}"
    if ttype == "Movie":
        duration = f"{np.random.randint(70, 170)} min"
        rating = np.random.choice(ratings_movie)
    else:
        duration = f"{np.random.randint(1, 9)} Season" + ("s" if np.random.randint(1, 9) > 1 else "")
        rating = np.random.choice(ratings_movie)

    rows.append({
        "show_id": f"s{i}",
        "type": ttype,
        "title": title,
        "director": "Not Given" if np.random.rand() < 0.3 else f"Director {np.random.randint(1, 500)}",
        "cast": f"Actor {np.random.randint(1, 1000)}, Actor {np.random.randint(1, 1000)}",
        "country": country,
        "date_added": f"{added_month}/{np.random.randint(1,28)}/{added_year}",
        "release_year": int(release_year),
        "rating": rating,
        "duration": duration,
        "listed_in": listed_in,
        "description": "A gripping story that unfolds over time."
    })

df = pd.DataFrame(rows)
df.to_csv("netflix_titles.csv", index=False)
print(f"Generated {len(df)} rows -> netflix_titles.csv")
