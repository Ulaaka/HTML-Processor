import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import bar_graph, table
from datetime import date
from html_parser import category_mapping
import plotly.express as px


def busiest_days_layout():

    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='data_range_busiest_days',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        dcc.Slider(5, 20, 1, value=10, id='slider_busiest_days'),
        html.Br(),
        html.P("Show by:"),
        dcc.Dropdown(id='dropdown_busiest_days',
                options=['Category', 'Video Type'],
                value='Category', clearable=False
            ),
        html.Br(),
        dcc.Graph(id='busiest_days_graph'),
        dbc.Accordion(id='busiest_days_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("busiest_days_graph", "figure"),
    Output("busiest_days_table", "children"),
    Input('slider_busiest_days', "value"),
    Input('data_range_busiest_days', 'start_date'),
    Input('data_range_busiest_days', 'end_date'),
    Input('dropdown_busiest_days', 'value')
)
def update_graph(limit, start_date, end_date, chosen):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    df = query.the_busiest_day(
        category_or_type=chosen,
        limit=limit,
        lower_range=start_date,
        upper_range=end_date,
    )
    figure = bar_graph(df, chosen, x_axis='Date' , y_axis='Sub Count', hover=['Total Count', 'Day of Week'])

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]