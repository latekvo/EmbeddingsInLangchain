import html
from dataclasses import dataclass
from enum import Enum

import requests

# use for trivial crawling - has all we need to retrieve front-page data
HN_V0_URL = "https://hacker-news.firebaseio.com/v0/"
DOT_JSON = ".json"
# use for hybrid searches - existing alternative to our indexing, has request limit
HN_V1_URL = "http://hn.algolia.com/api/v1/"


class HNPathsV0(Enum):
    # stories - external
    TOP_STORIES = HN_V0_URL + "topstories" + DOT_JSON
    NEW_STORIES = HN_V0_URL + "newstories" + DOT_JSON
    BEST_STORIES = HN_V0_URL + "beststories" + DOT_JSON
    # stories - text/internal
    ASK_STORIES = HN_V0_URL + "askstories" + DOT_JSON
    SHOW_STORIES = HN_V0_URL + "showstories" + DOT_JSON
    JOB_STORIES = HN_V0_URL + "jobstories" + DOT_JSON
    # query
    USER = HN_V0_URL + "user/"
    ITEM = HN_V0_URL + "item/"
    # misc
    MAX_ITEM = HN_V0_URL + "maxitem" + DOT_JSON
    UPDATES = HN_V0_URL + "updates" + DOT_JSON


class HNItemType(Enum):
    STORY = "story"
    POST = "post"
    JOB = "job"
    COMMENT = "comment"
    POLL = "poll"
    POLLOPT = "pollopt"


def clean_html(input_text):
    return html.unescape(input_text).replace("<", "").replace(">", "")


def gen_item_path(item_id: int):
    return HNPathsV0.ITEM.value + str(item_id) + ".json"


@dataclass
class Story:
    id: int
    title: str
    url: str | None
    text: str | None  # alternative to url


def get_stories(type_url=HNPathsV0.TOP_STORIES) -> list[Story]:
    story_ids = requests.get(url=type_url.value).json()

    stories = []
    for story_id in story_ids:
        story_json = requests.get(url=gen_item_path(story_id)).json()

        stories.append(
            Story(
                id=story_json.get("id"),
                url=story_json.get("url"),
                title=story_json.get("title"),
                text=story_json.get("text"),
            )
        )

    return stories
