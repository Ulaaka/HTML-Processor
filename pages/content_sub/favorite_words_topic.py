import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date
from html_parser import category_mapping
def favorite_words_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='data_range_most_repeated_words',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        html.H6("Words to show:"),
        dcc.Slider(5, 40, 5, value=20, id='slider_most_repeated_words'),
        html.Br(),
        html.P("Category:"),
        dcc.Dropdown(id='dropdown_favorite_words_category',
                options=['All'] + list(category_mapping.values()),
                value='All', clearable=False
        ),
        html.Br(),
        html.P("Video Type:"),
        dcc.Dropdown(id='dropdown_favorite_words_type',
                options=['All', 'Video', 'Reel', 'Unavailable'],
                value='All', clearable=False
        ),
        dcc.Graph(id='most_repeated_words_graph'),
        dbc.Accordion(id='most_repeated_words_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("most_repeated_words_graph", "figure"),
    Output("most_repeated_words_table", "children"),
    Input('slider_most_repeated_words', "value"),
    Input('data_range_most_repeated_words', 'start_date'),
    Input('data_range_most_repeated_words', 'end_date'),
    Input('dropdown_favorite_words_category', 'value'),
    Input('dropdown_favorite_words_type', 'value')
)

def update_table(value, start_date, end_date, video_category, video_type):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    if video_category == 'All':
        video_category = None

    if video_type == 'All':
        video_type = None
    else:
        video_type = video_type.lower()

    df = query.the_most_repeated_words(limit=value, video_type=video_type, video_category=video_category, lower_range=start_date, upper_range=end_date)

    return hbar(df, x ='Total Count', y="Word").update_layout(height=420) , [dbc.AccordionItem(table(df), title="Show data")]