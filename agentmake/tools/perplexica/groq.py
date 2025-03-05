def perplexica_groq(messages, **kwargs):

    import requests, json, os

    from agentmake import GroqAI
    from agentmake.utils.online import get_local_ip
    PERPLEXICA_HOST = os.getenv("PERPLEXICA_HOST") if os.getenv("PERPLEXICA_HOST") else f"http://{get_local_ip()}"
    #PERPLEXICA_FRONTEND_PORT = int(os.getenv("PERPLEXICA_FRONTEND_PORT")) if os.getenv("PERPLEXICA_FRONTEND_PORT") else 3000
    PERPLEXICA_BACKEND_PORT = int(os.getenv("PERPLEXICA_BACKEND_PORT")) if os.getenv("PERPLEXICA_BACKEND_PORT") else 3001
    PERPLEXICA_LOCAL_EMBEDDING = os.getenv("PERPLEXICA_LOCAL_EMBEDDING") if os.getenv("PERPLEXICA_LOCAL_EMBEDDING") else "xenova-bge-small-en-v1.5"
    PERPLEXICA_OPTIMIZATION_MODE = os.getenv("PERPLEXICA_OPTIMIZATION_MODE") if os.getenv("PERPLEXICA_OPTIMIZATION_MODE") else "speed"
    PERPLEXICA_FOCUS_MODE = os.getenv("PERPLEXICA_FOCUS_MODE") if os.getenv("PERPLEXICA_FOCUS_MODE") else "webSearch"

    query = messages[-1].get("content", "")
    if not query:
        return None

    history = []
    for i in messages[:-1]:
        role = i.get("role", "")
        if role == "assistant":
            history.append(i)
        elif role == "user":
            i["role"] = "human"
            history.append(i)

    api_url = f"{PERPLEXICA_HOST}:{PERPLEXICA_BACKEND_PORT}/api/search" 
    headers = {"Content-Type": "application/json"}
    # references:
    # https://github.com/ItzCrazyKns/Perplexica/blob/master/docs/API/SEARCH.md
    # https://github.com/ItzCrazyKns/Perplexica/tree/master/src/lib/providers

    data = {
        "chatModel": {
            "provider": "custom_openai",
            "model": GroqAI.DEFAULT_MODEL,
            "customOpenAIBaseURL": "https://api.groq.com/openai/v1",
            "customOpenAIKey": GroqAI.getApiKey(),
        },
        "embeddingModel": {
            "provider": "local",
            "model": PERPLEXICA_LOCAL_EMBEDDING,
        },
        "optimizationMode": PERPLEXICA_OPTIMIZATION_MODE,
        "focusMode": PERPLEXICA_FOCUS_MODE,
        "query": query,
        "history": history,
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for bad status codes

        response_json = response.json()
        #print(response_json) 

        answer = response_json["message"]
        sources = response_json["sources"]
        
        print("```answer")
        print(answer)
        print("```\n\n```sources")

        for index, i in enumerate(sources):
            if "metadata" in i:
                title = i["metadata"].get("title", "")
                url = i["metadata"].get("url", "")
                if title and url:
                    source = f"{(index + 1)}. [{title}]({url})"
                    print(source)
        print("```")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
    except KeyError as e:
        print(f"Missing key in response: {e}")
    
    return ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Get research result via Perplexica using Groq API"""

TOOL_FUNCTION = perplexica_groq
