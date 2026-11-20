import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, scatter_graph

def forgotten_favorites_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Channels You Used Watch a Lot Before (based on neglect score)", body=True, className="mt-2"),
        html.Br(),
        dcc.Slider(5, 150, 1, value=20, id='slider_forgotten'),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='date_range_forgotten',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='forgotten_channels'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_forgotten_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='forgotten_channels_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_forgotten"),
    ])

@callback(
    Output("forgotten_channels", "figure"),
    Output("forgotten_channels_table", "children"),
    Input('slider_forgotten', "value"),
    Input('date_range_forgotten', 'start_date'),
    Input('date_range_forgotten', 'end_date')
)
def update_table(value, start_date, end_date):
    df = query.the_longest_untouched_channel(limit=value, lower_range=start_date, upper_range=end_date)

    figure = scatter_graph(graph_df=df, x_axis="Since Last Watched", y_axis="Total Watch", size_value="Neglect Score", hover_value="Channel Name")
    return figure, [dbc.AccordionItem(table(table_df=df, url="URL"), title="Show data")]

@callback(
    Output("download_forgotten", "data"),
    Input("download_forgotten_btn", "n_clicks"),
    State('slider_forgotten', "value"),
    State('date_range_forgotten', 'start_date'),
    State('date_range_forgotten', 'end_date'),
    prevent_initial_call=True,
)
def download_forgotten_csv(_, value, start_date, end_date):
    df = query.the_longest_untouched_channel(limit=value, lower_range=start_date, upper_range=end_date)

    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"forgotten_favorites_{start_date}_to_{end_date}.csv", index=False)