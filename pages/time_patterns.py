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
from .time_patterns_sub.last_days_topic import last_days_layout


def title(topic=None):
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
    elif topic == "last_days":
        return ""

    return "Here is general info about the topics on this page"


dash.register_page(
    __name__,
    path_template="/time_patterns/<topic>",
    title=title,
    description=description,
    path="/time_patterns/day_trend",
    redirect_from=["/time_patterns", "/time_patterns/"],
)


def layout(topic=None, **other_unknown_query_strings):

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
    elif topic == "last_days":
        topic_card =  last_days_layout()
    else:
        topic_card= ""

    return dbc.Row(
        [dbc.Col(sidebar_time_patterns(f"/time_patterns/{topic}"), width=2), dbc.Col([topic_card], width=10)]
    )

