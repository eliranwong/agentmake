from agentmake import AGENTMAKE_USER_DIR, USER_OS
from pathlib import Path
import os, shutil, json

def getOllamaModelDir():
    # read https://github.com/ollama/ollama/blob/main/docs/faq.md#where-are-models-stored
    OLLAMA_MODELS = os.getenv("OLLAMA_MODELS")
    if not OLLAMA_MODELS or (OLLAMA_MODELS and not os.path.isdir(OLLAMA_MODELS)):
        os.environ['OLLAMA_MODELS'] = ""

    if os.environ['OLLAMA_MODELS']:
        return os.environ['OLLAMA_MODELS']
    elif USER_OS == "Windows":
        modelDir = os.path.expanduser(r"~\.ollama\models")
    elif USER_OS == "macOS":
        modelDir = os.path.expanduser("~/.ollama/models")
    elif USER_OS == "Linux":
        modelDir = "/usr/share/ollama/.ollama/models"
        modelDir2 = os.path.expanduser("~/.ollama/models")
        if not os.path.isdir(modelDir) and os.path.isdir(modelDir2):
            modelDir = modelDir2
    
    if os.path.isdir(modelDir):
        return modelDir
    return ""

def getDownloadedOllamaModels(library:str="library") -> dict:
    models = {}
    if modelDir := getOllamaModelDir():
        library = os.path.join(modelDir, "manifests", "registry.ollama.ai", library)
        if os.path.isdir(library):
            for d in os.listdir(library):
                model_dir = os.path.join(library, d)
                if os.path.isdir(model_dir):
                    for f in os.listdir(model_dir):
                        manifest = os.path.join(model_dir, f)
                        if os.path.isfile(manifest):
                            try:
                                with open(manifest, "r", encoding="utf-8") as fileObj:
                                    content = fileObj.read()
                                model_file = json.loads(content)["layers"][0]["digest"]
                                if model_file:
                                    model_file = model_file.replace(":", "-")
                                    model_file = os.path.join(modelDir, "blobs", model_file)
                                    if os.path.isfile(model_file):
                                        model_tag = f"{d}:{f}"
                                        models[model_tag] = model_file
                                        if f == "latest":
                                            models[d] = model_file
                            except:
                                pass
    return models

def exportOllamaModels(selection: list=[]) -> list:
    print("# Exporting Ollama models ...")
    gguf_directory = os.path.join(AGENTMAKE_USER_DIR, "models", "gguf")
    Path(gguf_directory).mkdir(parents=True, exist_ok=True)
    if not selection:
        # get all models if no selection specified
        selection = list(getDownloadedOllamaModels().keys())
    selection = [i.replace(":latest", "") if i.endswith(":latest") else i for i in selection]
    exportedFiles = []
    for i in selection:
        if "/" in i:
            library, model = i.split("/", 1)
            exported_filename = library + "_" + model.replace(":", "_")
        else:
            library, model = "library", i
            exported_filename = model.replace(":", "_")
        exported_path = os.path.join(gguf_directory, f"{exported_filename}.gguf")
        if not os.path.isfile(exported_path):
            models = getDownloadedOllamaModels(library)
            if model in models:
                shutil.copy2(models[model], exported_path)
                if os.path.isfile(exported_path):
                    print(f"Model: {model}")
                    print(f"Exported: {exported_path}")
                    exportedFiles.append(exported_path)
            else:
                print(f"Model '{model}' not found!")
    return exportedFiles

if __name__ == "__main__":
    exportOllamaModels(["mistral"])