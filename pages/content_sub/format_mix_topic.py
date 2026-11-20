import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import table, pie_graph
from datetime import date
from html_parser import category_mapping

def format_mix_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Composition of Video Formats During Selected Period", body=True, className="mt-2"),
        html.Br(),
        dcc.DatePickerRange(
            id='data_range_format_mix',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        html.H6("Category:", className="content"),
        dcc.Dropdown(id='dropdown_format_fix',
                options=['All'] + list(category_mapping.values()),
                value='All', clearable=False
            ),
        html.Br(),
        dcc.Graph(id='format_mix_graph'),
        dbc.Accordion(id='format_mix_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("format_mix_graph", "figure"),
    Output("format_mix_table", "children"),
    Input('data_range_format_mix', 'start_date'),
    Input('data_range_format_mix', 'end_date'),
    Input('dropdown_format_fix', 'value')
)

def update_table(start_date, end_date, category):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    if category == 'All':
        category = None

    df = query.video_length_preference(video_category=category, lower_range=start_date, upper_range=end_date)

    figure = pie_graph(graph_df=df,value_col=df['Total Count'], name_col=df['Type'])

    return figure , [dbc.AccordionItem(table(df), title="Show data")]