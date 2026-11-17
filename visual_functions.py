
import plotly.express as px
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table, dcc, html
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc

TABLE_STYLE = dict(
    page_size=10, 
    sort_action="native", 
    style_table={"overflowX": "auto"},
    style_header={"backgroundColor": "#f8f9fa", "fontWeight": "600", "border": "none",
                  "borderBottom": "1px solid #dee2e6"},
    style_cell={"border": "none", "borderBottom": "1px solid #f1f3f5", "padding": "8px 12px",
                "textAlign": "left", "fontFamily": "inherit", "fontSize": "0.9rem",
                "maxWidth": 320, "overflow": "hidden", "textOverflow": "ellipsis"},
)

def short(s, n=45):
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "…"

def hbar(df, x, y, n=20, **kw):
    d = df.head(n).assign(_label=lambda t: t[y].map(short))
    fig = px.bar(d, x=x, y="_label", orientation="h", hover_name=y, **kw)
    fig.update_yaxes(autorange="reversed", title=None)
    return fig

def donut(df, names, values, n=12):
    return px.pie(df.head(n), names=names, values=values, hole=0.55)

def bar_line(df, x, bar, line):
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
    s = df.set_index("hour")["Total Count"].reindex(range(24), fill_value=0)
    fig = go.Figure(go.Barpolar(r=s.values, theta=[h * 15 + 7.5 for h in s.index], width=15,
                                hovertext=[f"{h}:00" for h in s.index], hoverinfo="text+r"))
    fig.update_layout(polar=dict(
        angularaxis=dict(direction="clockwise", rotation=90, tickvals=list(range(0, 360, 45)),
                         ticktext=[f"{h}:00" for h in range(0, 24, 3)]),
        radialaxis=dict(showticklabels=False, gridcolor="#e9ecef")))
    return fig

def streaks(df):
    d = df.copy()
    d["Start"] = pd.to_datetime(d["Start"])
    d["End"] = pd.to_datetime(d["End"]) + pd.Timedelta(days=1)
    d["Streak"] = [f"#{i + 1} · {n} days" for i, n in enumerate(d["Total Days"])]
    fig = px.timeline(d, x_start="Start", x_end="End", y="Streak", color="Total Days",
                      color_continuous_scale="Blues")
    fig.update_yaxes(autorange="reversed", title=None)
    return fig

def week_label(s):
    return pd.to_datetime(s).dt.strftime("Week of %b %d")

def table(df):
    d = df.copy()
    for c in d.columns:
        if pd.api.types.is_datetime64_any_dtype(d[c]):
            d[c] = d[c].dt.strftime("%Y-%m-%d %H:%M")
    cols = [{"name": str(c), "id": str(c), **({"presentation": "markdown"} if c == "URL" else {})} for c in d.columns]
    if "URL" in d:
        d["URL"] = d["URL"].map(lambda u: f"[open]({u})")
    return dash_table.DataTable(data=d.to_dict("records"), columns=cols, **TABLE_STYLE)

def graph(fig, df):
    return html.Div([
        dcc.Graph(figure=fig.update_layout(height=420)),
        dbc.Accordion([
            dbc.AccordionItem(table(df), title="Show data")
        ], start_collapsed=True, flush=True)
    ])