from langchain.output_parsers import PydanticOutputParser
from .entities import Story
from libs import llm_factory
import logging

logger = logging.getLogger()

class Agent:
    SYSTEM_PROMPT = "You are a helpful agent."

    def __init__(self, llm, instruction):
        self.instruction = instruction
        self.llm = llm

    def generate(self, user_prompt):
        return self.invoke(self._get_system_prompt("You are a helpful assistant."), user_prompt).content

    def invoke(self, system, user_prompt):
        # messages = [
        #     ("system", system),
        #     ("user", user_prompt),
        # ]
        messages = [
             { "role": "system", "content": system },
            { "role": "user", "content": user_prompt }
        ]
        logger.debug(messages)
        return self.llm.invoke(messages)

    def _get_system_prompt(self):
        return self.SYSTEM_PROMPT.format(instruction=self.instruction)

class SynopsisGeneration(Agent):
    SYSTEM_PROMPT = """
You are a story writer.  You are writing a story on the following instruction.  Your response should only contain the story.

{instruction}
"""
    def generate(self, user_prompt):
        return self.invoke(self._get_system_prompt(), user_prompt).content

    def _get_system_prompt(self):
        return self.SYSTEM_PROMPT.format(instruction=self.instruction)

from pydantic import BaseModel

class ChapterPlotWriter(Agent):
    SYSTEM_PROMPT = """
    You are a story writer.  Based on the story, create {number_of_chapters} chapter plots.

    Each chapter plot must have at least {word_count_for_chapter} words."""

    def __init__(self, llm, number_of_chapters, word_count_for_chapter):
        self.number_of_chapters = number_of_chapters
        self.word_count_for_chapter = word_count_for_chapter

        class MyStory(BaseModel):
            class Chapter(BaseModel):
                number: int
                plot: str
            chapters: list[Chapter]

        self.llm = llm.with_structured_output(MyStory)
        assert hash(llm) != hash(self.llm)

    def generate(self, story:str) -> list[dict]:
        return self.invoke(self._get_system_prompt(), story).model_dump()["chapters"]

    def _get_system_prompt(self):
        return self.SYSTEM_PROMPT.format(number_of_chapters=self.number_of_chapters, word_count_for_chapter=self.word_count_for_chapter)

class ChapterSummarizer(Agent):
    SYSTEM_PROMPT = """
You are a story summarizing agent.  You need to summarize given chapters to produce a summary of the story.
Your response will be used to continue to next chapter so don't not miss out the important details.

Do not generate new content. Your job is summarization. Summarize the story in {word_count} words.

"""
    def __init__(self, llm, word_count=200):
        self.word_count = word_count
        self.llm = llm

    def generate(self, story:str):
        return self.invoke(self.SYSTEM_PROMPT.format(word_count=self.word_count), story).model_dump()

class ChapterWriter(Agent):
    SYSTEM_PROMPT = """
You are a story writer. The story outline is given to you.  You will write a particular chapter based on the user's input.

The chapter must have at least {word_count_for_chapter} words
{instruction}
"""

    def __init__(self, llm, chapter_num, story: dict, word_count_for_chapter=200):
        self.chapter_num = chapter_num
        self.llm = llm
        self.story = story
        self.word_count_for_chapter = word_count_for_chapter
        super().__init__(llm, story["instruction"])

    def generate(self, current_plot):
        return super().invoke(self.SYSTEM_PROMPT.format(
            instruction=self.instruction,
            word_count_for_chapter=self.word_count_for_chapter
        ), self.user_prompt(current_plot)).content

    @property
    def summary(self):
        if not self.story["summary"]:
             agent = ChapterSummarizer(self.llm)
             self.story["summary"] = \
                agent.generate(Story.all_stories(self.story))

        return self.story["summary"]

    @property
    def last_chapter_summary(self):
        agent = ChapterSummarizer(self.llm)
        return agent.generate(Story.last_chapter(self.story)["story"])

    @property
    def plots(self):
        return [ [chapter["number"],  chapter["plot"]] for chapter in self.story["chapters"]]

    def user_prompt(self, plot):
        if self.chapter_num == 1:
            return f"""
Story outline:
{self.plots}

Chapter {self.chapter_num}:
{plot}
"""
        else:
            return f"""
Story outline:
{self.plots}

Previous chapter summary:
{self.last_chapter_summary}

Chapter {self.chapter_num}:
{plot}
"""
