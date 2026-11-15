
import calendar

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash import Dash, Input, Output, dash_table, dcc, html
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots

from database_connection_duckdb import DatabaseDuck
from db_queries_duckdb import QueryProcessorDuck
import os
from html_parser import HTML_Parser
from html_processor import HTML_Processor

db = DatabaseDuck()

"""parser  = HTML_Parser(os.path.join("data_folder", 'watch-history.html'))
processor = HTML_Processor(parser.history_list, db)"""
query = QueryProcessorDuck(db)

_T = query.table
YEARS = sorted(_T["time_stamp"].dt.year.unique().tolist(), reverse=True)
CATS = sorted(_T["video_category"].dropna().unique().tolist())
MONTHS = [{"label": calendar.month_abbr[m], "value": m} for m in range(1, 13)]

PALETTE = ["#0d6efd", "#6f42c1", "#d63384", "#fd7e14", "#198754", "#20c997", "#0dcaf0", "#6c757d"]
CHART_HEIGHT = 420


TABLE_STYLE = dict(
    page_size=10, sort_action="native", style_table={"overflowX": "auto"},
    style_header={"backgroundColor": "#f8f9fa", "fontWeight": "600", "border": "none",
                  "borderBottom": "1px solid #dee2e6"},
    style_cell={"border": "none", "borderBottom": "1px solid #f1f3f5", "padding": "8px 12px",
                "textAlign": "left", "fontFamily": "inherit", "fontSize": "0.9rem",
                "maxWidth": 320, "overflow": "hidden", "textOverflow": "ellipsis"},
)


def ctl(arg, kind, label, **kw):
    return dict(arg=arg, kind=kind, label=label, **kw)

DATES = [ctl("lower_range", "date", "From"), ctl("upper_range", "date", "To")]
VTYPE = ctl("video_type", "select", "Format", options=["video", "reel", "unavailable"], blank="All")
YEAR = ctl("year_choice", "select", "Year", options=YEARS, value=YEARS[0], cast=int, blank="Latest")
LIMIT = lambda n: ctl("video_limit", "number", "How many", value=n, cast=int, props=dict(min=1, max=100))

# ──────────────────────────────────────────────────────────── 4. CHARTS ──
def short(s, n=45):
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "…"

def hbar(df, x, y, n=20, **kw):
    """Horizontal ranking bar; long labels are shortened, full text shows on hover."""
    d = df.head(n).assign(_label=lambda t: t[y].map(short))
    fig = px.bar(d, x=x, y="_label", orientation="h", hover_name=y, **kw)
    fig.update_yaxes(autorange="reversed", title=None)
    return fig

def donut(df, names, values, n=12):
    return px.pie(df.head(n), names=names, values=values, hole=0.55)

