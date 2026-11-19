from dash import html
import dash_bootstrap_components as dbc
import dash

from .content_sub.content_side_bar import sidebar_content
from .content_sub.most_watched_content_topic import most_watched_content_layout
from .content_sub.favorite_words_topic import favorite_words_layout
from .content_sub.format_mix_topic import format_mix_layout
from .content_sub.format_trend_topic import format_trend_layout
from .content_sub.interests_topic import interests_layout
from .content_sub.heatmap_topic import heatmap_layout
from .content_sub.unavailable_topic import unavailable_layout


def title(topic=None):
    return f"Content page: {topic}"


def description(topic=None):
    if topic == "most_watched_content":
        return ""
    elif topic == "favorite_words":
        return ""
    elif topic == "interests":
        return ""
    elif topic == "format_mix":
        return ""
    elif topic == "format_trend":
        return ""
    elif topic == "heatmap":
        return ""
    elif topic == "unavailable":
        return ""

    return "Here is general info about the topics on this page"


dash.register_page(
    __name__,
    path_template="/content/<topic>",
    title=title,
    description=description,
    path="/content/most_watched_content",
    redirect_from=["/content", "/content/"],
)

def layout(topic=None, **other_unknown_query_strings):

    if topic == "most_watched_content":
        topic_card =  most_watched_content_layout()
    elif topic == "favorite_words":
        topic_card =  favorite_words_layout()
    elif topic == "interests":
        topic_card =  interests_layout()
    elif topic == "format_mix":
        topic_card =  format_mix_layout()
    elif topic == "format_trend":
        topic_card =  format_trend_layout()
    elif topic == "heatmap":
        topic_card =  heatmap_layout()
    elif topic == "unavailable":
        topic_card =  unavailable_layout()
    else:
        topic_card= ""

    return dbc.Row(
        [dbc.Col(sidebar_content(f"/content/{topic}"), width=2), dbc.Col([topic_card], width=10)]
    )

