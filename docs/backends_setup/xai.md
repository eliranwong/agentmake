# Backend Setup - X AI

1. Create an X AI API key at: https://x.ai/api

2. Run `ai -ec`

3. Fill in the value of `XAI_API_KEY` like this:

> XAI_API_KEY=xxxxxxxxxxxxxxxxxx

4. Optionally, you can set the default backend to `xai`:

> DEFAULT_AI_BACKEND=xai

5. Use backend `xai` without setting it as default:

> agentmake -b xai
