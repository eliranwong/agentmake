from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["stable-diffusion-cpp-python"]
try:
    from stable_diffusion_cpp import StableDiffusion
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    from stable_diffusion_cpp import StableDiffusion

def create_image_flux_portrait(messages, **kwargs):

    from stable_diffusion_cpp import StableDiffusion

    from agentmake import AGENTMAKE_USER_DIR
    from agentmake import config, getOpenCommand
    from agentmake.utils.system import getCurrentDateTime, getCpuThreads

    import os, shutil, subprocess
    from pathlib import Path
    from huggingface_hub import hf_hub_download

    FLUX_IMAGE_MODEL = os.getenv("FLUX_IMAGE_MODEL") if os.getenv("FLUX_IMAGE_MODEL") else "flux1-dev-q4_k.gguf"
    FLUX_IMAGE_WIDTH = int(os.getenv("FLUX_IMAGE_HEIGHT")) if os.getenv("FLUX_IMAGE_HEIGHT") else 1088
    FLUX_IMAGE_HEIGHT = int(os.getenv("FLUX_IMAGE_WIDTH")) if os.getenv("FLUX_IMAGE_WIDTH") else 1920
    FLUX_IMAGE_SAMPLE_STEPS = int(os.getenv("FLUX_IMAGE_SAMPLE_STEPS")) if os.getenv("FLUX_IMAGE_SAMPLE_STEPS") else 20


    def downloadFluxModels():
        # reference: https://github.com/william-murray1204/stable-diffusion-cpp-python#flux-image-generation
        # llm directory
        llm_directory = os.path.join(AGENTMAKE_USER_DIR, "models", "flux")
        Path(llm_directory).mkdir(parents=True, exist_ok=True)
        lora_model_dir = os.path.join(llm_directory, "lora")
        Path(lora_model_dir).mkdir(parents=True, exist_ok=True)
        filename = FLUX_IMAGE_MODEL
        flux_model_path = os.path.join(llm_directory, filename)

        if not os.path.isfile(flux_model_path):
            print("Downloading Flux.1-dev model ...")
            hf_hub_download(
                repo_id="leejet/FLUX.1-dev-gguf",
                filename=filename,
                local_dir=llm_directory,
                #local_dir_use_symlinks=False,
            )

        filename = "ae.safetensors"
        lora_file = os.path.join(llm_directory, filename)
        if not os.path.isfile(lora_file):
            #print("Downloading Flux.1 vae ...")
            #hf_hub_download(
            #    repo_id="black-forest-labs/FLUX.1-dev",
            #    filename=filename,
            #    local_dir=llm_directory,
            #    #local_dir_use_symlinks=False,
            #)
            print(f"You need to manually download the file `ae.safetensors` from https://huggingface.co/black-forest-labs/FLUX.1-dev and place it in `{llm_directory}`.")
            return ""

        filename = "clip_l.safetensors"
        lora_file = os.path.join(llm_directory, filename)
        if not os.path.isfile(lora_file):
            print("Downloading Flux.1 clip_l ...")
            hf_hub_download(
                repo_id="comfyanonymous/flux_text_encoders",
                filename=filename,
                local_dir=llm_directory,
                #local_dir_use_symlinks=False,
            )

        filename = "t5xxl_fp16.safetensors"
        lora_file = os.path.join(llm_directory, filename)
        if not os.path.isfile(lora_file):
            print("Downloading Flux.1 t5xxl ...")
            hf_hub_download(
                repo_id="comfyanonymous/flux_text_encoders",
                filename=filename,
                local_dir=llm_directory,
                #local_dir_use_symlinks=False,
            )
        
        return flux_model_path

    image_prompt = messages[-1].get("content", "")
    def callback(step: int, steps: int, time: float):
        print("Completed step: {} of {}".format(step, steps))

    def openImageFile(imageFile):
        openCmd = getOpenCommand()
        if shutil.which("termux-share"):
            os.system(f"termux-share {imageFile}")
        elif shutil.which(openCmd):
            cli = f"{openCmd} {imageFile}"
            #os.system(cli)
            subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        message = f"Image saved: {imageFile}"
        print(message)

    # image file path
    imageFile = os.path.join(os.getcwd(), f"image_{getCurrentDateTime()}.png")

    flux_model_path = downloadFluxModels()
    if not flux_model_path:
        return ""

    llm_directory = os.path.join(AGENTMAKE_USER_DIR, "models", "flux")
    lora_model_dir = os.path.join(llm_directory, "lora")
    flux = StableDiffusion(
        diffusion_model_path=flux_model_path,
        lora_model_dir=lora_model_dir if flux_model_path.endswith("flux1-dev-q8_0.gguf") else "", # Only the Flux-dev q8_0 will work with LoRAs.
        wtype="default", # Weight type (options: default, f32, f16, q4_0, q4_1, q5_0, q5_1, q8_0)
        # seed=1337, # Uncomment to set a specific seed
        verbose=False,
        n_threads=getCpuThreads(),
        clip_l_path=os.path.join(llm_directory, "clip_l.safetensors"),
        t5xxl_path=os.path.join(llm_directory, "t5xxl_fp16.safetensors"),
        vae_path=os.path.join(llm_directory, "ae.safetensors"),
    )
    flux.txt_to_img(
        image_prompt,
        width=config.image_width if hasattr(config, "local_image_width") and config.image_width else FLUX_IMAGE_WIDTH,
        height=config.image_height if hasattr(config, "local_image_height") and config.image_height else FLUX_IMAGE_HEIGHT,
        sample_steps=config.image_sample_steps if hasattr(config, "local_image_sample_steps") and config.image_sample_steps else FLUX_IMAGE_SAMPLE_STEPS,
        cfg_scale=1.0, # a cfg_scale of 1 is recommended for FLUX
        sample_method="euler", # euler is recommended for FLUX
        progress_callback=callback,
    )[0].save(imageFile)
    del flux
    openImageFile(imageFile)
    return ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Create a portrait-oriented image with Flux model."""

TOOL_FUNCTION = create_image_flux_portrait