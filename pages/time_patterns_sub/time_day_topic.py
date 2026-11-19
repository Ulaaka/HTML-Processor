import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date
from html_parser import category_mapping
import plotly.express as px
import plotly.graph_objects as go

def time_day_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='data_range_time_day',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        html.P("Category:"),
        dcc.Dropdown(id='dropdown_time_day_category',
                options=['All'] + list(category_mapping.values()),
                value='All', clearable=False
        ),
        html.Br(),
        html.P("Video Type:"),
        dcc.Dropdown(id='dropdown_time_day_type',
                options=['All', 'Video', 'Reel', 'Unavailable'],
                value='All', clearable=False
        ),
        html.Br(),
        dcc.Graph(id='time_day_graph'),
        dbc.Accordion(id='time_day_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("time_day_graph", "figure"),
    Output("time_day_table", "children"),
    Input('dropdown_time_day_category', "value"),
    Input('dropdown_time_day_type', "value"),
    Input('data_range_time_day', "start_date"),
    Input('data_range_time_day', "end_date")


)
def update_graph(video_category, video_type, start_date, end_date):

    video_category = None if video_category == 'All' else video_category
    video_type = None if video_type == 'All' else video_type.lower()

    df = query.time_of_the_day(lower_range=start_date, upper_range=end_date, video_type=video_type, video_category=video_category)

    s = df.set_index("hour")["Total Count"].reindex(range(24), fill_value=0)
    figure = go.Figure(go.Barpolar(r=s.values, theta=[h * 15 + 7.5 for h in s.index], width=15,
                                hovertext=[f"{h}:00" for h in s.index], hoverinfo="text+r"))
    figure.update_layout(polar=dict(
        angularaxis=dict(direction="clockwise", rotation=90, tickvals=list(range(0, 360, 45)),
                         ticktext=[f"{h}:00" for h in range(0, 24, 3)]),
        radialaxis=dict(showticklabels=False, gridcolor="#e9ecef")))

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]