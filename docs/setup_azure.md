# Use Models Deployed via Azure Service

Agentmake supports both OpenAI and non-OpenAI models, deployed with Azure service.  

To use them with AgentMake:

* specify `azure` as backend to use Azure OpenAI models

* specify `azure_any` as backend to use Azure non-OpenAI models

To set up or deploy models with Azure, go to https://ai.azure.com/github.

Go to `Deployment` to check for model names.

<img width="1288" height="913" alt="Image" src="https://github.com/user-attachments/assets/cccfbe68-5c94-42da-bff2-f08fa5ddfc72" />

# Use OpenAI Models with AgentMake

Go to `Overview` -> `Azure OpenAI`, copy Azure OpenAI endpoint and API key.

<img width="1270" height="917" alt="Image" src="https://github.com/user-attachments/assets/4b22fb39-da7a-4783-9b52-4812bdb9a7c2" />

To configure, run:

> ai -ec

For example, add or edit:

```
AZURE_OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AZURE_OPENAI_API_ENDPOINT=https://xxxxxxxxxxxx.openai.azure.com/
AZURE_OPENAI_MODEL=gpt-4.1
AZURE_OPENAI_TEMPERATURE=0.3
AZURE_OPENAI_MAX_TOKENS=16384
```

# Use Non-OpenAI Models with AgentMake

Go to `Overview` -> `Azure AI Inference`, copy Azure AI model inference endpoint and API key.

<img width="1271" height="917" alt="Image" src="https://github.com/user-attachments/assets/551d42d8-68b7-44c3-aa09-330e31ba4f7e" />

To configure, run:

> ai -ec

For example, add or edit:

```
AZURE_ANY_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AZURE_ANY_API_ENDPOINT=https://xxxxxxxxxxxx.services.ai.azure.com/models
AZURE_ANY_MODEL=grok-3
AZURE_ANY_TEMPERATURE=0.3
AZURE_ANY_MAX_TOKENS=16384
```
