from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from IPython.display import Image
from dataclasses import dataclass, asdict, field

@dataclass
class Chapter:
    number: int
    plot: str
    story: str = None

    def dict(self):
        return asdict(self)

@dataclass
class Story:
    instruction: str = None
    synopsis: str = None
    chapters: list[Chapter] = field(default_factory=lambda: [])
    summary: str = None
    number_of_chapters: int = None

    # def chapter(self, number):
    #     return list(filter(lambda x : x.number == number, self.chapters))[0]

    def plot(self, number):
        return self.chapter(number).plot

    def all_plots(self):
        return [ chapter.plot for chapter in self.chapters]

    @staticmethod
    def all_chapters(story: dict):
        """
        this return all chapters developed so far
        """
        return list(filter(lambda x : x.get("story") is not None, story["chapters"]))

    @staticmethod
    def all_stories(story: dict):
        """
        this return all stories developed so far
        """
        chapters: list[dict] = Story.all_chapters(story)
        return [ chapter["story"] for chapter in chapters]

    @staticmethod
    def last_chapter(story: dict):
        """
        Return last chapter with story
        """
        chapters = list(filter(lambda x : x.get("story") is not None, story["chapters"]))
        return chapters[-1]

    @staticmethod
    def current_chapter(story: dict):
        """
        Return the chapter with no story
        """
        chapters = list(filter(lambda x : x.get("story") is not None, story["chapters"]))
        return chapters[0] if len(chapters) > 0 else None

    @staticmethod
    def plots(story: dict):
        return [ [chapter["number"],  chapter["plot"]] for chapter in story["chapters"]]

    @staticmethod
    def is_first_chapter(story: dict):
        return story.get("summary") is None

    @staticmethod
    def get_chapter(story: dict, number: int):
        return list(filter(lambda x : x["number"] == number, story["chapters"]))[0]

    @staticmethod
    def from_dict(s: dict):
        return Story(**s)

    def dict(self):
        return asdict(self)

