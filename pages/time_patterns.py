from dash import html
import dash_bootstrap_components as dbc
import dash

from .time_patterns_sub.time_patterns_sidebar import sidebar_time_patterns
from .time_patterns_sub.day_trend_topic import day_trend_layout
from .time_patterns_sub.weeks_trend_topic import weeks_trend_layout
from .time_patterns_sub.months_trend_topic import months_trend_layout
from .time_patterns_sub.quarters_trend_topic import quarters_trend_layout
from .time_patterns_sub.years_trend_topic import years_trend_layout
from .time_patterns_sub.time_day_topic import time_day_layout

def title(topic=None):
    # This will show in browser tab and the meta tags
    return f"Time Patterns page: {topic}"


def description(topic=None):
    if topic == "day_trend":
        return ""
    elif topic == "weeks_trend":
        return ""
    elif topic == "months_trend":
        return ""
    elif topic == "quarters_trend":
        return ""
    elif topic == "years_trend":
        return ""
    elif topic == "time_day":
        return ""

    return "Here is general info about the topics on this page"


dash.register_page(
    __name__,
    path_template="/time_patterns/<topic>",
    title=title,
    description=description,
    # sets a default for the path variable
    path="/time_patterns/day_trend",
    # prevents showing a Page Not Found if someone enters /about in the browser
    redirect_from=["/time_patterns", "/time_patterns/"],
)


def layout(topic=None, **other_unknown_query_strings):
    parent_card =  dbc.Card(" Here is the main Time Patterns Page content", body=True)

    if topic == "day_trend":
        topic_card =  day_trend_layout()
    elif topic == "weeks_trend":
        topic_card =  weeks_trend_layout()
    elif topic == "months_trend":
        topic_card =  months_trend_layout()
    elif topic == "quarters_trend":
        topic_card =  quarters_trend_layout()
    elif topic == "years_trend":
        topic_card =  years_trend_layout()
    elif topic == "time_day":
        topic_card =  time_day_layout()
    else:
        topic_card= ""

    return dbc.Row(
        [dbc.Col(sidebar_time_patterns(f"/time_patterns/{topic}"), width=2), dbc.Col([parent_card, topic_card], width=10)]
    )

