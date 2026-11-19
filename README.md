<h1 align="center">YouTube Watch History Analyser</h1>

<p align="center">
  A Dash dashboard that turns your Google Takeout watch history into interactive charts.
</p>

<p align="center">
  <img alt="Dash" src="https://img.shields.io/badge/Dash-Plotly-3F4F75?logo=plotly&logoColor=white">
  <img alt="pandas" src="https://img.shields.io/badge/pandas-data%20processing-150458?logo=pandas&logoColor=white">
  <img alt="DuckDB" src="https://img.shields.io/badge/DuckDB-supported-FFF000?logo=duckdb&logoColor=black">
  <img alt="MySQL" src="https://img.shields.io/badge/MySQL-supported-4479A1?logo=mysql&logoColor=white">
</p>

<!-- Add a screenshot or GIF of the dashboard here, e.g.:
![Dashboard preview](docs/preview.png)
-->

Everything runs locally (the only thing sent out is the list of video IDs, to the YouTube Data API for durations and categories). Export your YouTube watch history, load it once, and explore what you watch, when you watch it, which channels you keep coming back to, and how your habits change over time.

**Pipeline:** parse the HTML → enrich every video through the YouTube Data API → store it in a database → query with SQL + pandas → plot with Dash.

## Table of contents

- [Key features](#key-features)
- [Project structure](#project-structure)
- [Installation](#installation)
- [Connecting to the database (2 ways)](#connecting-to-the-database-2-ways)
- [Usage](#usage)
- [Acknowledgements](#acknowledgements)
- [Conclusion](#conclusion)

---

## Key features

### Fast data ingestion

- **Async + batch requests.** Video IDs are sent to the YouTube Data API in batches of 50 (the API maximum), and the batches are fired concurrently with `aiohttp` + `asyncio` behind a semaphore (10 requests in flight). Batching cuts the number of calls dramatically, and going async on top of that cut the runtime by roughly another 20%.
- **HTML parsing with BeautifulSoup.** The Takeout file is large (~46 MB for my history), so it is parsed with `BeautifulSoup` + `lxml`, split into sections of 40 entries and processed in a `ThreadPoolExecutor`. Ads (entries marked `Details:`) and non-video links are skipped.
- **Enrichment.** Each video gets a duration (used to label it as a `video` or a `reel`, i.e. 3 minutes or shorter) and a category (Music, Gaming, Education, ...). Videos that have since been deleted or made private are kept and labelled `unavailable`.

### Two database options

| | DuckDB (default) | MySQL |
|---|---|---|
| **Type** | Embedded, column-oriented | Traditional client/server, row-oriented |
| **Setup** | None, the file `watch_history.duckdb` is created automatically | Needs a running server, a database and credentials in `.env` |
| **Good for** | Analytical queries (group-bys, windows, scans over a few columns) | Familiar setup, if you already run MySQL |
| **Code** | `DatabaseDuck` + `QueryProcessorDuck` | `Database` + `QueryProcessor` |

Both use the same `watch_history` schema and a `UNIQUE (video_url, time_stamp)` constraint, so re-importing the same file never creates duplicates (`INSERT IGNORE` in MySQL, `INSERT OR IGNORE` in DuckDB).

### Processing with pandas + SQL

SQL does the heavy lifting where it is naturally good at it (aggregations, `RANK() OVER (PARTITION BY ...)` for "top channel per month"), and pandas handles the rest (tokenising titles for the favourite-words chart, reshaping for heatmaps and trends, streak calculations).

> **Note:** Polars could be used instead of pandas, but for a dataset of this size (tens of thousands of rows) the difference would be negligible, so I stuck with pandas.

### Graphs, organised as a tree

The dashboard uses Dash multi-page routing. Each page has a sidebar, and each sidebar entry is its own graph.

```
Home
├── Highlights
│   ├── First watched
│   ├── Last watched
│   ├── Longest titles
│   └── Random day
├── Channels
│   ├── Most watched
│   ├── Channel of the month
│   ├── Forgotten favourites
│   └── Latest month
├── Content
│   ├── Most watched content
│   ├── Format mix (video vs reel)
│   ├── Format trend
│   ├── Heatmap
│   ├── Interests (categories)
│   ├── Favourite words
│   └── Unavailable videos
├── Time Patterns
│   ├── Time of day
│   ├── Day trend
│   ├── Last days
│   ├── Weeks trend
│   ├── Months trend
│   ├── Quarters trend
│   └── Years trend
└── Habits
    ├── Explorer
    ├── Busiest days
    ├── Busiest weeks
    ├── Weekend vs weekday
    └── Streaks
```

---

## Project structure

```
.
├── app.py                  # Dash entry point (navbar + page container)
├── requests.py             # YouTube Data API calls (async batch requests)
├── html_parser.py          # BeautifulSoup parsing + enrichment
├── html_processor.py       # Inserts the parsed list into DuckDB
├── query_connection.py     # Picks the database backend, exposes `query`
├── database/
│   ├── database_connection_duckdb.py
│   └── database_connection.py      # MySQL
├── queries/
│   ├── db_queries_duckdb.py
│   └── db_queries.py               # MySQL
├── database_creation       # MySQL schema (+ DuckDB translation)
├── pages/
│   ├── home.py
│   ├── highlight.py
│   ├── highlight_sub/      # one file per sidebar topic
│   ├── channels.py
│   ├── channels_sub/
│   ├── content.py
│   ├── content_sub/
│   ├── time_patterns.py
│   ├── time_patterns_sub/
│   ├── habits.py
│   └── habits_sub/
├── watch_history.duckdb    # created automatically on first run (git-ignored)
├── .env                    # create this yourself (git-ignored)
└── data_folder/            # create this yourself (git-ignored)
    └── watch-history.html  # your Takeout export
```

> `data_folder/`, `.env` and `*.duckdb` are listed in `.gitignore` because they hold personal data and secrets. They will **not** exist after you clone the repo, so you need to create them yourself (see [Installation](#installation)).

---

## Installation

### 1. Clone and install dependencies

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install dash dash-bootstrap-components pandas numpy nltk \
            beautifulsoup4 lxml python-dateutil aiohttp requests \
            python-decouple duckdb mysql-connector-python
```

`mysql-connector-python` is only needed if you choose the MySQL option.

Download the NLTK stop-word list once (used by the "favourite words" chart):

```bash
python -c "import nltk; nltk.download('stopwords')"
```

### 2. Get your watch history

1. Go to [Google Takeout](https://takeout.google.com/).
2. Deselect everything, then select **YouTube and YouTube Music**.
3. Under *All YouTube data included*, keep only **history**, and under *Multiple formats* set history to **HTML**.
4. Export and download the archive, then find `watch-history.html` inside it.
5. In the project root, create a folder called `data_folder` (it is git-ignored, so it is not included when you clone) and copy the file into it:

   ```bash
   mkdir data_folder
   cp /path/to/Takeout/YouTube\ and\ YouTube\ Music/history/watch-history.html data_folder/
   ```

   The code expects the file at exactly `data_folder/watch-history.html`.

### 3. Get a YouTube Data API key

Create a key in the [Google Cloud Console](https://console.cloud.google.com/) (enable **YouTube Data API v3**), then create a `.env` file in the project root (it is git-ignored, so it is not part of the repo):

```env
YOUTUBE_API=your_api_key_here

# Only needed for the MySQL option
DATABASE_HOST=localhost
DATABASE_USER=root
DATABASE_PASSWORD=your_password
DATABASE_NAME=youtube_database
```

> **Privacy:** your watch history is personal. `.env`, `data_folder/` and `*.duckdb` are already in `.gitignore`, so your API key, your history and your database stay on your machine. If you fork this repo, don't remove those entries.

---

## Connecting to the database (2 ways)

All the dashboard pages talk to the database through the `query` object created in `query_connection.py`, so switching backend is a change in that one file.

### Option 1: DuckDB (default, zero setup)

No server, no credentials. The database file `watch_history.duckdb` and the table are created automatically the first time `DatabaseDuck()` runs.

`query_connection.py`:

```python
from database.database_connection_duckdb import DatabaseDuck
from queries.db_queries_duckdb import QueryProcessorDuck

db = DatabaseDuck()
query = QueryProcessorDuck(db)
```

Load your history once. Create a small script called `load_data.py` in the project root (it reads `data_folder/watch-history.html`, so make sure that file is in place first):

```python
import os
from html_parser import HTML_Parser
from html_processor import HTML_Processor
from query_connection import db

parser = HTML_Parser(os.path.join("data_folder", "watch-history.html"))
HTML_Processor(parser.history_list, db)
```

```bash
python load_data.py
```

### Option 2: MySQL

**a) Create the database and table.** Run the MySQL block from the top of the `database_creation` file (everything above the "Translated to duckDB here" comment):

```sql
CREATE DATABASE IF NOT EXISTS youtube_database;
USE youtube_database;

CREATE TABLE IF NOT EXISTS watch_history (
    historyID      INT AUTO_INCREMENT PRIMARY KEY,
    video_url      VARCHAR(255) NOT NULL,
    video_name     VARCHAR(255) NOT NULL,
    video_type     VARCHAR(255) NOT NULL,
    video_category VARCHAR(255) NOT NULL,
    channel_url    VARCHAR(255) NOT NULL,
    channel_name   VARCHAR(255) NOT NULL,
    time_stamp     DATETIME,
    INDEX video_index (video_name),
    INDEX channel_date_index (channel_name, time_stamp)
);

ALTER TABLE watch_history
ADD UNIQUE KEY uq_video_time (video_url, time_stamp);
```

**b) Add your credentials** to `.env` (`DATABASE_HOST`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME`, see above).

**c) Point `query_connection.py` at the MySQL classes:**

```python
from queries.db_queries import QueryProcessor

query = QueryProcessor()   # opens the MySQL connection itself
```

**d) Load your history.** `HTML_Processor` is wired to DuckDB, so for MySQL call the insert directly:

```python
import os
from html_parser import HTML_Parser
from query_connection import query

parser = HTML_Parser(os.path.join("data_folder", "watch-history.html"))
query.insert_history(parser.history_list)
```

> Both processors read the table into a DataFrame when they start. If you load new data, restart the app so the pages see it.

---

## Usage

```bash
python load_data.py     # once, or whenever you have a new Takeout export
python app.py
```

Then open <http://127.0.0.1:8050>, pick a page from the navbar, and use the sidebar to switch between graphs. Most graphs also let you filter by date range, video type (`video` / `reel`) and category.

Re-running the loader with the same file is safe. Duplicate `(video_url, time_stamp)` rows are ignored.

---

## Acknowledgements

- The layout started from the simple Bootstrap navbar + container example in the [Dash Bootstrap Components docs](https://dash-bootstrap-components.opensource.faculty.ai/) (`dbc.NavbarSimple` with `dbc.Container`), combined with [Dash multi-page apps](https://dash.plotly.com/urls) (`use_pages=True`). I took that minimal skeleton and built the page tree, sidebars and every graph on top of it.
  <!-- TODO: replace the link above with the exact example page you started from -->
- The async batch-request approach is based on these two articles:
  - [aiohttp + asyncio vs requests: comparing Python HTTP libraries](https://dev.to/ashutoshsarangi/aiohttp-asyncio-vs-requests-comparing-python-http-libraries-46j9)
  - [Asynchronous HTTP requests with Python (GeeksforGeeks)](https://www.geeksforgeeks.org/python/asynchronous-http-requests-with-python/)

---

## Conclusion

This was a fun project. I got to work with async requests, scraping a big HTML export, two very different databases, and, best of all, Dash for building the graphs. It turned a pile of raw Takeout HTML into something I actually enjoy exploring.