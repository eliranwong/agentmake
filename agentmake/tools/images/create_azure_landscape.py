import os, shutil
from base64 import b64decode
import shutil
from agentmake import config, getOpenCommand
from agentmake.utils.system import getCurrentDateTime
from agentmake.backends.azure import AzureAI


def create_image_azure_landscape(messages, **kwargs):
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

    azure_dalle_model = os.getenv("AZURE_DALLE_MODEL") if os.getenv("AZURE_DALLE_MODEL") else "dall-e-3"

    # get responses
    #https://platform.openai.com/docs/guides/images/introduction
    response = AzureAI.getDalleClient().images.generate(
        model=azure_dalle_model,
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
    config.azure_client.close()
    config.azure_client = None
    return ""

TOOL_SCHEMA = {}

TOOL_FUNCTION = create_image_azure_landscape