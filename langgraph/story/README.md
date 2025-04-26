```
from libs import llm_factory
from story.story import Story, Chapter
from story.agents import SynopsisGeneration, ChapterPlotWriter, ChapterSummarizer, ChapterWriter
from libs.graph import Graph
import logging
import os
from story.graph import graph

logging.basicConfig(level=logging.DEBUG)

from IPython.display import Image
Image(graph.get_graph().draw_png())

llm = llm_factory.create("local")

graph.invoke({"message": [], "story": Story(
    instruction="Use language 6th grader can understand",
    synopsis="The story is about a snow white who is full of pride.  She always thought she was the most beautiful girl in the town.  It turns out the queen is the most beautiful.",
    number_of_chapters=5
).dict()})
```
