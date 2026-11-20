import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, generic_bar
from datetime import date

def weekend_weekday_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Comparison of Weekday and Weekend During Selected Period", body=True, className="mt-2"),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='date_range_weekend_weekday',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
            dbc.Col([
                html.H6("Filter By:", className="content"),
                dcc.Dropdown(id='dropdown_weekend_weekday',
                        options=['Category', 'Type'],
                        value='Category', clearable=False
                ),
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='weekend_weekday_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_weekend_weekday_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='weekend_weekday_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_weekend_weekday"),
    ])

@callback(
    Output("weekend_weekday_graph", "figure"),
    Output("weekend_weekday_table", "children"),
    Input('date_range_weekend_weekday', 'start_date'),
    Input('date_range_weekend_weekday', 'end_date'),
    Input('dropdown_weekend_weekday', 'value')
)
def update_graph(start_date, end_date, category_or_type):

    df = query.weekday_vs_weekend(category_or_type=category_or_type, lower_range=start_date, upper_range=end_date)

    df = df.melt(id_vars=category_or_type, var_name="Day type", value_name="Average")

    figure = generic_bar(graph_df=df, x_axis=category_or_type, y_axis="Average", chosen="Day type")

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]

@callback(
    Output("download_weekend_weekday", "data"),
    Input("download_weekend_weekday_btn", "n_clicks"),
    State('date_range_weekend_weekday', 'start_date'),
    State('date_range_weekend_weekday', 'end_date'),
    State('dropdown_weekend_weekday', 'value'),
    prevent_initial_call=True,
)
def download_weekend_weekday_csv(_, start_date, end_date, category_or_type):

    df = query.weekday_vs_weekend(category_or_type=category_or_type, lower_range=start_date, upper_range=end_date)

    df = df.melt(id_vars=category_or_type, var_name="Day type", value_name="Average")

    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"weekend_weekday_{start_date}_to_{end_date}.csv", index=False)