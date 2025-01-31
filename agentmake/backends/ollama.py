from ..utils.online import get_local_ip
from ..utils.schema import getParameterSchema
from typing import Optional
from tqdm import tqdm
from ollama import Client, Options
from ollama._types import ChatResponse
from ollama import pull
from ollama import list as ollama_ls
import ollama
import re, json

class OllamaLLM:

    DEFAULT_ENDPOINT = f"http://{get_local_ip()}:11434"
    DEFAULT_MODEL = "llama3.2"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = -1
    DEFAULT_CONTEXT_WINDOW = 2048
    DEFAULT_BATCH_SIZE = 512
    DEFAULT_KEEP_ALIVE = "5m"

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
            #api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
            api_endpoint: Optional[str]=None,
            #api_project_id: Optional[str]=None, # applicable to Vertex AI only
            #api_service_location: Optional[str]=None, # applicable to Vertex AI only
            **kwargs,
    ) -> ChatResponse:
        if prefill:
            messages.append({'role': 'assistant', 'content': prefill})
        model = model if model else OllamaLLM.DEFAULT_MODEL
        # download model if it is not in the model list
        OllamaLLM.downloadModel(model)
        return Client(host=api_endpoint if api_endpoint else OllamaLLM.DEFAULT_ENDPOINT).chat(
            keep_alive=model_keep_alive if model_keep_alive else OllamaLLM.DEFAULT_KEEP_ALIVE,
            model=model,
            messages=messages,
            format=getParameterSchema(schema) if schema else None,
            stream=stream,
            options=Options(
                temperature=temperature if temperature is not None else OllamaLLM.DEFAULT_TEMPERATURE,
                num_ctx=context_window if context_window is not None else OllamaLLM.DEFAULT_CONTEXT_WINDOW,
                num_batch=batch_size if batch_size is not None else OllamaLLM.DEFAULT_BATCH_SIZE,
                num_predict=max_tokens if max_tokens else OllamaLLM.DEFAULT_MAX_TOKENS,
                stop=stop,
                **kwargs,
            ),
        )

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
            #api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
            api_endpoint: Optional[str]=None,
            #api_project_id: Optional[str]=None, # applicable to Vertex AI only
            #api_service_location: Optional[str]=None, # applicable to Vertex AI only
            **kwargs,
    ) -> dict:
        completion = OllamaLLM.getChatCompletion(
            messages,
            model=model,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
            batch_size=batch_size,
            prefill=prefill,
            stop=stop,
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
        if force or not model in [i.model for i in ollama_ls().models]:
            print(f"Downloading model '{model}' ...")
            try:
                #https://github.com/ollama/ollama-python/blob/main/examples/pull-progress/main.py
                current_digest, bars = '', {}
                for progress in pull(model, stream=True):
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
            except ollama.ResponseError as e:
                print('Error:', e.error)
                return False
        return True