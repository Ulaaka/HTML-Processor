from dash import html
import dash_bootstrap_components as dbc

path_pagename_map_highlight = {
    "/highlight/first_watched": "First Watched",
    "/highlight/last_watched": "Last Watched",
    "/highlight/random_day": "Random Day",
    "/highlight/longest_titles": "Longest Titles"
}

def sidebar_highlight(current_path):
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
                for href, name in path_pagename_map_highlight.items()
            ],
            vertical=True,
            pills=True,
            className="bg-light",
        )
    )
