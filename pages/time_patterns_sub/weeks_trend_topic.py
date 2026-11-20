import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, bar_graph

def weeks_trend_layout():

    return html.Div([
        dbc.Card(" Watch Activity For Each Selected Week", body=True, className="mt-2"),
        html.Br(),
        dcc.Slider(1, 26, 1, value=7, id="slider_weeks_trend"),
        html.Br(),
        dbc.Row([
            dbc.Col(
                [
                    html.H6("Show by:", className="mb-1"),
                    dcc.Dropdown(
                        id="dropdown_weeks_trend",
                        options=["Category", "Video Type"],
                        value="Category",
                        clearable=False,
                    )
                ],
                md=4
            ),
        ]),
        html.Br(),
        dcc.Graph(id='weeks_trend_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_week_trend_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='weeks_trend_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_week_trend"),
    ])

@callback(
    Output("weeks_trend_graph", "figure"),
    Output("weeks_trend_table", "children"),
    Input('slider_weeks_trend', "value"),
    Input('dropdown_weeks_trend', 'value')
)
def update_graph(limit, chosen):
    df = query.weekly_trend_updated(category_or_type=chosen, limit=limit)

    figure = bar_graph(df, chosen, x_axis='Week' , y_axis='Sub Count', hover="Total Count")

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]

@callback(
    Output("download_week_trend", "data"),
    Input("download_week_trend_btn", "n_clicks"),
    State("slider_weeks_trend", "value"),
    State("dropdown_weeks_trend", "value"),
    prevent_initial_call=True,
)
def download_week_trend_csv(_, limit, chosen):
    df = query.weekly_trend_updated(category_or_type=chosen, limit=limit)

    return dcc.send_data_frame(df.to_csv, f"week_trend_{limit}_weeks.csv", index=False)