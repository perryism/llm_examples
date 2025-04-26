from story import helpers

from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage
from story.agents import SynopsisGeneration, ChapterPlotWriter, ChapterSummarizer, ChapterWriter
from libs.graph import Graph
from libs import llm_factory
from story.entities import Story


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    story: dict

graph = Graph(AgentState)

CHAPTER_WORD_COUNT = 200
LLM_NAME = "local"

@graph.entry_point
def generate_story(state: AgentState):
    story_obj = state["story"]
    llm = llm_factory.create(LLM_NAME)
    brief_story = helpers.generate_story(llm, story_obj['instruction'], story_obj["synopsis"])
    return {"messages": [brief_story], "story": story_obj}

output = print
input_prompt = input

@graph.condition("generate_story", {"good": "write_chapter_plot", "bad": "generate_story", "unknown": "generate_story" })
def is_story_good(state: AgentState):
    brief_story = state["messages"][-1]
    output(brief_story)
    # answer = input_prompt("is the outline good? (y/n)")
    answer = "y"
    return  { "y": "good", "n": "bad"}.get(answer, "unknown")

@graph.node
def write_chapter_plot(state: AgentState):
    brief_story = state["messages"][-1]
    story_dict = state["story"]
    num = story_dict["number_of_chapters"]
    llm = llm_factory.create(LLM_NAME)
    chapters = helpers.plot_writer(llm, num, brief_story, 100)
    story_dict["chapters"] = chapters
    return {"messages": [chapters], "story": story_dict }

@graph.true(generate_story, write_chapter_plot, generate_story)
def isis(state: AgentState):
    brief_story = state["messages"][-1]
    output(brief_story)
    # answer = input_prompt("is the outline good? (y/n)")
    answer = "y"
    return  { "y": "good", "n": "bad"}.get(answer, "unknown")

@graph.condition("write_chapter_plot", {"good": "write_chapter", "bad": "write_chapter_plot", "unknown": "write_chapter_plot" })
def is_plot_good(state: AgentState):
    chapters = state["messages"][-1]
    story_dict = state["story"]
    output(story_dict["chapters"])
    answer = input_prompt("is the plot good? (y/n)")
    return  { "y": "good", "n": "bad"}.get(answer, "unknown")

@graph.node
def write_chapter(state: AgentState):
    story_dict = state["story"]
    current_chapter = story_dict.get("current_chapter", 1)
    story_dict["current_chapter"] = current_chapter
    llm = llm_factory.create(LLM_NAME)
    chapter = helpers.write_chapter(llm, current_chapter, story_dict, CHAPTER_WORD_COUNT)
    return {"messages": [chapter], "story": story_dict}

@graph.condition("write_chapter", {"good": "prepare_chapter", "bad": "write_chapter", "unknown": "write_chapter" })
def is_chapter_good(state: AgentState):
    chapter_story = state["messages"][-1]
    output(chapter_story)
    answer = input_prompt("is the chapter good? (y/n)")
    return  { "y": "good", "n": "bad"}.get(answer, "unknown")

@graph.node
def prepare_chapter(state: AgentState):
    chapter_story = state["messages"][-1]
    story_dict = state["story"]
    chapter = Story.get_chapter(story_dict, story_dict["current_chapter"])
    chapter["story"] = chapter_story
    story_dict["current_chapter"] += 1
    print('current', story_dict["current_chapter"])
    return {"message": [], "story": story_dict}

@graph.condition("prepare_chapter", {"continue": "write_chapter", "finished": "finish_story", "unknown": "finish_story"})
def continue_next_chapter(state: AgentState):
    story_dict = state["story"]
    finished = story_dict["number_of_chapters"] < story_dict["current_chapter"]
    return "finished" if finished else "continue"

@graph.node
def finish_story(state: AgentState):
    story_dict = state["story"]
    for chapter in story_dict["chapters"]:
        print(chapter["number"])
        print(chapter["story"])

from IPython.display import Image
graph = graph.graph
graph = graph.compile()
