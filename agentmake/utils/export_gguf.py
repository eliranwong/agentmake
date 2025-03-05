from agentmake import AGENTMAKE_USER_DIR
from pathlib import Path
import os, shutil, platform, json

def getOllamaModelDir():
    thisPlatform = platform.system()
    # read https://github.com/ollama/ollama/blob/main/docs/faq.md#where-are-models-stored
    OLLAMA_MODELS = os.getenv("OLLAMA_MODELS")
    if not OLLAMA_MODELS or (OLLAMA_MODELS and not os.path.isdir(OLLAMA_MODELS)):
        os.environ['OLLAMA_MODELS'] = ""

    if os.environ['OLLAMA_MODELS']:
        return os.environ['OLLAMA_MODELS']
    elif thisPlatform == "Windows":
        modelDir = os.path.expanduser(r"~\.ollama\models")
    elif thisPlatform == "macOS":
        modelDir = os.path.expanduser("~/.ollama/models")
    elif thisPlatform == "Linux":
        modelDir = "/usr/share/ollama/.ollama/models"
        modelDir2 = os.path.expanduser("~/.ollama/models")
        if not os.path.isdir(modelDir) and os.path.isdir(modelDir2):
            modelDir = modelDir2
    
    if os.path.isdir(modelDir):
        return modelDir
    return ""

def getDownloadedOllamaModels() -> dict:
    models = {}
    if modelDir := getOllamaModelDir():
        library = os.path.join(modelDir, "manifests", "registry.ollama.ai", "library")
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
    models = getDownloadedOllamaModels()
    exportedFiles = []
    for model, originalpath in models.items():
        filename = model.replace(":", "_")
        exportpath = os.path.join(gguf_directory, f"{filename}.gguf")
        if not os.path.isfile(exportpath) and not model.endswith(":latest") and ((not selection) or (model in selection)):
            print(f"Model: {model}")
            shutil.copy2(originalpath, exportpath)
            print(f"Exported: {exportpath}")
        if os.path.isfile(exportpath):
            exportedFiles.append(exportpath)
    return exportedFiles

if __name__ == "__main__":
    exportOllamaModels(["mistral"])