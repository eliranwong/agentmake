import os
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