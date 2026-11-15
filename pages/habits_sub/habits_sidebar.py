from dash import html
import dash_bootstrap_components as dbc

path_pagename_map_channels = {
    "/habits/busiest_days": "Busiest Days",
    "/habits/busiest_weeks": "Busiest Weeks",
    "/habits/streaks": "Streaks",
    "/habits/weekend_weekday": "Weekends vs Weekdays",
    "/habits/explorer": "Explorer"
}

def sidebar_habits(current_path):
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
                for href, name in path_pagename_map_channels.items()
            ],
            vertical=True,
            pills=True,
            className="bg-light",
        )
    )