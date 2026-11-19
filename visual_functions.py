
import plotly.express as px
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table

# ---- Table ----
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

def table(table_df, url=None, accordion = True, search = None):

    if url is None:
        url = []

    if not isinstance(url, (list, tuple, set)):
        url = [url]

    if search:
        table_df = table_df[table_df.astype(str).apply(lambda row: row.str.contains(search, case=False)).any(axis=1)]

    for c in table_df.columns:
        if pd.api.types.is_datetime64_any_dtype(table_df[c]):
            table_df[c] = table_df[c].dt.strftime("%Y-%m-%d %H:%M")

    for i in url:
                table_df[i] = table_df[i].map(lambda u: f"[open]({u})")

    cols = [{"name": str(c), "id": str(c), **({"presentation": "markdown"} if c in url else {})} for c in table_df.columns]

    if accordion:
        return dash_table.DataTable(data=table_df.to_dict("records"), columns=cols, **TABLE_STYLE)
    else:
        return table_df.to_dict("records"), cols

# --------  Graphs -------

def hbar(df, x, y, n=20, **kw):
    d = df.head(n).assign(_label=lambda t: t[y].map(short))
    fig = px.bar(d, x=x, y="_label", orientation="h", hover_name=y, **kw)
    fig.update_yaxes(autorange="reversed", title=None)
    return fig

def short(s, n=45):
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "…"

def generic_bar(graph_df, x_axis, y_axis, chosen):
    figure = px.bar(graph_df, x=x_axis, y=y_axis, color=chosen, barmode="group")
    return figure

def clock(df):
    s = df.set_index("hour")["Total Count"].reindex(range(24), fill_value=0)
    fig = go.Figure(go.Barpolar(r=s.values, theta=[h * 15 + 7.5 for h in s.index], width=15,
                                hovertext=[f"{h}:00" for h in s.index], hoverinfo="text+r"))
    fig.update_layout(polar=dict(
        angularaxis=dict(direction="clockwise", rotation=90, tickvals=list(range(0, 360, 45)),
                         ticktext=[f"{h}:00" for h in range(0, 24, 3)]),
        radialaxis=dict(showticklabels=False, gridcolor="#e9ecef")))
    return fig

def bar_graph(graph_df, chosen, x_axis, y_axis, hover, title = None):
    title = "" if title is None else title

    if not isinstance(hover, list):
        hover = [hover]


    figure = px.bar(
        graph_df,
        x=x_axis,
        y=y_axis,
        color=chosen,
        title=title,
        barmode='stack',
        hover_data=hover,
    )
    figure.update_xaxes(type='category')

    return figure

def line_graph(graph_df, chosen, title=None):
    title = "" if title is None else title

    figure = px.line(
        graph_df,
        markers=True,
        title=title,
        labels={"Hour": "Hour", "value": "Count", "variable": chosen},
    )

    figure.update_layout(
        xaxis=dict(tickmode="linear", dtick=1),
        template="plotly_white",
        legend_title_text=chosen,
    )

    return figure


def pie_graph(graph_df, value_col, name_col):
    figure = px.pie(graph_df, values=value_col, names=name_col, hole=.3)
    if graph_df.empty:
        figure = figure.add_annotation(text="No data for the selected filters", showarrow=False)
    return figure

def heatmap_graph(graph_df, x_label = "Week Number", y_label = "Week Day"):
    figure = px.imshow(
        graph_df,
        labels=dict(x=x_label, y=y_label, color_continuous_scale="Greens")
    )

    return figure


def streaks_graph(graph_df, x_start, x_end, y_axis, chosen):
   figure = px.timeline(graph_df, x_start=x_start, x_end=x_end, y=y_axis, color=chosen, color_continuous_scale="Blues")\
                    .update_yaxes(autorange="reversed", title=None)

   return figure


def scatter_graph(graph_df, x_axis, y_axis, size_value, hover_value):
    figure = px.scatter(graph_df, x=x_axis, y=y_axis, size=size_value, hover_name=hover_value, size_max=40)
    return figure
