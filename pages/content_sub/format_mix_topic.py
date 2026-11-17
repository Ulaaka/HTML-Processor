import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date
import plotly.express as px
from html_parser import category_mapping
def format_mix_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        html.P("Date Range:"),
        dcc.DatePickerRange(
            id='data_range_format_mix',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        html.P("Category:"),
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

    pie_figure = px.pie(df, values=df['Total Count'], names=df['Type'], hole=.3)

    if df.empty:
        pie_figure = pie_figure.add_annotation(text="No data for the selected filters", showarrow=False)

    return pie_figure , [dbc.AccordionItem(table(df), title="Show data")]