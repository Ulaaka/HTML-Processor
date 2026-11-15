from dash import html
import dash_bootstrap_components as dbc

path_pagename_map_content = {
    "/content/most_watched_content": "Most Watched Videos",
    "/content/favorite_words": "Favorite Words",
    "/content/interests": "Interests",
    "/content/format_mix": "Format Mix",
    "/content/format_trend": "Format Trend",
    "/content/search_titles": "Search Titles",
    "/content/unavailable": "Unavailable"
}

def sidebar_content(current_path):
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