import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import bar_graph, table
from datetime import date

def busiest_days_layout():

    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Watch Activity For Busiest Days During Selected Period and Their Compositions", body=True, className="mt-2"),
        html.Br(),
        dcc.Slider(5, 20, 1, value=10, id='slider_busiest_days'),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='data_range_busiest_days',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
            dbc.Col([
                html.H6("Show By:", className="content"),
                dcc.Dropdown(id='dropdown_busiest_days',
                        options=['Category', 'Video Type'],
                        value='Category', clearable=False
                    ),
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='busiest_days_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_busiest_days_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='busiest_days_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_busiest_days"),
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

    df = query.the_busiest_day(
        category_or_type=chosen,
        limit=limit,
        lower_range=start_date,
        upper_range=end_date,
    )
    figure = bar_graph(df, chosen, x_axis='Date' , y_axis='Sub Count', hover=['Total Count', 'Day of Week'])

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]

@callback(
    Output("download_busiest_days", "data"),
    Input("download_busiest_days_btn", "n_clicks"),
    State('slider_busiest_days', "value"),
    State('data_range_busiest_days', 'start_date'),
    State('data_range_busiest_days', 'end_date'),
    State('dropdown_busiest_days', 'value'),
    prevent_initial_call=True,
)
def download_busiest_days_csv(_, limit, start_date, end_date, chosen):

    df = query.the_busiest_day(
        category_or_type=chosen,
        limit=limit,
        lower_range=start_date,
        upper_range=end_date,
    )
    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"busiest_days_{start_date}_to_{end_date}.csv", index=False)