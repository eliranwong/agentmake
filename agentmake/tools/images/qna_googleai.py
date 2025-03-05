from typing import Union

def examine_images_googleai(query: str, image_filepath: Union[str, list], **kwargs):
    
    from agentmake.utils.images import is_valid_image_file, is_valid_image_url, encode_image
    from agentmake.utils.online import is_valid_url
    from agentmake import GoogleaiAI
    import os

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
            content.append({"type": "image_url", "image_url": {"url": i,},})
        elif os.path.isfile(i) and is_valid_image_file(i):
            content.append({"type": "image_url", "image_url": {"url": encode_image(i)},})
        else:
            image_filepath.remove(i)

    if content:
        client = GoogleaiAI.getClient()

        content.insert(0, {"type": "text", "text": query,})

        response = client.chat.completions.create(
            model=os.getenv("GOOGLEAI_VISUAL_MODEL") if os.getenv("GOOGLEAI_VISUAL_MODEL") else "gemini-1.5-pro",
            messages=[
                {
                "role": "user",
                "content": content,
                }
            ],
            temperature=float(os.getenv("GOOGLEAI_VISUAL_TEMPERATURE")) if os.getenv("GOOGLEAI_VISUAL_TEMPERATURE") else 0.3,
            max_tokens=int(os.getenv("GOOGLEAI_VISUAL_MAX_TOKENS")) if os.getenv("GOOGLEAI_VISUAL_MAX_TOKENS") else 4096,
        )
        answer = response.choices[0].message.content

        # display answer
        print("```assistant")
        print(answer)
        print("```")

        return ""
    return None

TOOL_SCHEMA = {
    "name": "examine_images_googleai",
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

TOOL_FUNCTION = examine_images_googleai
