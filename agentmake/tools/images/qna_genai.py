from typing import Union

def examine_images_genai(query: str, image_filepath: Union[str, list], **kwargs):
    
    from agentmake.utils.images import is_valid_image_file, is_valid_image_url, encode_image
    from agentmake.utils.online import is_valid_url
    from agentmake import GenaiAI
    from google.genai.types import Content, GenerateContentConfig, SafetySetting, Tool, Part, HttpOptions
    import os, re

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

    content = [Part.from_text(text=query)]
    # valid image paths
    for i in image_filepath:
        if is_valid_url(i) and is_valid_image_url(i):
            content.append({"type": "image_url", "image_url": {"url": i,},})
        elif os.path.isfile(i) and is_valid_image_file(i):
            #content.append({"type": "image_url", "image_url": {"url": encode_image(i)},})
            with open(i, 'rb') as f:
                image_bytes = f.read()
            ext = re.sub(r"^.*?\.([A-Za-z]+?)$", r"\1", i)
            content.append(Part.from_bytes(data=image_bytes, mime_type=f"image/{ext.lower() if ext else 'png'}"))
        else:
            image_filepath.remove(i)

    if content:
        #client = OpenaiAI.getClient()

        #content.insert(0, {"type": "text", "text": query,})

        response = client.chat.completions.create(
            model=os.getenv("VERTEXAI_VISUAL_MODEL") if os.getenv("VERTEXAI_VISUAL_MODEL") else "gemini-1.5-pro",
            messages=[
                {
                "role": "user",
                "content": content,
                }
            ],
            max_tokens=4096,
        )
        answer = response.choices[0].message.content

        # display answer
        print("```assistant")
        print(answer)
        print("```")

        return ""
    return None

TOOL_SCHEMA = {
    "name": "examine_images_genai",
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

TOOL_FUNCTION = examine_images_genai
