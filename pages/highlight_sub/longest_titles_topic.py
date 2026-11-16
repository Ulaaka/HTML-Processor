
from queries.query_connection import query
import dash_bootstrap_components as dbc
from dash import html, Input, Output, dash_table, dcc, callback
from visual_functions import TABLE_STYLE, table, hbar
from datetime import date


def longest_titles_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='data_range_longest',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        html.H6("Rows to show:"),
        dcc.Slider(5, 40, 5, value=20, id='rows_to_show_longest'),
        html.Br(),
        dcc.Graph(id='longest_graph'),
        html.Br(),
        dbc.Accordion(id='table_longest', start_collapsed=True, flush=True)
    ])

@callback(
    Output('longest_graph', 'figure'),
    Output("table_longest", "children"),
    Input("rows_to_show_longest", "value"),
    Input('data_range_longest', 'start_date'),
    Input('data_range_longest', 'end_date')
)

def update_table(rows, start_date, end_date):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    df = query.the_longest_titled_video(video_limit=rows, lower_range=start_date, upper_range=end_date)

    return hbar(df, x ='Title Length', y="Name").update_layout(height=420), [dbc.AccordionItem(table(df), title="Show data")]