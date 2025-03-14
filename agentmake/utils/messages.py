from agentmake import config, writeTextFile, readTextFile, PACKAGE_PATH, DEFAULT_TEXT_EDITOR
from agentmake.utils.dialogs import getValidOptions, getMultipleSelection
import os

def trimMessages():
    def getEditableContent(role, item):
        content = item.get("content", "")
        editableContent = f"[{role}] {content}"
        if len(editableContent) > 50:
            editableContent = editableContent[:50] + " ..."
        return editableContent
    editable = {}
    lastUserItem = 0
    editableContent = ""
    for index, item in enumerate(config.messages):
        role = item.get("role", "")
        if role == "user":
            editableContent = getEditableContent(role, item)
            lastUserItem = index
        elif role == "assistant":
            editableContent += " " + getEditableContent(role, item)
            editable[f"{lastUserItem}.{index}"] = editableContent
    if editable:
        selectedItems = getMultipleSelection(
            title="Trim Current Conversation",
            text="Select the items to be removed:",
            options=editable.keys(),
            descriptions=list(editable.values()),
            default_values=[],
        )
        if selectedItems is not None:
            for i in selectedItems:
                user, assistant = i.split(".")
                del config.messages[int(assistant)]
                del config.messages[int(user)]
            #showMessages(config.messages)
    else:
        print("No editable item found!")

def editMessages():
    editableContent, editItemIndex = getCurrentMessagesItem(instruction="Select the item to be edited:")
    if editItemIndex is not None:
        tempTextFile = os.path.join(PACKAGE_PATH, "temp", "editableItem.txt")
        # write previous response in a temp file
        writeTextFile(tempTextFile, editableContent)
        # editing
        os.system(f"{DEFAULT_TEXT_EDITOR} {tempTextFile}")
        # read edited response
        editedContent = readTextFile(tempTextFile)
        # save changes
        if not (editableContent == editedContent):
            config.messages[editItemIndex]["content"] = editedContent
            #showMessages(config.messages)

def getCurrentMessagesItem(instruction="Select an item:"):
    editable = {}
    lastItem = 0
    for index, item in enumerate(config.messages):
        role = item.get("role", "")
        if role in ("user", "assistant"):
            content = item.get("content", "")
            editableContent = f"[{role}] {content}"
            if len(editableContent) > 50:
                editableContent = editableContent[:50] + " ..."
            editable[str(index)] = editableContent
            lastItem = index
    if editable:
        editItem = getValidOptions(
            options=editable.keys(),
            descriptions=list(editable.values()),
            title="Edit Current Conversation",
            default=str(lastItem),
            text=instruction,
        )
        if editItem:
            editItemIndex = int(editItem)
            editableContent = config.messages[editItemIndex]["content"]
            return editableContent, editItemIndex
    else:
        print("No editable item found!")
    return None, None