def bar_line(df, x, bar, line):
    """Counts as bars + percentage change as a line on a second axis."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=df[x].astype(str), y=df[bar], name=bar)
    fig.add_scatter(x=df[x].astype(str), y=df[line], name=line, mode="lines+markers", secondary_y=True)
    fig.update_yaxes(title_text=line, secondary_y=True, showgrid=False)
    return fig

def hour_bar(df):
    s = df.set_index("Hour")["Total Count"].reindex(range(24), fill_value=0)
    fig = px.bar(x=s.index, y=s.values, labels={"x": "Hour of day", "y": "Videos"})
    fig.update_xaxes(dtick=1)
    return fig

def clock(df):
    """24h polar 'clock': one wedge per hour, 0:00 at the top."""
    s = df.set_index("hour")["Total Count"].reindex(range(24), fill_value=0)
    fig = go.Figure(go.Barpolar(r=s.values, theta=[h * 15 + 7.5 for h in s.index], width=15,
                                hovertext=[f"{h}:00" for h in s.index], hoverinfo="text+r"))
    fig.update_layout(polar=dict(
        angularaxis=dict(direction="clockwise", rotation=90, tickvals=list(range(0, 360, 45)),
                         ticktext=[f"{h}:00" for h in range(0, 24, 3)]),
        radialaxis=dict(showticklabels=False, gridcolor="#e9ecef")))
    return fig

def streaks(df):
    d = df.head(15).copy()
    d["Start"] = pd.to_datetime(d["Start"])
    d["End"] = pd.to_datetime(d["End"]) + pd.Timedelta(days=1)
    d["Streak"] = [f"#{i + 1} · {n} days" for i, n in enumerate(d["Total Days"])]
    fig = px.timeline(d, x_start="Start", x_end="End", y="Streak", color="Total Days",
                      color_continuous_scale="Blues")
    fig.update_yaxes(autorange="reversed", title=None)
    return fig

def week_label(s):
    return pd.to_datetime(s).dt.strftime("Week of %b %d")


CATEGORIES = [
    dict(id="highlights", path="/", title="Highlights", blurb="Firsts, lasts and oddities from your history."),
    dict(id="channels", path="/channels", title="Channels", blurb="Who you watch, and who you drifted away from."),
    dict(id="content", path="/content", title="Content", blurb="What you watch: videos, topics, words and formats."),
    dict(id="rhythm", path="/rhythm", title="Time patterns", blurb="When you watch: hours, weeks, seasons and years."),
    dict(id="habits", path="/habits", title="Habits", blurb="Busiest days, streaks and weekday vs weekend."),
]

ANALYSES = [
    dict(key="first", cat="highlights", title="First watched", fn="first_video_ever_watched",
         desc="The very first videos in your history.", controls=[LIMIT(5)]),
    dict(key="last", cat="highlights", title="Latest watched", fn="last_videos_ever_watched",
         desc="The most recent videos in your history.", controls=[LIMIT(5)]),
    dict(key="random", cat="highlights", title="Random day", fn="random_day_discovery",
         desc="Replay everything you watched on one randomly chosen day.",
         controls=[ctl(None, "button", "Surprise me")]),
    dict(key="titles", cat="highlights", title="Longest titles", fn="the_longest_titled_video",
         desc="Videos with the longest titles.", controls=[VTYPE, LIMIT(10)],
         chart=lambda d: hbar(d, "Title Length", "Name")),

    dict(key="top_channels", cat="channels", title="Most watched", fn="the_most_watched_channel",
         desc="Your top 20 channels of all time.", controls=[],
         chart=lambda d: hbar(d, "Total Watch", "Channel Name"),
         kpi=lambda d: [("Top channel", d["Channel Name"].iloc[0]), ("Videos", f"{d['Total Watch'].iloc[0]:,}")]),
    dict(key="monthly_champ", cat="channels", title="Channel of the month", fn="most_watched_channel_per_month",
         desc="The channel you watched most in each month.", controls=DATES,
         chart=lambda d: px.bar(d, x="Year - Month", y="Total Watch", color="Channel Name", barmode="group")),
    dict(key="unique", cat="channels", title="Latest month", fn="number_of_unique_channels_watched_month",
         desc="Channels you watched in the most recent month.", controls=[],
         chart=lambda d: hbar(d, "Total Count", "Channel Name", n=15),
         kpi=lambda d: [("Unique channels", f"{len(d):,}"), ("Most watched", d["Channel Name"].iloc[0])]),
    dict(key="neglected", cat="channels", title="Forgotten favourites", fn="the_longest_untouched_channel",
         desc="Channels you used to watch a lot and haven't opened for a while. "
              "Big bubbles = high neglect score (days since last watch × videos watched).",
         controls=DATES,
         chart=lambda d: px.scatter(d.head(150), x="Since Last Watched", y="Total Watch", size="Neglect Score",
                                    hover_name="Channel Name", size_max=40)),

    dict(key="videos", cat="content", title="Most watched videos", fn="the_most_watched_videos",
         desc="Videos you replayed the most.", controls=DATES,
         chart=lambda d: hbar(d, "Total Watch", "Video Name")),
    dict(key="words", cat="content", title="Favourite words", fn="the_most_repeated_words",
         desc="Words that show up most in the titles you watch.", controls=DATES,
         chart=lambda d: px.treemap(d, path=["Word"], values="Total Count")),
    dict(key="interests", cat="content", title="Interests", fn="interest_analysis",
         desc="Share of each category in the chosen period.",
         controls=[YEAR, ctl("month", "select", "Month", options=MONTHS, cast=int, blank="Whole year"), VTYPE],
         chart=lambda d: donut(d, "Video Category", "Total Count"),
         kpi=lambda d: [("Top interest", d["Video Category"].iloc[0])]),
    dict(key="format_mix", cat="content", title="Format mix", fn="video_length_preference",
         desc="Videos vs reels vs unavailable.", controls=DATES,
         chart=lambda d: donut(d, "Video Type", "Total Count")),
    dict(key="format_trend", cat="content", title="Format trend", fn="video_length_trend_over_month",
         desc="How the mix of formats changed month by month.", controls=[],
         chart=lambda d: px.bar(d.melt(id_vars="Video Type", var_name="Month", value_name="Videos"),
                                x="Month", y="Videos", color="Video Type")),
    dict(key="search", cat="content", title="Search titles", fn="return_by_name_combination",
         desc="Find videos whose title contains all the words you type.", need="sentence",
         controls=[ctl("sentence", "text", "Words", props=dict(placeholder="e.g. python tutorial")), *DATES]),
    dict(key="unavailable", cat="content", title="Unavailable", fn="unavailable_videos",
         desc="Videos that are no longer available.",
         controls=[ctl("category_type", "select", "Category", options=CATS, blank="All"), *DATES]),

    dict(key="daily", cat="rhythm", title="Day by hour", fn="daily_trend",
         desc="Hour-by-hour activity for one day. Leave the date empty for your latest day.",
         controls=[ctl("current_date", "date", "Day"), VTYPE], chart=hour_bar),
    dict(key="weekly", cat="rhythm", title="Weeks", fn="weekly_trend",
         desc="Videos per week over the last few weeks.",
         controls=[VTYPE, ctl("week_limit", "number", "Weeks", value=8, cast=int, props=dict(min=2, max=52))],
         chart=lambda d: px.bar(d.assign(Week=week_label(d["First Day"])), x="Week", y="Total Count")),
    dict(key="monthly", cat="rhythm", title="Months", fn="monthly_trend",
         desc="Videos per month, with the change versus the previous month.", controls=[YEAR, VTYPE],
         chart=lambda d: bar_line(d.assign(M=d["Month"].map(lambda m: calendar.month_abbr[m])),
                                  "M", "Total Count", "Change (%)")),
    dict(key="seasonal", cat="rhythm", title="Quarters", fn="seasonal_trend",
         desc="Videos per quarter, with the change versus the previous quarter.", controls=[YEAR, VTYPE],
         chart=lambda d: bar_line(d.assign(Q="Q" + d["Quarter"].astype(str)), "Q", "Total Count",
                                  "Change (Percentage%)")),
    dict(key="yearly", cat="rhythm", title="Years", fn="yearly_trend",
         desc="Videos per year, with the change versus the previous year.", controls=[VTYPE],
         chart=lambda d: bar_line(d, "Year", "Total Count", "Change (Percentage %)")),
    dict(key="hours", cat="rhythm", title="Time of day", fn="max_time_of_the_day",
         desc="Which hours of the day you watch the most.", controls=[*DATES, VTYPE], chart=clock),

    dict(key="busiest_day", cat="habits", title="Busiest days", fn="the_busiest_day",
         desc="Your 20 busiest days.", controls=DATES,
         chart=lambda d: px.bar(d.assign(Date=d["Date"].astype(str)), x="Date", y="Total Count", color="Day of Week"),
         kpi=lambda d: [("Busiest day", str(d["Date"].iloc[0])), ("Videos", f"{d['Total Count'].iloc[0]:,}")]),
    dict(key="busiest_week", cat="habits", title="Busiest weeks", fn="most_watched_week",
         desc="Weeks (Monday to Sunday) with the most videos.", controls=[*DATES, VTYPE],
         chart=lambda d: px.bar(d.head(15).assign(Week=week_label(d.head(15)["first_day"])), x="Week", y="Total Count")),
    dict(key="streaks", cat="habits", title="Streaks", fn="streak_analysis",
         desc="Runs of consecutive days with at least one video.", controls=DATES, chart=streaks,
         kpi=lambda d: [("Longest streak", f"{d['Total Days'].max()} days"), ("Streaks found", f"{len(d):,}")]),
    dict(key="weekend", cat="habits", title="Weekday vs weekend", fn="weekday_vs_weekend",
         desc="Average videos per weekday compared to per weekend day.", controls=DATES,
         chart=lambda d: px.bar(d.melt(id_vars="Video Type", var_name="Day type", value_name="Average"),
                                x="Video Type", y="Average", color="Day type", barmode="group")),
    dict(key="explorer", cat="habits", title="Explorer", fn="date_type_time_func",
         desc="Filter your history by format, time of day and category.",
         controls=[VTYPE, ctl("time", "select", "Time of day", options=["morning", "afternoon", "evening", "night"], blank="Any"),
                   ctl("category", "select", "Category", options=CATS, blank="All"), *DATES]),
]
SPECS = {s["key"]: s for s in ANALYSES}
PAGES = {c["path"]: c for c in CATEGORIES}

def cid(spec, c):
    return f"{spec['key']}-{c['arg'] or 'btn'}"

def widget(spec, c):
    k, i = c["kind"], cid(spec, c)
    if k == "select":
        opts = [o if isinstance(o, dict) else {"label": str(o), "value": o} for o in c["options"]]
        return dbc.Select(id=i, options=[{"label": c.get("blank", "All"), "value": ""}] + opts, value=c.get("value", ""))
    if k == "button":
        return dbc.Button(c["label"], id=i, color="primary", outline=True)
    return dbc.Input(id=i, type=k, value=c.get("value"), debounce=k in ("text", "number"), **c.get("props", {}))

def control(spec, c):
    label = dbc.Label(c["label"] if c["kind"] != "button" else "\u00a0", html_for=cid(spec, c))
    return dbc.Col([label, widget(spec, c)], xs=12, sm=6, md=3, className="control")

def kpi_card(label, value):
    return dbc.Col(dbc.Card(dbc.CardBody([html.Div(value, className="kpi-value"),
                                          html.Div(label, className="kpi-label")]), className="kpi"), md=3, sm=6)

def table(df):
    d = df.copy()
    for c in d.columns:
        if pd.api.types.is_datetime64_any_dtype(d[c]):
            d[c] = d[c].dt.strftime("%Y-%m-%d %H:%M")
    cols = [{"name": str(c), "id": str(c), **({"presentation": "markdown"} if c == "URL" else {})} for c in d.columns]
    if "URL" in d:
        d["URL"] = d["URL"].map(lambda u: f"[open]({u})")
    return dash_table.DataTable(data=d.to_dict("records"), columns=cols, **TABLE_STYLE)

def panel(spec):
    controls = spec["controls"]
    return html.Div([
        html.P(spec["desc"], className="text-muted"),
        dbc.Row([control(spec, c) for c in controls], className="controls g-3") if controls else None,
        dcc.Loading(html.Div(id=f"{spec['key']}-out", className="out"), type="dot"),
    ], className="panel")

def category_page(cat):
    specs = [s for s in ANALYSES if s["cat"] == cat["id"]]
    return html.Div([
        html.H2(cat["title"], className="display-6"),
        html.P(cat["blurb"], className="lead"),
        html.Hr(),
        dbc.Tabs([dbc.Tab(panel(s), label=s["title"], tab_id=s["key"]) for s in specs],
                 id=f"tabs-{cat['id']}", active_tab=specs[0]["key"]),
    ])

def render(spec, df):
    if df is None or df.empty:
        return dbc.Alert("No data for these filters. Try widening the date range or clearing a toggle.", color="light")
    out = []
    if spec.get("kpi"):
        out.append(dbc.Row([kpi_card(l, v) for l, v in spec["kpi"](df)], className="kpis g-3"))
    if spec.get("chart"):
        fig = spec["chart"](df).update_layout(height=CHART_HEIGHT)
        out += [dcc.Graph(figure=fig, config={"displayModeBar": False}),
                dbc.Accordion([dbc.AccordionItem(table(df), title="Show data")],
                              start_collapsed=True, flush=True, className="data-accordion")]
    else:
        out.append(table(df))
    return out

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,
           title="Watch History")

sidebar = html.Div([
    html.H2("Watch History", className="display-6"),
    html.Hr(),
    html.P("Explore what you watched, and when.", className="lead"),
    dbc.Nav([dbc.NavLink(c["title"], href=c["path"], active="exact") for c in CATEGORIES],
            vertical=True, pills=True),
], className="sidebar")

app.layout = html.Div([dcc.Location(id="url"), sidebar, html.Div(id="page-content", className="content")])


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(pathname):
    if pathname in PAGES:
        return category_page(PAGES[pathname])
    return html.Div([html.H1("404: Not found", className="text-danger"), html.Hr(),
                     html.P(f"The pathname {pathname} was not recognised.")])


def register(spec):
    """One callback per analysis. It only runs when its tab is the active one."""
    inputs = [Input(f"tabs-{spec['cat']}", "active_tab")] + [
        Input(cid(spec, c), "n_clicks" if c["kind"] == "button" else "value") for c in spec["controls"]]

    @app.callback(Output(f"{spec['key']}-out", "children"), inputs)
    def update(active, *values):
        if active != spec["key"]:
            raise PreventUpdate
        kwargs = {}
        for c, v in zip(spec["controls"], values):
            if c["arg"] is None:                      
                continue
            if v in ("", None):
                v = None
            elif c.get("cast"):
                v = c["cast"](v)
            elif c["arg"] == "upper_range":          
                v = f"{v} 23:59:59"
            kwargs[c["arg"]] = v
        if spec.get("need") and not kwargs.get(spec["need"]):
            return dbc.Alert(f"Fill in “{spec['need']}” to see results.", color="light")
        try:
            return render(spec, getattr(query, spec["fn"])(**kwargs))
        except Exception as e:                      
            return dbc.Alert(f"{spec['fn']} failed: {type(e).__name__}: {e}", color="danger")


for _spec in ANALYSES:
    register(_spec)

if __name__ == "__main__":
    app.run(debug=True, use_reloader = False)