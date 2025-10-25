from agentmake import config
from ..utils.online import get_local_ip
from ..utils.schema import getParameterSchema
from typing import Optional
from tqdm import tqdm
from ollama import Options, ResponseError
from ollama._types import ChatResponse
from ollama import Client
import re, os, json, traceback

DEVELOPER_MODE = True if os.getenv("DEVELOPER_MODE") and os.getenv("DEVELOPER_MODE").upper() == "TRUE" else False

class OllamaAI:

    DEFAULT_API_KEY = os.getenv("OLLAMA_API_KEY").split(",") if os.getenv("OLLAMA_API_KEY") else ["agentmake"]
    DEFAULT_ENDPOINT = os.getenv("OLLAMA_ENDPOINT") if os.getenv("OLLAMA_ENDPOINT") else f"http://{get_local_ip()}:11434"
    DEFAULT_MODEL = os.getenv("OLLAMA_MODEL") if os.getenv("OLLAMA_MODEL") else "llama3.2"
    DEFAULT_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE")) if os.getenv("OLLAMA_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS")) if os.getenv("OLLAMA_MAX_TOKENS") else -1
    DEFAULT_CONTEXT_WINDOW = int(os.getenv("OLLAMA_CONTEXT_WINDOW")) if os.getenv("OLLAMA_CONTEXT_WINDOW") else 2048
    DEFAULT_BATCH_SIZE = int(os.getenv("OLLAMA_BATCH_SIZE")) if os.getenv("OLLAMA_BATCH_SIZE") else 512
    DEFAULT_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE") if os.getenv("OLLAMA_KEEP_ALIVE") else "5m"

    @staticmethod
    def getApiKey():
        # rotate multiple API keys
        if len(OllamaAI.DEFAULT_API_KEY) > 1:
            first_item = OllamaAI.DEFAULT_API_KEY.pop(0)
            OllamaAI.DEFAULT_API_KEY.append(first_item)
        return OllamaAI.DEFAULT_API_KEY[0]

    @staticmethod
    def getClient(api_endpoint: Optional[str]=None, api_key: Optional[str]=None):
        config.ollama_client = Client(
            host=api_endpoint if api_endpoint else OllamaAI.DEFAULT_ENDPOINT,
            headers={'Authorization': 'Bearer ' + (api_key if api_key else OllamaAI.getApiKey())}
        )
        return config.ollama_client

    @staticmethod
    def getChatCompletion(
        messages: list,
        model: Optional[str]=None,
        model_keep_alive: Optional[str]=None,
        schema: Optional[dict]=None,
        temperature: Optional[float]=None, 
        max_tokens: Optional[int]=None,
        context_window: Optional[int]=None, # applicable to ollama only
        batch_size: Optional[int]=None, # applicable to ollama only
        prefill: Optional[str]=None,
        stop: Optional[list]=None,
        stream: Optional[bool]=False,
        api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
        api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        **kwargs,
    ) -> ChatResponse:
        if prefill:
            messages.append({'role': 'assistant', 'content': prefill})
        model = model if model else OllamaAI.DEFAULT_MODEL
        # Note: custom client, like Client(host=api_endpoint if api_endpoint else OllamaAI.DEFAULT_ENDPOINT), rasies resource warning
        # download model if it is not in the model list
        os.environ["OLLAMA_HOST"] = api_endpoint if api_endpoint else OllamaAI.DEFAULT_ENDPOINT
        if not os.getenv("OLLAMA_HOST").startswith("https://"):
            OllamaAI.downloadModel(model)
        completion = None
        used_api_keys = []
        while completion is None:
            this_api_key = api_key if api_key else OllamaAI.getApiKey()
            if this_api_key in used_api_keys:
                break
            else:
                used_api_keys.append(this_api_key)
            try:
                completion = OllamaAI.getClient(api_endpoint=os.getenv("OLLAMA_HOST"), api_key=this_api_key).chat(
                    keep_alive=model_keep_alive if model_keep_alive else OllamaAI.DEFAULT_KEEP_ALIVE,
                    model=model,
                    messages=messages,
                    format=getParameterSchema(schema) if schema else None,
                    stream=stream,
                    options=Options(
                        temperature=temperature if temperature is not None else OllamaAI.DEFAULT_TEMPERATURE,
                        num_ctx=context_window if context_window is not None else OllamaAI.DEFAULT_CONTEXT_WINDOW,
                        num_batch=batch_size if batch_size is not None else OllamaAI.DEFAULT_BATCH_SIZE,
                        num_predict=None if os.getenv("OLLAMA_HOST") == "https://ollama.com" else max_tokens if max_tokens else OllamaAI.DEFAULT_MAX_TOKENS,
                        stop=stop,
                        **kwargs,
                    ),
                )
            except Exception as e:
                print(f"An error occurred: {e}")
                if DEVELOPER_MODE:
                    print(traceback.format_exc())
                print(f"Failed API key: {this_api_key}")
        return completion

    @staticmethod
    def getDictionaryOutput(
        messages: list,
        schema: dict,
        model: Optional[str]=None,
        model_keep_alive: Optional[str]=None,
        temperature: Optional[float]=None, 
        max_tokens: Optional[int]=None,
        context_window: Optional[int]=None, # applicable to ollama only
        batch_size: Optional[int]=None, # applicable to ollama only
        prefill: Optional[str]=None,
        stop: Optional[list]=None,
        api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
        api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        **kwargs,
    ) -> dict:
        completion = OllamaAI.getChatCompletion(
            messages,
            model=model,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
            batch_size=batch_size,
            prefill=prefill,
            stop=stop,
            api_key=api_key,
            api_endpoint=api_endpoint,
            model_keep_alive=model_keep_alive,
            **kwargs
        )
        jsonOutput = completion.message.content
        jsonOutput = re.sub("^[^{]*?({.*?})[^}]*?$", r"\1", jsonOutput)
        return json.loads(jsonOutput)

    @staticmethod
    def downloadModel(model: str, force: bool=False) -> bool:
        if not ":" in model:
            model = f"{model}:latest"
        if force or not model in [i.model for i in OllamaAI.getClient().list().models]:
            print(f"Downloading model '{model}' ...")
            try:
                #https://github.com/ollama/ollama-python/blob/main/examples/pull-progress/main.py
                current_digest, bars = '', {}
                for progress in OllamaAI.getClient().pull(model, stream=True):
                    digest = progress.get('digest', '')
                    if digest != current_digest and current_digest in bars:
                        bars[current_digest].close()

                    if not digest:
                        print(progress.get('status'))
                        continue

                    if digest not in bars and (total := progress.get('total')):
                        bars[digest] = tqdm(total=total, desc=f'pulling {digest[7:19]}', unit='B', unit_scale=True)

                    if completed := progress.get('completed'):
                        bars[digest].update(completed - bars[digest].n)

                    current_digest = digest
            except ResponseError as e:
                print('Error:', e.error)
                return False
        return True