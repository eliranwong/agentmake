def create_image_genai9x16(messages, **kwargs):

    import os, shutil
    import shutil
    from agentmake import getOpenCommand, getCurrentDateTime
    from agentmake import GenaiAI
    from google.genai.types import GenerateImagesConfig

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
    response = GenaiAI.getClient().models.generate_images(
        model=os.getenv("VERTEXAI_IMAGEN_MODEL") if os.getenv("VERTEXAI_IMAGEN_MODEL") else "imagen-3.0-generate-002",
        prompt=image_prompt,
        config=GenerateImagesConfig(
            number_of_images=1,
            include_rai_reason=True,
            output_mime_type='image/png',
            aspect_ratio="9:16", # "1:1", "9:16", "16:9", "4:3", "3:4"
        ),
    )
    """
    aspect_ratio: Aspect ratio for the image. Supported values are:
        * 1:1 - Square image
        * 9:16 - Portait image
        * 16:9 - Landscape image
        * 4:3 - Landscape, desktop ratio.
        * 3:4 - Portrait, desktop ratio
    """
    # save image
    response.generated_images[0].image.save(imageFile)
    # open image
    openImageFile(imageFile)
    return ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Create a portrait-oriented image with Imagen model in 9:16 ratio."""

TOOL_FUNCTION = create_image_genai9x16