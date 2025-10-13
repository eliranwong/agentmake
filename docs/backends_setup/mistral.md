# Backend Setup - Mistral AI

Mistral AI API Key allows you to have FREE access to [selected open source LLMs](https://docs.mistral.ai/getting-started/models/models_overview/).

At the time of writing, Mistral AI offers API keys for both FREE and paid tier users.

Even FREE tier users can use Mistral Large models

![mistral_large](https://github.com/user-attachments/assets/8f262ec0-511d-461f-a094-e634f3004fc1)

# Generate Mistral API Key

![api_setup](https://github.com/user-attachments/assets/a93d6875-dbe8-44d6-84d4-6f924e6d54aa)

1. Go to https://console.mistral.ai/api-keys/

2. Log in with a registered account (Note that each free plan requires a phone number to verify.)

3. Click menu item "API Keys" on the left

4. Click button "Create new Key"

5. Enter a name, for example, "agentmake"

6. Copy or make a note of the created API key

# Use Mistral AI as Backend in AgentMake AI

1. Run `ai -ec`

2. Fill in the value of `MISTRAL_API_KEY` like this:

> MISTRAL_API_KEY=xxxxxxxxxxxxxxxxxx

3. Optionally, you can set the default backend to `mistral`:

> DEFAULT_AI_BACKEND=mistral

4. Use backend `mistral` without setting it as default:

> agentmake -b mistral
