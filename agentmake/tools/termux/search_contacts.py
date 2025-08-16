def search_contacts(search_item: str, **kwargs):
    import subprocess, json
    found = []
    contacts = subprocess.run("termux-contact-list", shell=True, capture_output=True, text=True).stdout
    contacts = json.loads(contacts)
    for i in contacts:
        name = i.get("name", "")
        number = i.get("number", "")
        if search_item in name or search_item in number:
            foundItem = f"{name}: {number}"
            found.append(foundItem)
    if found:
        print("\n".join(found))
    return ""

TOOL_SCHEMA = {
    "name": "search_contacts",
    "description": f'''Search for an item in my contact records''',
    "parameters": {
        "type": "object",
        "properties": {
            "search_item": {
                "type": "string",
                "description": "The search string for performing the search",
            },
        },
        "required": ["search_item"],
    },
}

TOOL_FUNCTION = search_contacts
