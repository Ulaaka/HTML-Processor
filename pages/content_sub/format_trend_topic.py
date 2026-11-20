import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import bar_graph, table
from html_parser import category_mapping

def format_trend_layout():
    return html.Div([
        dbc.Card("Composition of Video Formats Per Month Over the Entire Duration", body=True, className="mt-2"),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Category:", className="content"),
                dcc.Dropdown(id='dropdown_format_trend',
                        options=['All'] + list(category_mapping.values()),
                        value='All', clearable=False
                    ),
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='format_trend_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_format_trend_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='format_trend_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_format_trend"),
    ])


@callback(
    Output("format_trend_graph", "figure"),
    Output("format_trend_table", "children"),
    Input('dropdown_format_trend', 'value')
)
def update_graph(video_category):
    if video_category == 'All':
        video_category = None

    df = query.video_length_trend_over_month(video_category=video_category)
    df = df.melt(id_vars="Video Type", var_name="Month", value_name="Videos")

    figure = bar_graph(df, "Video Type", x_axis='Month', y_axis='Videos', hover="Videos")

    return figure, [dbc.AccordionItem(table(df), title="Show data")]

@callback(
    Output("download_format_trend", "data"),
    Input("download_format_trend_btn", "n_clicks"),
    State('dropdown_format_trend', 'value'),
    prevent_initial_call=True,
)
def download_format_trend_csv(_, video_category):
    if video_category == 'All':
        video_category = None

    df = query.video_length_trend_over_month(video_category=video_category)
    df = df.melt(id_vars="Video Type", var_name="Month", value_name="Videos")

    return dcc.send_data_frame(df.to_csv, "format_trend.csv", index=False)