from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["rembg", "onnxruntime"]
try:
    import rembg
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import rembg

def remove_image_background(image_filepath: str, **kwargs):
    from agentmake.utils.images import is_valid_image_file
    import os, rembg

    if isinstance(image_filepath, str):
        if not image_filepath.startswith("["):
            image_filepath = f'["{image_filepath}"]'
        image_filepath = eval(image_filepath)
    if not image_filepath:
        return None

    filesCopy = image_filepath[:]
    for item in filesCopy:
        if os.path.isdir(item):
            for root, _, allfiles in os.walk(item):
                for file in allfiles:
                    file_path = os.path.join(root, file)
                    image_filepath.append(file_path)
            image_filepath.remove(item)

    for input_path in image_filepath:
        if is_valid_image_file(input_path):
            output_path = f"{input_path}_no_bg.png"
            with open(input_path, 'rb') as i:
                with open(output_path, 'wb') as o:
                    print(f"Reading image file: {input_path}")
                    img = rembg.remove(i.read())
                    o.write(img)
                    print(f"File saved: {output_path}")
        else:
            print(f"'{input_path}' is not an image file!")
    return ""

TOOL_SCHEMA = {
    "name": "remove_image_background",
    "description": f'''Remove image background''',
    "parameters": {
        "type": "object",
        "properties": {
            "image_filepath": {
                "type": "string",
                "description": """Return a list of image paths, e.g. '["image1.png", "/tmp/image2.png"]'. Return '[]' if image path is not provided.""",
            },
        },
        "required": ["image_filepath"],
    },
}

TOOL_FUNCTION = remove_image_background