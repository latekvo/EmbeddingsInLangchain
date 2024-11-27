import html
from dataclasses import dataclass
from enum import Enum

import requests
from langchain_core.documents import Document

from utils import url_download_document

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
    document: Document
    url: str | None
    title: str
    text: str


def get_stories(type_url=HNPathsV0.TOP_STORIES, max_amount=10) -> list[Story]:
    story_ids: list[int] = requests.get(url=type_url.value).json()

    story_ids = story_ids[0:max_amount]

    stories = []
    for story_id in story_ids:
        story_json = requests.get(url=gen_item_path(story_id)).json()
        url = story_json.get("url")
        text = story_json.get("text")

        if url is not None:
            document = url_download_document(url)
            text = document.page_content
        else:
            if text is None:
                # in rare situations questions are returned by TOP_STORIES request
                story_ids.remove(story_id)
                continue

            document = Document(text)

        story = Story(
            id=story_json.get("id"),
            url=url,
            title=story_json.get("title"),
            text=text,
            document=document,
        )

        stories.append(story)

    return stories
