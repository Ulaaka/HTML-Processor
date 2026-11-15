from dash import html
import dash_bootstrap_components as dbc

path_pagename_map_content = {
    "/time_patterns/day_trend": "Day Trend",
    "/time_patterns/weeks_trend": "Weeks Trend",
    "/time_patterns/months_trend": "Months Trend",
    "/time_patterns/quarters_trend": "Quarters Trend",
    "/time_patterns/years_trend": "Years Trend",
    "/time_patterns/time_day": "Time of the Day"
}

def sidebar_time_patterns(current_path):
    return html.Div(
        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(name, className="ms-2"),
                    ],
                    href=href,
                    active=(href == current_path),
                )
                for href, name in path_pagename_map_content.items()
            ],
            vertical=True,
            pills=True,
            className="bg-light",
        )
    )