def create_image_openai_landscape(messages, **kwargs):

    import os, shutil
    from base64 import b64decode
    import shutil
    from agentmake import config, getOpenCommand, getCurrentDateTime
    from agentmake import OpenaiAI

    image_prompt = messages[-1].get("content", "")
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
        
    imageFile = os.path.join(os.getcwd(), f"image_{getCurrentDateTime()}.png")

    # get responses
    #https://platform.openai.com/docs/guides/images/introduction
    response = OpenaiAI.getClient().images.generate(
        model="dall-e-3",
        prompt=image_prompt,
        size="1792x1024", # "1024x1024", "1024x1792", "1792x1024"
        quality="hd", # "hd" or "standard"
        response_format="b64_json",
        n=1,
    )
    # open image
    #imageUrl = response.data[0].url
    #jsonFile = os.path.join(config.toolMateAIFolder, "temp", "openai_image.json")
    #with open(jsonFile, mode="w", encoding="utf-8") as fileObj:
    #    json.dump(response.data[0].b64_json, fileObj)
    image_data = b64decode(response.data[0].b64_json)
    with open(imageFile, mode="wb") as pngObj:
        pngObj.write(image_data)
    openImageFile(imageFile)
    # close connection
    config.openai_client.close()
    config.openai_client = None
    return ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Create a landscape-oriented image with OpenAI Dall E 3 model."""

TOOL_FUNCTION = create_image_openai_landscape