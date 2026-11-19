\documentclass[11pt,a4paper]{article}

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[margin=2.5cm]{geometry}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{enumitem}
\usepackage{listings}
\usepackage{array}
\usepackage[hidelinks]{hyperref}

\definecolor{codebg}{HTML}{F5F5F5}
\definecolor{codeframe}{HTML}{CCCCCC}
\definecolor{linkblue}{HTML}{1A5FB4}
\hypersetup{colorlinks=true, urlcolor=linkblue, linkcolor=linkblue}

\newcommand{\code}[1]{\texttt{\detokenize{#1}}}

\lstset{
  basicstyle=\ttfamily\small,
  backgroundcolor=\color{codebg},
  frame=single,
  rulecolor=\color{codeframe},
  breaklines=true,
  columns=fullflexible,
  keepspaces=true,
  showstringspaces=false,
  xleftmargin=0.5em,
  xrightmargin=0.5em,
  aboveskip=0.8em,
  belowskip=0.8em
}

\lstdefinelanguage{env}{
  morecomment=[l]{\#},
}

\setlength{\parindent}{0pt}
\setlength{\emergencystretch}{3em}
\setlength{\parskip}{0.6em}
\setlist{itemsep=0.2em, topsep=0.3em}

\title{\textbf{YouTube Watch History Analyser}}
\author{}
\date{}

\begin{document}

\maketitle
\vspace{-2em}

A Dash dashboard that turns your Google Takeout YouTube watch history (\code{watch-history.html}) into interactive charts: what you watch, when you watch it, which channels you keep coming back to, and how your habits change over time.

The pipeline is: \textbf{parse the HTML $\rightarrow$ enrich every video through the YouTube Data API $\rightarrow$ store it in a database $\rightarrow$ query with SQL + pandas $\rightarrow$ plot with Dash.}

\tableofcontents
\newpage

%--------------------------------------------------------------------
\section{Key Features}

\subsection{Fast data ingestion}
\begin{itemize}
  \item \textbf{Async + batch requests.} Video IDs are sent to the YouTube Data API in batches of 50 (the API maximum), and the batches are fired concurrently with \code{aiohttp} + \code{asyncio} behind a semaphore (10 requests in flight). Batching cuts the number of calls dramatically, and going async on top of that cut the runtime by roughly another 20\%.
  \item \textbf{HTML parsing with BeautifulSoup.} The Takeout file is large (about 46~MB for my history), so it is parsed with \code{BeautifulSoup} + \code{lxml}, split into sections of 40 entries and processed in a \code{ThreadPoolExecutor}. Ads (entries marked \code{Details:}) and non-video links are skipped.
  \item \textbf{Enrichment.} Each video gets a duration (used to label it as a \code{video} or a \code{reel}, i.e.\ 3 minutes or shorter) and a category (Music, Gaming, Education, \ldots). Videos that have since been deleted or made private are kept and labelled \code{unavailable}.
\end{itemize}

\subsection{Two database options}

\begin{center}
\small
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{2.2cm}>{\raggedright\arraybackslash}p{5.8cm}>{\raggedright\arraybackslash}p{5.8cm}@{}}
\toprule
 & \textbf{DuckDB (default)} & \textbf{MySQL} \\
\midrule
Type & Embedded, column-oriented & Traditional client/server, row-oriented \\
Setup & None; the file \code{watch_history.duckdb} is created automatically & Needs a running server, a database and credentials in \code{.env} \\
Good for & Analytical queries (group-bys, windows, scans over a few columns) & Familiar setup, if you already run MySQL \\
Code & \code{DatabaseDuck} + \code{QueryProcessorDuck} & \code{Database} + \code{QueryProcessor} \\
\bottomrule
\end{tabular}
\end{center}

Both use the same \code{watch_history} schema and a \code{UNIQUE (video_url, time_stamp)} constraint, so re-importing the same file never creates duplicates (\code{INSERT IGNORE} in MySQL, \code{INSERT OR IGNORE} in DuckDB).

\subsection{Processing with pandas + SQL}
SQL does the heavy lifting where it is naturally good at it (aggregations, \code{RANK() OVER (PARTITION BY ...)} for ``top channel per month''), and pandas handles the rest (tokenising titles for the favourite-words chart, reshaping for heatmaps and trends, streak calculations).

\begin{quote}
Polars could be used instead of pandas, but for a dataset of this size (tens of thousands of rows) the difference would be negligible, so I stuck with pandas.
\end{quote}

\subsection{Graphs, organised as a tree}
The dashboard uses Dash multi-page routing. Each page has a sidebar, and each sidebar entry is its own graph/topic.

\begin{lstlisting}
Home
|-- Highlights
|   |-- First watched
|   |-- Last watched
|   |-- Longest titles
|   `-- Random day
|-- Channels
|   |-- Most watched
|   |-- Channel of the month
|   |-- Forgotten favourites
|   `-- Latest month
|-- Content
|   |-- Most watched content
|   |-- Format mix (video vs reel)
|   |-- Format trend
|   |-- Heatmap
|   |-- Interests (categories)
|   |-- Favourite words
|   `-- Unavailable videos
|-- Time Patterns
|   |-- Time of day
|   |-- Day trend
|   |-- Last days
|   |-- Weeks trend
|   |-- Months trend
|   |-- Quarters trend
|   `-- Years trend
`-- Habits
    |-- Explorer
    |-- Busiest days
    |-- Busiest weeks
    |-- Weekend vs weekday
    `-- Streaks
\end{lstlisting}

%--------------------------------------------------------------------
\section{Project Structure}

\begin{lstlisting}
.
|-- app.py                  # Dash entry point (navbar + page container)
|-- requests.py             # YouTube Data API calls (async batch requests)
|-- html_parser.py          # BeautifulSoup parsing + enrichment
|-- html_processor.py       # Inserts the parsed list into DuckDB
|-- query_connection.py     # Picks the database backend, exposes `query`
|-- database/
|   |-- database_connection_duckdb.py
|   `-- database_connection.py          # MySQL
|-- queries/
|   |-- db_queries_duckdb.py
|   `-- db_queries.py                   # MySQL
|-- database_creation       # MySQL schema (+ DuckDB translation)
|-- pages/                  # One file per page + one sub-folder per sidebar
|   |-- home.py
|   |-- highlight.py        + highlight_sub/
|   |-- channels.py         + channels_sub/
|   |-- content.py          + content_sub/
|   |-- time_patterns.py    + time_patterns_sub/
|   `-- habits.py           + habits_sub/
`-- data_folder/
    `-- watch-history.html  # your Takeout export (not committed)
\end{lstlisting}

%--------------------------------------------------------------------
\section{Installation}

\subsection{Clone and install dependencies}

\begin{lstlisting}[language=bash]
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install dash dash-bootstrap-components pandas numpy nltk \
            beautifulsoup4 lxml python-dateutil aiohttp requests \
            python-decouple duckdb mysql-connector-python
\end{lstlisting}

\code{mysql-connector-python} is only needed if you choose the MySQL option.

Download the NLTK stop-word list once (used by the ``favourite words'' chart):

\begin{lstlisting}[language=bash]
python -c "import nltk; nltk.download('stopwords')"
\end{lstlisting}

\subsection{Get your watch history}
\begin{enumerate}
  \item Go to \href{https://takeout.google.com/}{Google Takeout}.
  \item Deselect everything, then select \textbf{YouTube and YouTube Music}.
  \item Under \emph{All YouTube data included}, keep only \textbf{history}, and under \emph{Multiple formats} set history to \textbf{HTML}.
  \item Export, download, and copy \code{watch-history.html} into \code{data_folder/}.
\end{enumerate}

\subsection{Get a YouTube Data API key}
Create a key in the \href{https://console.cloud.google.com/}{Google Cloud Console} (enable \textbf{YouTube Data API v3}), then create a \code{.env} file in the project root:

\begin{lstlisting}[language=env]
YOUTUBE_API=your_api_key_here

# Only needed for the MySQL option
DATABASE_HOST=localhost
DATABASE_USER=root
DATABASE_PASSWORD=your_password
DATABASE_NAME=youtube_database
\end{lstlisting}

\begin{quote}
Your watch history is personal. Add \code{.env}, \code{data_folder/} and \code{*.duckdb} to your \code{.gitignore}.
\end{quote}

%--------------------------------------------------------------------
\section{Connecting to the Database (2 Ways)}

All the dashboard pages talk to the database through the \code{query} object created in \code{query_connection.py}, so switching backend is a change in that one file.

\subsection{Option 1: DuckDB (default, zero setup)}

No server, no credentials. The database file \code{watch_history.duckdb} and the table are created automatically the first time \code{DatabaseDuck()} runs.

\code{query_connection.py}:

\begin{lstlisting}[language=Python]
from database.database_connection_duckdb import DatabaseDuck
from queries.db_queries_duckdb import QueryProcessorDuck

db = DatabaseDuck()
query = QueryProcessorDuck(db)
\end{lstlisting}

Load your history once with a small script (\code{load_data.py}):

\begin{lstlisting}[language=Python]
import os
from html_parser import HTML_Parser
from html_processor import HTML_Processor
from query_connection import db

parser = HTML_Parser(os.path.join("data_folder", "watch-history.html"))
HTML_Processor(parser.history_list, db)
\end{lstlisting}

\begin{lstlisting}[language=bash]
python load_data.py
\end{lstlisting}

\subsection{Option 2: MySQL}

\textbf{a) Create the database and table.} Run the MySQL block from the top of the \code{database_creation} file (everything above the ``Translated to duckDB here'' comment):

\begin{lstlisting}[language=SQL]
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
\end{lstlisting}

\textbf{b) Add your credentials} to \code{.env} (\code{DATABASE_HOST}, \code{DATABASE_USER}, \code{DATABASE_PASSWORD}, \code{DATABASE_NAME}, see above).

\textbf{c) Point \code{query_connection.py} at the MySQL classes:}

\begin{lstlisting}[language=Python]
from queries.db_queries import QueryProcessor

query = QueryProcessor()   # opens the MySQL connection itself
\end{lstlisting}

\textbf{d) Load your history.} \code{HTML_Processor} is wired to DuckDB, so for MySQL call the insert directly:

\begin{lstlisting}[language=Python]
import os
from html_parser import HTML_Parser
from query_connection import query

parser = HTML_Parser(os.path.join("data_folder", "watch-history.html"))
query.insert_history(parser.history_list)
\end{lstlisting}

\begin{quote}
Both processors read the table into a DataFrame when they start. If you load new data, restart the app so the pages see it.
\end{quote}

%--------------------------------------------------------------------
\section{Usage}

\begin{lstlisting}[language=bash]
python load_data.py     # once, or whenever you have a new Takeout export
python app.py
\end{lstlisting}

Then open \url{http://127.0.0.1:8050}, pick a page from the navbar, and use the sidebar to switch between graphs. Most graphs also let you filter by date range, video type (\code{video} / \code{reel}) and category.

Re-running the loader with the same file is safe. Duplicate \code{(video_url, time_stamp)} rows are ignored.

%--------------------------------------------------------------------
\section{Acknowledgements}

\begin{itemize}
  \item The layout started from the simple Bootstrap navbar + container example in the \href{https://dash-bootstrap-components.opensource.faculty.ai/}{Dash Bootstrap Components docs} (\code{dbc.NavbarSimple} with \code{dbc.Container}), combined with \href{https://dash.plotly.com/urls}{Dash multi-page apps} (\code{use_pages=True}). I took that minimal skeleton and built the page tree, sidebars and every graph on top of it.
  % TODO: replace the link above with the exact example page you started from
  \item The async batch-request approach is based on these two articles:
  \begin{itemize}
    \item \href{https://dev.to/ashutoshsarangi/aiohttp-asyncio-vs-requests-comparing-python-http-libraries-46j9}{aiohttp + asyncio vs requests: comparing Python HTTP libraries}
    \item \href{https://www.geeksforgeeks.org/python/asynchronous-http-requests-with-python/}{Asynchronous HTTP requests with Python (GeeksforGeeks)}
  \end{itemize}
\end{itemize}

%--------------------------------------------------------------------
\section{Conclusion}

This was a fun project. I got to work with async requests, scraping a big HTML export, two very different databases, and, best of all, Dash for building the graphs. It turned a pile of raw Takeout HTML into something I actually enjoy exploring.

\end{document}