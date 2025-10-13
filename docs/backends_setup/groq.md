# Backend Setup - Groq Cloud API Key

Groq Cloud API Key allows you to have FREE access to [selected open source LLMs](https://console.groq.com/docs/models).

At the time of writing, use of Groq Cloud API is FREE.

# Generate Groq API Key

1. Go to https://console.groq.com/keys

2. Log in with a registered account

3. Click menu item "API Keys" on the left

4. Click button "Create API Key"

5. Enter a name, for example, "agentmake"

6. Copy or make a note of the created API key

![groq_api_key](https://github.com/eliranwong/toolmate/assets/25262722/d479ad5f-40b5-4d9b-a766-83db023ead1c)

# Use Groq API Key in AgentMake AI

1. Run `ai -ec`

2. Fill in the value of `GROQ_API_KEY` like this:

> GROQ_API_KEY=xxxxxxxxxxxxxxxxxx

Use `,` as separator to support multiple API keys rotation, e.g.:

> GROQ_API_KEY=xxxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxx,xxxxxxxxxxxxxxxxxx

3. Optionally, you can set the default backend to `groq`:

> DEFAULT_AI_BACKEND=groq

4. Use backend `groq` without setting it as default:

> agentmake -b groq
