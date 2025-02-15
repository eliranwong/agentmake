def create_image_genai(messages, **kwargs):

    import os, shutil
    import shutil
    from agentmake import config, getOpenCommand, getCurrentDateTime
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
        model='imagen-3.0-generate-002',
        prompt=image_prompt,
        config=GenerateImagesConfig(
            number_of_images=1,
            include_rai_reason=True,
            output_mime_type='image/png',
        ),
    )
    # save image
    response.generated_images[0].image.save(imageFile)
    # open image
    openImageFile(imageFile)
    return ""

TOOL_SCHEMA = {}

TOOL_FUNCTION = create_image_genai