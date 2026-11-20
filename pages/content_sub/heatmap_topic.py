import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, heatmap_graph
from html_parser import category_mapping

def heatmap_layout():
    years = query.all_years()

    return html.Div([
        dbc.Card("Watch Activity Heatmap For Selected Month", body=True, className="mt-2"),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Year:", className="content"),
                dcc.Dropdown(id='dropdown_heatmap_year',
                        options=years,
                        value=max(years), clearable=False
                    ),
            ], md=3),
            dbc.Col([
                html.H6("Month:", className="content"),
                dcc.Dropdown(id='dropdown_heatmap_month'),
            ], md=3),
            dbc.Col([
                html.H6("Category:", className="content"),
                dcc.Dropdown(id='dropdown_heatmap_category',
                        options=['All'] + list(category_mapping.values()),
                        value='All', clearable=False
                ),
            ], md=3),
            dbc.Col([
                html.H6("Video Type:", className="content"),
                dcc.Dropdown(id='dropdown_heatmap_type',
                        options=['All', 'Video', 'Reel', 'Unavailable'],
                        value='All', clearable=False
                ),
            ], md=3),
        ]),
        html.Br(),
        dcc.Graph(id='heatmap_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_heatmap_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='heatmap_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_heatmap"),
    ])

@callback(
    Output('dropdown_heatmap_month', 'options'),
    Output('dropdown_heatmap_month', 'value'),
    Input('dropdown_heatmap_year', 'value'))
def set_months_options(selected_year):
    options = query.all_months(selected_year)
    return options, options[0]

@callback(
    Output("heatmap_graph", "figure"),
    Output("heatmap_table", "children"),
    Input('dropdown_heatmap_category', "value"),
    Input('dropdown_heatmap_type', "value"),
    Input('dropdown_heatmap_year', "value"),
    Input('dropdown_heatmap_month', "value")
)
def update_graph(video_category, video_type, year, month):
    video_category = None if video_category == 'All' else video_category
    video_type = None if video_type == 'All' else video_type.lower()

    df = query.calendar_heatmap(year=year, month=month, video_category=video_category, video_type=video_type)

    figure = heatmap_graph(graph_df=df, x_label="Week Number", y_label="Week Day")

    return figure, [dbc.AccordionItem(table(df), title="Show data")]

@callback(
    Output("download_heatmap", "data"),
    Input("download_heatmap_btn", "n_clicks"),
    State('dropdown_heatmap_category', "value"),
    State('dropdown_heatmap_type', "value"),
    State('dropdown_heatmap_year', "value"),
    State('dropdown_heatmap_month', "value"),
    prevent_initial_call=True,
)
def download_heatmap_csv(_, video_category, video_type, year, month):
    video_category = None if video_category == 'All' else video_category
    video_type = None if video_type == 'All' else video_type.lower()

    df = query.calendar_heatmap(year=year, month=month, video_category=video_category, video_type=video_type)

    return dcc.send_data_frame(df.to_csv, f"heatmap_{year}_{month}.csv", index=False)