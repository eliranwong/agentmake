"""
Automate create of teams of agents to work on user requests.

# To install AgentMake AI first, run:
> pip install agentmake

# To configure XAI API key in AgentMake AI settings, run:
> ai -ec
"""

from agentmake import agentmake
from agentmake.plugins.uba.lib.BibleBooks import BibleBooks

bible_books = BibleBooks.abbrev["eng"]

for i in range(1,67):
    book_name = bible_books.get(str(i))[-1]
    instructions = (
        f"Write a comprehensive and detailed introduction to the book of '{book_name}' in the Bible.",
        f"Write a comprehensive and detailed bible study guide for studying the book of '{book_name}' in the Bible.",
    )
    for ii in instructions:
        agentmake(ii, agent="teamwork", backend="xai", max_tokens=8192)