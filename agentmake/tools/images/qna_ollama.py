from typing import Union

def examine_images_ollama(query: str, image_filepath: Union[str, list], **kwargs):
    
    from agentmake.utils.images import is_valid_image_file, is_valid_image_url
    from agentmake.utils.online import is_valid_url
    from agentmake import OllamaAI
    from ollama import Options
    import os
    import http.client
    import urllib.request
    from typing import cast

    OLLAMA_VISUAL_MODEL = os.getenv("OLLAMA_VISUAL_MODEL") if os.getenv("OLLAMA_VISUAL_MODEL") else "llava-phi3"
    OllamaAI.downloadModel(OLLAMA_VISUAL_MODEL)

    if isinstance(image_filepath, str):
        if not image_filepath.startswith("["):
            image_filepath = f'["{image_filepath}"]'
        image_filepath = eval(image_filepath)

    filesCopy = image_filepath[:]
    for item in filesCopy:
        if os.path.isdir(item):
            for root, _, allfiles in os.walk(item):
                for file in allfiles:
                    file_path = os.path.join(root, file)
                    image_filepath.append(file_path)
            image_filepath.remove(item)

    content = []
    # valid image paths
    for i in image_filepath:
        if is_valid_url(i) and is_valid_image_url(i):
            with urllib.request.urlopen(i) as response:
                response = cast(http.client.HTTPResponse, response)
                image_bytes = response.read()
            content.append(image_bytes)
        elif os.path.isfile(i) and is_valid_image_file(i):
            #content.append(i) # a path of raw bytes
            with open(i, 'rb') as f:
                image_bytes = f.read()
            content.append(image_bytes)
        #else:
            #image_filepath.remove(i)

    if content:
        client = OllamaAI.getClient()

        response = client.chat(
            model=OLLAMA_VISUAL_MODEL,
            messages=[{'role': 'user', 'content': query, 'images': content}],
            options=Options(
                num_predict=2048,
                temperature=float(os.getenv("OLLAMA_VISUAL_TEMPERATURE")) if os.getenv("OLLAMA_VISUAL_TEMPERATURE") else 0.3,
                num_predict=int(os.getenv("OLLAMA_VISUAL_MAX_TOKENS")) if os.getenv("OLLAMA_VISUAL_MAX_TOKENS") else -1,
            ),
        )
        answer = response.message.content

        # display answer
        print("```assistant")
        print(answer)
        print("```")

        return ""
    return None

TOOL_SCHEMA = {
    "name": "examine_images_ollama",
    "description": "Describe or ask question about the given images",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Questions or query about the images",
            },
            "image_filepath": {
                "type": "string",
                "description": """Return a list of image paths or urls, e.g. '["image1.png", "/tmp/image2.png", "https://letmedoit.ai/image.png"]'. Return '[]' if image path is not provided.""",
            },
        },
        "required": ["query", "image_filepath"],
    },
}

TOOL_FUNCTION = examine_images_ollama
