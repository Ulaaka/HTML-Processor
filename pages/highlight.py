from dash import html
import dash_bootstrap_components as dbc
import dash

from .highlight_sub.highlight_side_bar import sidebar_highlight
from .highlight_sub.first_watched_topic import first_watched_layout
from .highlight_sub.last_watched_topic import last_watched_layout
from .highlight_sub.random_day_topic import random_day_layout
from .highlight_sub.longest_titles_topic import longest_titles_layout

def title(topic=None):
    # This will show in browser tab and the meta tags
    return f"Highlight page: {topic}"


def description(topic=None):
    if topic == "first_watched":
        return ""
    elif topic == "last_watched":
        return ""
    elif topic == "random_day":
        return ""
    elif topic == "longest_titles":
        return ""

    return "Here is general info about the topics on this page"


dash.register_page(
    __name__,
    path_template="/highlight/<topic>",
    title=title,
    description=description,
    # sets a default for the path variable
    path="/highlight/first_watched",
    # prevents showing a Page Not Found if someone enters /about in the browser
    redirect_from=["/highlight", "/highlight/"],
)

def layout(topic=None, **other_unknown_query_strings):
    parent_card =  dbc.Card(" Here is the main Highlight Page content", body=True)

    if topic == "first_watched":
        topic_card =  first_watched_layout()
    elif topic == "last_watched":
        topic_card =  last_watched_layout
    elif topic == "random_day":
        topic_card =  random_day_layout
    elif topic == "longest_titles":
        topic_card =  longest_titles_layout
    else:
        topic_card= ""

    return dbc.Row(
        [dbc.Col(sidebar_highlight(f"/highlight/{topic}"), width=2), dbc.Col([parent_card, topic_card], width=10)]
    )

