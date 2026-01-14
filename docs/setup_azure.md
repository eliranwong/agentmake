# Use Models Deployed via Azure Service

Agentmake supports both OpenAI and non-OpenAI models, deployed with Azure service.  

To use them with AgentMake:

* specify `azure_openai` as backend to use Azure OpenAI models

* specify `azure_deepseek` as backend to use Azure DeepSeek models

* specify `azure_mistral` as backend to use Azure Mistral models

* specify `azure_cohere` as backend to use Azure Cohere models

* specify `azure_xai` as backend to use Azure Xai models

* specify `azure_sdk` as backend to use Azure models with Azure AI SDK

* specify `custom` or `custom1` or `custom2` as backend to use other Azure openai-compatible models with OpenAI SDK

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
AZURE_SDK_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AZURE_SDK_API_ENDPOINT=https://xxxxxxxxxxxx.services.ai.azure.com/models
AZURE_SDK_MODEL=grok-3
AZURE_SDK_TEMPERATURE=0.3
AZURE_SDK_MAX_TOKENS=16384
```
