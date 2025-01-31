try:
    from google.genai.types import Content, GenerateContentConfig, SafetySetting, Tool
    from google.genai import Client
except:
    # Google GenAI SDK is not supported on Android Termux
    pass
from typing import Optional, Any
import json, os


class GenaiLLM:

    DEFAULT_API_KEY = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    DEFAULT_API_PROJECT_ID = ""
    DEFAULT_API_SERVICE_LOCATION = "us-central1"
    DEFAULT_MODEL = "gemini-1.5-pro"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 8192 # https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models

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
                    history.append(Content(role="user" if role == "user" else "model", parts=[types.Part.from_text(content)]))
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
        if not api_key and not GenaiLLM.DEFAULT_API_KEY:
            raise ValueError("API key is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        # convert messages to GenAI format
        history, system_message, last_user_message = GenaiLLM.toGenAIMessages(messages=messages)
        # create GenAI client
        api_project_id = api_project_id if api_project_id else GenaiLLM.DEFAULT_API_PROJECT_ID
        api_service_location = api_service_location if api_service_location else GenaiLLM.DEFAULT_API_SERVICE_LOCATION
        api_key = api_key if api_key else GenaiLLM.DEFAULT_API_KEY
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = api_key if os.path.isfile(api_key) else ""
        genai_client = Client(vertexai=True, project=api_project_id, location=api_service_location) if os.path.isfile(api_key) and api_project_id and api_service_location else Client(api_key=api_key)
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
        genai_config = GenerateContentConfig(
            system_instruction=system_message,
            temperature=temperature if temperature is not None else GenaiLLM.DEFAULT_TEMPERATURE,
            #top_p=0.95,
            #top_k=20,
            candidate_count=1,
            #seed=5,
            max_output_tokens=max_tokens if max_tokens else GenaiLLM.DEFAULT_MAX_TOKENS,
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
        genai_chat = genai_client.chats.create(
            model=model if model else GenaiLLM.DEFAULT_MODEL,
            config=genai_config,
            history=history,
            **kwargs
        )
        return genai_chat.send_message_stream(last_user_message) if stream else genai_chat.send_message(last_user_message)

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
        completion = GenaiLLM.getChatCompletion(
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
            **kwargs
        )
        textOutput = completion.candidates[0].content.parts[0].text
        if textOutput and textOutput.startswith("```json\n"):
            textOutput = textOutput[8:-4]
        return json.loads(textOutput)

class VertexaiLLM:

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
        return GenaiLLM.getChatCompletion(
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
        return GenaiLLM.getDictionaryOutput(
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
