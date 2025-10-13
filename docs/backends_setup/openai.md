# Backend Setup - OpenAI

1. Create an OpenAI API key at: https://platform.openai.com/

2. Run `ai -ec`

3. Fill in the value of `OPENAI_API_KEY` like this:

> OPENAI_API_KEY=xxxxxxxxxxxxxxxxxx

4. Optionally, you can set the default backend to `openai`:

> DEFAULT_AI_BACKEND=openai

5. Use backend `openai` without setting it as default:

> agentmake -b openai
