import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import bar_graph, table
from datetime import date
from html_parser import category_mapping
import plotly.express as px

def busiest_weeks_layout():

    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='data_range_busiest_weeks',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        dcc.Slider(5, 20, 1, value=10, id='slider_busiest_weeks'),
        html.Br(),
        html.P("Show by:"),
        dcc.Dropdown(id='dropdown_busiest_weeks',
                options=['Category', 'Video Type'],
                value='Category', clearable=False
            ),
        html.Br(),
        dcc.Graph(id='busiest_weeks_graph'),
        dbc.Accordion(id='busiest_weeks_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("busiest_weeks_graph", "figure"),
    Output("busiest_weeks_table", "children"),
    Input('slider_busiest_weeks', "value"),
    Input('data_range_busiest_weeks', 'start_date'),
    Input('data_range_busiest_weeks', 'end_date'),
    Input('dropdown_busiest_weeks', 'value')
)
def update_graph(limit, start_date, end_date, chosen):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    df = query.most_watched_week(
        category_or_type=chosen,
        limit=limit,
        lower_range=start_date,
        upper_range=end_date,
    )
    figure = bar_graph(df, chosen, x_axis='Week' , y_axis='Sub Count', hover='Total Count')

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]