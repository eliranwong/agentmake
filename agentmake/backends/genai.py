try:
    from google.genai.types import Content, GenerateContentConfig, SafetySetting, Tool, Part, HttpOptions
    from google.genai import Client
except:
    # Google GenAI SDK is not supported on Android Termux
    pass
from agentmake import config, GoogleaiAI
from typing import Optional, Any
import os, traceback

DEVELOPER_MODE = True if os.getenv("DEVELOPER_MODE") and os.getenv("DEVELOPER_MODE").upper() == "TRUE" else False


class GenaiAI:

    AGENTMAKE_USER_DIR = os.getenv("AGENTMAKE_USER_DIR") if os.getenv("AGENTMAKE_USER_DIR") else os.path.join(os.path.expanduser("~"), "agentmake")

    # set environment variable `GOOGLE_APPLICATION_CREDENTIALS`
    if os.getenv("VERTEXAI_API_KEY") and os.path.isfile(os.path.expanduser(os.getenv("VERTEXAI_API_KEY"))):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.expanduser(os.getenv("VERTEXAI_API_KEY"))
    elif os.path.isfile(os.path.join(AGENTMAKE_USER_DIR, "google_application_credentials.json")):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(AGENTMAKE_USER_DIR, "google_application_credentials.json")
    elif not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

    # set default key; make it a list to support rotation of multiple API keys
    if os.getenv("VERTEXAI_API_KEY") and not os.path.isfile(os.getenv("VERTEXAI_API_KEY")):
        DEFAULT_API_KEY = os.getenv("VERTEXAI_API_KEY").split(",")
    elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        DEFAULT_API_KEY = [os.getenv("GOOGLE_APPLICATION_CREDENTIALS")]
    else:
        DEFAULT_API_KEY = GoogleaiAI.DEFAULT_API_KEY

    DEFAULT_API_PROJECT_ID = os.getenv("VERTEXAI_API_PROJECT_ID")
    DEFAULT_API_SERVICE_LOCATION = os.getenv("VERTEXAI_API_SERVICE_LOCATION") if os.getenv("VERTEXAI_API_SERVICE_LOCATION") else "us-central1"
    DEFAULT_MODEL = os.getenv("VERTEXAI_MODEL") if os.getenv("VERTEXAI_MODEL") else "gemini-2.5-pro"
    DEFAULT_TEMPERATURE = float(os.getenv("VERTEXAI_TEMPERATURE")) if os.getenv("VERTEXAI_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("VERTEXAI_MAX_TOKENS")) if os.getenv("VERTEXAI_MAX_TOKENS") else 65536 # https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models

    @staticmethod
    def toGenAIMessages(messages: dict=[]) -> Optional[list]:
        system_message = ""
        last_user_message = ""
        if messages:
            history = []
            for i in messages:
                role = i.get("role", "")
                content = i.get("content", "")
                if role in ("user", "assistant"):
                    history.append(Content(role="user" if role == "user" else "model", parts=[Part.from_text(text=content)]))
                    if role == "user":
                        last_user_message = content
                elif role == "system":
                    system_message = content
            # remove the last user message
            if history and history[-1].role == "user":
                history = history[:-1]
            else:
                last_user_message = ""
            if not history:
                history = None
        else:
            history = None
        return history, system_message, last_user_message

    @staticmethod
    def getApiKey():
        # rotate multiple API keys
        if len(GenaiAI.DEFAULT_API_KEY) > 1:
            first_item = GenaiAI.DEFAULT_API_KEY.pop(0)
            GenaiAI.DEFAULT_API_KEY.append(first_item)
        return GenaiAI.DEFAULT_API_KEY[0]

    @staticmethod
    def getClient(api_key: Optional[str]=None, api_project_id: Optional[str]=None, api_service_location: Optional[str]=None):
        # create GenAI client
        api_project_id = api_project_id if api_project_id else GenaiAI.DEFAULT_API_PROJECT_ID
        api_service_location = api_service_location if api_service_location else GenaiAI.DEFAULT_API_SERVICE_LOCATION
        api_key = api_key if api_key else GenaiAI.getApiKey()
        if os.path.isfile(os.path.expanduser(api_key)):
            api_key = os.path.expanduser(api_key)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = api_key
        config.genai_client = Client(vertexai=True, project=api_project_id, location=api_service_location) if os.path.isfile(api_key) and api_project_id and api_service_location else Client(api_key=api_key)
        return config.genai_client

    @staticmethod
    def getConfig(
        system_message: Optional[str]=None,
        schema: Optional[dict]=None,
        temperature: Optional[float]=None,
        max_tokens: Optional[int]=None,
        stop: Optional[list]=None,
        api_timeout: Optional[int]=None,
        tools: Optional[list]=None,
    ):
        if not system_message:
            system_message = os.getenv("DEFAULT_SYSTEM_MESSAGE") if os.getenv("DEFAULT_SYSTEM_MESSAGE") else "You are an AI assistant."
        genai_config = GenerateContentConfig(
            http_options=HttpOptions(timeout=api_timeout),
            system_instruction=system_message+"""\n\n# Output Format\nOutputs in JSON.""" if schema else system_message,
            temperature=temperature if temperature is not None else GenaiAI.DEFAULT_TEMPERATURE,
            #top_p=0.95,
            #top_k=20,
            candidate_count=1,
            #seed=5,
            max_output_tokens=max_tokens if max_tokens else GenaiAI.DEFAULT_MAX_TOKENS,
            stop_sequences=stop if stop else ["STOP!"],
            #presence_penalty=0.0,
            #frequency_penalty=0.0,
            safety_settings= [
                SafetySetting(
                    category='HARM_CATEGORY_CIVIC_INTEGRITY',
                    threshold='BLOCK_ONLY_HIGH',
                ),
                SafetySetting(
                    category='HARM_CATEGORY_DANGEROUS_CONTENT',
                    threshold='BLOCK_ONLY_HIGH',
                ),
                SafetySetting(
                    category='HARM_CATEGORY_HATE_SPEECH',
                    threshold='BLOCK_ONLY_HIGH',
                ),
                SafetySetting(
                    category='HARM_CATEGORY_HARASSMENT',
                    threshold='BLOCK_ONLY_HIGH',
                ),
                SafetySetting(
                    category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                    threshold='BLOCK_ONLY_HIGH',
                ),
            ],
            tools=tools,
        )
        return genai_config

    @staticmethod
    def getChatCompletion(
        messages: list,
        model: Optional[str]=None,
        schema: Optional[dict]=None,
        temperature: Optional[float]=None,
        max_tokens: Optional[int]=None,
        #context_window: Optional[int]=None, # applicable to ollama only
        #batch_size: Optional[int]=None, # applicable to ollama only
        #prefill: Optional[str]=None,
        stop: Optional[list]=None,
        stream: Optional[bool]=False,
        api_key: Optional[str]=None, # enter credentials json file path if using Vertex AI; or enter Google AI API key for accessing Google AI services
        #api_endpoint: Optional[str]=None,
        api_project_id: Optional[str]=None, # applicable to Vertex AI only
        api_service_location: Optional[str]=None, # applicable to Vertex AI only
        api_timeout: Optional[int]=None,
        **kwargs,
    ) -> Any:
        if not api_key and not GenaiAI.DEFAULT_API_KEY:
            raise ValueError("VertexAI credential json file path or GoogleAI API key is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        # convert messages to GenAI format
        history, system_message, last_user_message = GenaiAI.toGenAIMessages(messages=messages)
        # format GenAI tool
        if schema:
            name, description, parameters = schema["name"], schema["description"], schema["parameters"]
            if "type" in parameters:
                parameters["type"] = parameters["type"].upper() # Input should be 'TYPE_UNSPECIFIED', 'STRING', 'NUMBER', 'INTEGER', 'BOOLEAN', 'ARRAY' or 'OBJECT' [type=literal_error, input_value='object', input_type=str]
            for key, value in parameters["properties"].items():
                if "type" in value:
                    parameters["properties"][key]["type"] = parameters["properties"][key]["type"].upper() # Input should be 'TYPE_UNSPECIFIED', 'STRING', 'NUMBER', 'INTEGER', 'BOOLEAN', 'ARRAY' or 'OBJECT' [type=literal_error, input_value='object', input_type=str]
            # declare a function
            function_declaration = dict(
                name=name,
                description=description,
                parameters=parameters,
            )
            tool = Tool(
                function_declarations=[function_declaration],
            )
            tools = [tool]
        else:
            tools = None
        # generate content
        genai_config = GenaiAI.getConfig(
            system_message=system_message,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_timeout=api_timeout,
            tools=tools,
        )
        # run completion
        completion = None
        used_api_keys = []
        while completion is None:
            this_api_key = api_key if api_key else GenaiAI.getApiKey()
            if this_api_key in used_api_keys:
                break
            else:
                used_api_keys.append(this_api_key)
            try:
                genai_chat = GenaiAI.getClient(api_key=this_api_key, api_project_id=api_project_id, api_service_location=api_service_location).chats.create(
                    model=model if model else GenaiAI.DEFAULT_MODEL,
                    config=genai_config,
                    history=history,
                    **kwargs
                )
                completion = genai_chat.send_message_stream(last_user_message) if stream else genai_chat.send_message(last_user_message)
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
        temperature: Optional[float]=None, 
        max_tokens: Optional[int]=None,
        #context_window: Optional[int]=None, # applicable to ollama only
        #batch_size: Optional[int]=None, # applicable to ollama only
        #prefill: Optional[str]=None,
        stop: Optional[list]=None,
        api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
        #api_endpoint: Optional[str]=None,
        api_project_id: Optional[str]=None, # applicable to Vertex AI only
        api_service_location: Optional[str]=None, # applicable to Vertex AI only
        api_timeout: Optional[int]=None,
        **kwargs,
    ) -> dict:
        completion = GenaiAI.getChatCompletion(
            messages,
            model=model,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
            #prefill=prefill,
            stop=stop,
            api_key=api_key,
            #api_endpoint=api_endpoint,
            api_project_id=api_project_id,
            api_service_location=api_service_location,
            api_timeout=api_timeout,
            **kwargs
        )
        part = completion.candidates[0].content.parts[0]
        textOutput = part.function_call.args if part.function_call else part.text
        if isinstance(textOutput, str) and textOutput and textOutput.startswith("```json\n"):
            textOutput = textOutput[8:-4]
        return "" if textOutput is None else textOutput

class VertexaiAI:

    @staticmethod
    def getChatCompletion(
            messages: list,
            model: Optional[str]=None,
            schema: Optional[dict]=None,
            temperature: Optional[float]=None,
            max_tokens: Optional[int]=None,
            #context_window: Optional[int]=None, # applicable to ollama only
            #batch_size: Optional[int]=None, # applicable to ollama only
            #prefill: Optional[str]=None,
            stop: Optional[list]=None,
            stream: Optional[bool]=False,
            api_key: Optional[str]=None, # enter credentials json file path if using Vertex AI; or enter Google AI API key for accessing Google AI services
            #api_endpoint: Optional[str]=None,
            api_project_id: Optional[str]=None, # applicable to Vertex AI only
            api_service_location: Optional[str]=None, # applicable to Vertex AI only
            **kwargs,
    ) -> Any:
        return GenaiAI.getChatCompletion(
            messages,
            model=model,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            stream=stream,
            api_key=api_key,
            api_project_id=api_project_id,
            api_service_location=api_service_location,
            **kwargs
        )

    @staticmethod
    def getDictionaryOutput(
            messages: list,
            schema: dict,
            model: Optional[str]=None,
            temperature: Optional[float]=None, 
            max_tokens: Optional[int]=None,
            #context_window: Optional[int]=None, # applicable to ollama only
            #batch_size: Optional[int]=None, # applicable to ollama only
            #prefill: Optional[str]=None,
            stop: Optional[list]=None,
            api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
            #api_endpoint: Optional[str]=None,
            api_project_id: Optional[str]=None, # applicable to Vertex AI only
            api_service_location: Optional[str]=None, # applicable to Vertex AI only
            **kwargs,
    ) -> dict:
        return GenaiAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_key=api_key,
            api_project_id=api_project_id,
            api_service_location=api_service_location,
            **kwargs
        )
