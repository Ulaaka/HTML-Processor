import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import hbar, table

def interests_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Video Category Count During Selected Period", body=True, className="mt-2"),
        html.Br(),
        dcc.Slider(5, 40, 5, value=20, id='slider_category_count'),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='data_range_category_count',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='category_count_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_category_count_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='category_count_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_category_count"),
    ])

@callback(
    Output("category_count_graph", "figure"),
    Output("category_count_table", "children"),
    Input('slider_category_count', "value"),
    Input('data_range_category_count', 'start_date'),
    Input('data_range_category_count', 'end_date')
)
def update_table(value, start_date, end_date):
    df = query.interest_analysis(limit=value, lower_range=start_date, upper_range=end_date)

    return hbar(df, x='Total Count', y="Category").update_layout(height=420), [dbc.AccordionItem(table(df), title="Show data")]

@callback(
    Output("download_category_count", "data"),
    Input("download_category_count_btn", "n_clicks"),
    State('slider_category_count', "value"),
    State('data_range_category_count', 'start_date'),
    State('data_range_category_count', 'end_date'),
    prevent_initial_call=True,
)
def download_category_count_csv(_, value, start_date, end_date):
    df = query.interest_analysis(limit=value, lower_range=start_date, upper_range=end_date)

    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"category_count_{start_date}_to_{end_date}.csv", index=False)