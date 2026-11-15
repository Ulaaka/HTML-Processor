from dash import html
import dash_bootstrap_components as dbc
import dash

from .channels_sub.channels_side_bar import sidebar_channels
from .channels_sub.most_watched_topic import most_watched_layout
from .channels_sub.channel_month_topic import channel_month_layout
from .channels_sub.latest_month_topic import latest_month_layout
from .channels_sub.forgotten_favorites_topic import forgotten_favorites_layout

def title(topic=None):
    return f"Channels page: {topic}"


def description(topic=None):
    if topic == "most_watched":
        return ""
    elif topic == "channel_month":
        return ""
    elif topic == "latest_month":
        return ""
    elif topic == "forgotten_favorites":
        return ""

    return "Here is general info about the topics on this page"


dash.register_page(
    __name__,
    path_template="/channels/<topic>",
    title=title,
    description=description,
    # sets a default for the path variable
    path="/channels/most_watched",
    # prevents showing a Page Not Found if someone enters /about in the browser
    redirect_from=["/channels", "/channels/"],
)


def layout(topic=None, **other_unknown_query_strings):
    parent_card =  dbc.Card(" Here is the main Highlight Page content", body=True)

    if topic == "most_watched":
        topic_card =  most_watched_layout()
    elif topic == "channel_month":
        topic_card =  channel_month_layout
    elif topic == "latest_month":
        topic_card =  latest_month_layout
    elif topic == "forgotten_favorites":
        topic_card =  forgotten_favorites_layout
    else:
        topic_card= ""

    return dbc.Row(
        [dbc.Col(sidebar_channels(f"/channels/{topic}"), width=2), dbc.Col([parent_card, topic_card], width=10)]
    )

