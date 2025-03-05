TOOL_SCHEMA = {
    "name": "add_calendar_event",
    "description": "Add a calendar event",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title of the event.",
            },
            "description": {
                "type": "string",
                "description": "The detailed description of the event, including the people involved and their roles, if any.",
            },
            "url": {
                "type": "string",
                "description": "Event url",
            },
            "start_time_converted_in_milliseconds": {
                "type": "string",
                "description": "The start date and time converted in milliseconds since epoch",
            },
            "end_time_converted_in_milliseconds": {
                "type": "string",
                "description": "The start date and time converted in milliseconds since epoch. If not given, return 1 hour later than the start_time_converted_in_milliseconds",
            },
            "location": {
                "type": "string",
                "description": "The location or venue of the event.",
            },
        },
        "required": ["title", "description"],
    },
}

def add_calendar_event(title: str, description: str, url: str="", start_time_converted_in_milliseconds: str="", end_time_converted_in_milliseconds: str="", location: str="", **kwargs):
    import subprocess

    start_time = start_time_converted_in_milliseconds
    end_time = end_time_converted_in_milliseconds

    insert_url = f"\nURL: {url}\n" if url else ""
    insert_location = f"\nLocation: {location}" if location else ""
    description = f'''{description}{insert_url}{insert_location}'''.replace('"', '\\"')

    cli = f'''am start -a android.intent.action.INSERT -t vnd.android.cursor.item/event -e title "{title}" -e description "{description}" -e beginTime {start_time} -e endTime {end_time} -e location {location}'''
    subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return ""

TOOL_FUNCTION = add_calendar_event