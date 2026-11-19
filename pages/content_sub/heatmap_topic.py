import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import table, heatmap_graph
from datetime import date
from html_parser import category_mapping
import plotly.express as px
import plotly.graph_objects as go

def heatmap_layout():
    years = query.all_years()

    return html.Div([
        html.P("Year:"),
        dcc.Dropdown(id='dropdown_heatmap_year',
                options=years,
                value=max(years), clearable=False
            ),
        html.P("Month:"),
        dcc.Dropdown(id='dropdown_heatmap_month'),
        html.P("Category:"),
        dcc.Dropdown(id='dropdown_heatmap_category',
                options=['All'] + list(category_mapping.values()),
                value='All', clearable=False
        ),
        html.Br(),
        html.P("Video Type:"),
        dcc.Dropdown(id='dropdown_heatmap_type',
                options=['All', 'Video', 'Reel', 'Unavailable'],
                value='All', clearable=False
        ),
        html.Br(),
        dcc.Graph(id='heatmap_graph'),
        dbc.Accordion(id='heatmap_table', start_collapsed=True, flush=True)
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

    df = query.calendar_heatmap(year = year, month=month, video_category=video_category, video_type=video_type)

    figure = heatmap_graph(graph_df=df, x_label="Week Number", y_label="Week Day")

    return figure, [dbc.AccordionItem(table(df), title="Show data")]