-- ============================================================
-- netflix_queries.sql
-- Standalone SQL business queries for the Netflix content
-- analytics project. Import netflix_cleaned.csv into any SQL
-- engine as a table named `netflix` and run these directly.
-- ============================================================

-- 1. Content type split
SELECT type, COUNT(*) AS count
FROM netflix
GROUP BY type
ORDER BY count DESC;

-- 2. Top 10 countries by title count
SELECT country, COUNT(*) AS titles
FROM netflix
GROUP BY country
ORDER BY titles DESC
LIMIT 10;

-- 3. Content growth by year added (catalog expansion trend)
SELECT year_added, COUNT(*) AS titles_added
FROM netflix
WHERE year_added IS NOT NULL
GROUP BY year_added
ORDER BY year_added;

-- 4. Top 10 genres
SELECT primary_genre, COUNT(*) AS count
FROM netflix
GROUP BY primary_genre
ORDER BY count DESC
LIMIT 10;

-- 5. Rating distribution (audience skew)
SELECT rating, COUNT(*) AS count
FROM netflix
GROUP BY rating
ORDER BY count DESC;

-- 6. Average movie duration trend by release year
SELECT release_year, ROUND(AVG(duration_minutes), 1) AS avg_duration
FROM netflix
WHERE type = 'Movie' AND duration_minutes IS NOT NULL
GROUP BY release_year
ORDER BY release_year;

-- 7. Country x Genre cross-tab (top genre per top 5 countries)
SELECT country, primary_genre, COUNT(*) AS titles
FROM netflix
WHERE country IN (
    SELECT country FROM netflix GROUP BY country ORDER BY COUNT(*) DESC LIMIT 5
)
GROUP BY country, primary_genre
ORDER BY country, titles DESC;

-- 8. Year-over-year catalog growth rate (%)
WITH yearly AS (
    SELECT year_added, COUNT(*) AS titles
    FROM netflix
    WHERE year_added IS NOT NULL
    GROUP BY year_added
)
SELECT
    year_added,
    titles,
    ROUND(
        100.0 * (titles - LAG(titles) OVER (ORDER BY year_added))
        / LAG(titles) OVER (ORDER BY year_added), 2
    ) AS yoy_growth_pct
FROM yearly
ORDER BY year_added;
