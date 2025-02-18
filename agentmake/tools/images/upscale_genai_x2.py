from typing import Union

def upscale_images_genai(image_filepath: Union[str, list], **kwargs):
    
    from agentmake import getOpenCommand, getCurrentDateTime
    from agentmake.utils.images import is_valid_image_file, is_valid_image_url
    from agentmake.utils.online import is_valid_url
    from agentmake import GenaiAI
    from google.genai.types import Image, UpscaleImageConfig
    import http.client
    import urllib.request
    from typing import cast
    import os, re, shutil

    def openImageFile(imageFile):
        openCmd = getOpenCommand()
        if shutil.which("termux-share"):
            os.system(f"termux-share {imageFile}")
        elif shutil.which(openCmd):
            cli = f"{openCmd} {imageFile}"
            os.system(cli)
            #subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        message = f"Image saved: {imageFile}"
        print(message)

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

    client = GenaiAI.getClient()
    # valid image paths
    for i in image_filepath:
        if is_valid_url(i) and is_valid_image_url(i):
            with urllib.request.urlopen(i) as response:
                response = cast(http.client.HTTPResponse, response)
                image_bytes = response.read()
            ext = re.sub(r"^.*?\.([A-Za-z]+?)$", r"\1", i)
            image = Image(image_bytes=image_bytes, mime_type=f"image/{ext.lower() if ext else 'png'}")
            new_imageFile = os.path.join(os.getcwd(), f"image_{getCurrentDateTime()}.{ext}")
        elif os.path.isfile(i) and is_valid_image_file(i):
            with open(i, 'rb') as f:
                image_bytes = f.read()
            ext = re.sub(r"^.*?\.([A-Za-z]+?)$", r"\1", i)
            image = Image(image_bytes=image_bytes, mime_type=f"image/{ext.lower() if ext else 'png'}")
            ext_len = len(ext) + 1
            new_imageFile = i[:(0-ext_len)] + f"_x2.{ext}"
        response = client.models.upscale_image(
            model=os.getenv("VERTEXAI_IMAGEN_MODEL") if os.getenv("VERTEXAI_IMAGEN_MODEL") else "imagen-3.0-generate-002",
            image=image,
            upscale_factor="x2",
            config=UpscaleImageConfig(
                include_rai_reason=True,
                output_mime_type=f"image/{ext}",
            ),
        )
        # save image
        response.generated_images[0].image.save(new_imageFile)
        # open image
        openImageFile(new_imageFile)
    return ""

TOOL_SCHEMA = {
    "name": "upscale_images_genai",
    "description": "Upscale or double the size of images",
    "parameters": {
        "type": "object",
        "properties": {
            "image_filepath": {
                "type": "string",
                "description": """Return a list of image paths or urls, e.g. '["image1.png", "/tmp/image2.png", "https://letmedoit.ai/image.png"]'. Return '[]' if image path is not provided.""",
            },
        },
        "required": ["image_filepath"],
    },
}

TOOL_FUNCTION = upscale_images_genai
