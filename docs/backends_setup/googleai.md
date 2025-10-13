# Backend Setup - Google AI Studio Gemini API

1. Create an X AI API key at: https://aistudio.google.com

2. Run `ai -ec`

3. Fill in the value of `GOOGLEAI_API_KEY` like this:

> GOOGLEAI_API_KEY=xxxxxxxxxxxxxxxxxx

Use `,` as separator to support multiple API keys rotation, e.g.:

> GOOGLEAI_API_KEY=xxxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxx

If you want to use Google GenAI libary `google-genai`, you also need to set `VERTEXAI_API_KEY` as follow:

> VERTEXAI_API_KEY=${GOOGLEAI_API_KEY}

4. Optionally, you can set the default backend to `googleai` or `genai`:

> DEFAULT_AI_BACKEND=googleai

or

> DEFAULT_AI_BACKEND=genai

Remarks: To use library `google-genai`, you need to install agentmake with running:

> pip install --upgrade "agentmake[genai]"

5. Use backend `googleai` or `genai` without setting it as default:

> agentmake -b googleai

or

> agentmake -b genai

## Note

* When you use backend `googleai`, AgentMake AI uses OpenAI-style API to interact with Gemini.
* When you use backend `genai`, AgentMake AI uses Google GenAI library to interact with Gemini.
* Not all devices or terminal app support library `google-genai`. For example, we haven't managed installing `google-genai` on Android Termux app.
