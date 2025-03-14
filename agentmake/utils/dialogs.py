from prompt_toolkit.shortcuts import checkboxlist_dialog, radiolist_dialog
from prompt_toolkit import HTML

def getMultipleSelection(title="Multiple Selection", text="Select item(s):", options=["ALL"], descriptions=[], default_values=["ALL"]):
    if descriptions:
        values = [(option, descriptions[index]) for index, option in enumerate(options)]
    else:
        values = [(option, option) for option in options]
    return checkboxlist_dialog(
        title=title,
        text=text,
        values=values,
        default_values=default_values,
        #style=self.style,
    ).run()

def getValidOptions(options=[], descriptions=[], bold_descriptions=False, filter="", default="", title="Available Options", text="Select an option:"):
    if not options:
        return ""
    filter = filter.strip().lower()
    if descriptions:
        descriptionslower = [i.lower() for i in descriptions]
        values = [(option, HTML(f"<b>{descriptions[index]}</b>") if bold_descriptions else descriptions[index]) for index, option in enumerate(options) if (filter in option.lower() or filter in descriptionslower[index])]
    else:
        values = [(option, option) for option in options if filter in option.lower()]
    if not values:
        if descriptions:
            values = [(option, HTML(f"<b>{descriptions[index]}</b>") if bold_descriptions else descriptions[index]) for index, option in enumerate(options)]
        else:
            values = [(option, option) for option in options]
    result = radiolist_dialog(
        title=title,
        text=text,
        values=values,
        default=default if default and default in options else values[0][0],
        #style=self.style,
    ).run()
    if result:
        return result
    return ""