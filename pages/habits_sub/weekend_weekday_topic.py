import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import table, generic_bar
from datetime import date

def weekend_weekday_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='date_range_weekend_weekday',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        html.P("By which filter:"),
        dcc.Dropdown(id='dropdown_weekend_weekday',
                options=['Category', 'Type'],
                value='Category', clearable=False
        ),
        dcc.Graph(id='weekend_weekday_graph'),
        dbc.Accordion(id='weekend_weekday_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("weekend_weekday_graph", "figure"),
    Output("weekend_weekday_table", "children"),
    Input('date_range_weekend_weekday', 'start_date'),
    Input('date_range_weekend_weekday', 'end_date'),
    Input('dropdown_weekend_weekday', 'value')
)
def update_graph(start_date, end_date, category_or_type):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    df = query.weekday_vs_weekend(category_or_type=category_or_type, lower_range=start_date, upper_range=end_date)

    df = df.melt(id_vars=category_or_type, var_name="Day type", value_name="Average")

    figure = generic_bar(graph_df=df, x_axis=category_or_type, y_axis="Average", chosen="Day type")

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]