import os, html2text, html
from typing import Union

def readTextFile(textFile: str) -> Union[str, None]:
    if not os.path.isfile(textFile):
        return None
    with open(textFile, 'r', encoding='utf8') as fileObj:
        content = fileObj.read()
    return content if content else ""

def writeTextFile(textFile: str, textContent: str) -> None:
    with open(textFile, "w", encoding="utf-8") as fileObj:
        fileObj.write(textContent)

# Function to convert HTML to Markdown
def htmlToMarkdown(html_string):
    # Create an instance of the HTML2Text converter
    converter = html2text.HTML2Text()
    # Convert the HTML string to Markdown
    markdown_string = converter.handle(html_string)
    # Return the Markdown string
    return markdown_string

def plainTextToUrl(text):
    # https://wiki.python.org/moin/EscapingHtml
    text = html.escape(text)
    searchReplace = (
        (" ", "%20"),
        ("\n", "%0D%0A"),
    )
    for search, replace in searchReplace:
        text = text.replace(search, replace)
    return text