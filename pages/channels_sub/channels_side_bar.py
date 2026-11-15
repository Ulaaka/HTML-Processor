from dash import html
import dash_bootstrap_components as dbc

path_pagename_map_channels = {
    "/channels/most_watched": "Most Watched",
    "/channels/channel_month": "Channel of the Month",
    "/channels/latest_month": "Latest Month",
    "/channels/forgotten_favorites": "Forgotten Favorites"
}

def sidebar_channels(current_path):
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