from dash import html
import dash_bootstrap_components as dbc
import dash

from .habits_sub.habits_sidebar import sidebar_habits
from .habits_sub.busiest_days_topic import busiest_days_layout
from .habits_sub.busiest_weeks_topic import busiest_weeks_layout
from .habits_sub.streaks_topic import streaks_layout
from .habits_sub.weekend_weekday_topic import weekend_weekday_layout
from .habits_sub.explorer_topic import explorer_layout

def title(topic=None):
    return f"Habits page: {topic}"


def description(topic=None):
    if topic == "busiest_days":
        return ""
    elif topic == "busiest_weeks":
        return ""
    elif topic == "streaks":
        return ""
    elif topic == "weekend_weekday":
        return ""
    elif topic == "explorer":
        return ""

    return "Here is general info about the topics on this page"


dash.register_page(
    __name__,
    path_template="/habits/<topic>",
    title=title,
    description=description,
    path="/habits/busiest_days",
    redirect_from=["/habits", "/habits/"],
)


def layout(topic=None, **other_unknown_query_strings):

    if topic == "busiest_days":
        topic_card =  busiest_days_layout()
    elif topic == "busiest_weeks":
        topic_card =  busiest_weeks_layout()
    elif topic == "streaks":
        topic_card =  streaks_layout()
    elif topic == "weekend_weekday":
        topic_card =  weekend_weekday_layout()
    elif topic == "explorer":
        topic_card =  explorer_layout()
    else:
        topic_card= ""

    return dbc.Row(
        [dbc.Col(sidebar_habits(f"/habits/{topic}"), width=2), dbc.Col([topic_card], width=10)]
    )

