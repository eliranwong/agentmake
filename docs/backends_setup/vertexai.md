# Backend Setup - Google Vertex AI

# Set up your Google Cloud Platform project

1. Go to https://console.cloud.google.com/

![new_project](https://github.com/eliranwong/letmedoit/assets/25262722/e3c3a5f0-9155-414b-816a-b10bf7cfa839)

2. Either "Select a project" or create "NEW PROJECT", enter, e.g.:

Project name: agentmake

![project_name](https://github.com/eliranwong/ToolMate/assets/25262722/c9d99cf2-1e2f-410a-966e-cb62e3bd2867)

3. Set up billing information

MENU > Billing > Payment method

4. Set up service account

MENU > MORE PRODUCTS > IAM & ADMIN > Service Accounts

![menu_service_account](https://github.com/eliranwong/ToolMate/assets/25262722/2ad81bb0-53c0-4958-b44c-20b00ab161a9)

Create service account, e.g.:

* Service account name: agentmake

* Service account ID: agentmake

* Service account description: agentmake

Click "CREATE AND CONTINUE"

![create_service_account_button](https://github.com/eliranwong/letmedoit/assets/25262722/47a3647f-ad36-4c1e-acae-9d40127e6379)

![service_account_details](https://github.com/eliranwong/letmedoit/assets/25262722/5445d6e9-c609-4dd9-93c3-e9ce9d6efe73)

* Select role > Owner > CONTINUE > DONE

![role_owner](https://github.com/eliranwong/letmedoit/assets/25262722/1cb0db0d-9971-4ae4-994b-011708cd62e9)

5. Download API key in JSON format

Right next to the created service account, select the 3-dot action button > Manage keys

![manage_keys](https://github.com/eliranwong/letmedoit/assets/25262722/73d32cc9-8fc0-4f2f-93bd-fa1acb42060a)

ADD KEY > Create new key

![create_new_key](https://github.com/eliranwong/letmedoit/assets/25262722/5ac459ad-6df1-4bb3-b2fc-88566fe73a53)

Select JSON format and automatically download the file

![json_format](https://github.com/eliranwong/letmedoit/assets/25262722/5fdf3d03-e263-45d6-8526-44c454450060)

# Enable APIs in Google Console

## Gemini Pro

1. Go to https://console.cloud.google.com/vertex-ai

2. Click "ENABLE ALL RECOMMENDATED APIS"

3. Copy the JSON file, downloaded in the previous step, to directory "\~/agentmake/" and rename it as "credentials_google_cloud.json"

![gemini_pro_api](https://github.com/eliranwong/letmedoit/assets/25262722/78b2f78c-2823-45ad-9645-d924c07e4ef7)

![service_enabled](https://github.com/eliranwong/letmedoit/assets/25262722/eb9e9fa7-873c-48b8-8249-dce9a9812b31)

Remarks:

* The "~" in the copied path denotes user home directory

# Use Vertex AI in AgentMake AI

1. To use Vertex AI with library `google-genai`, you need to install with running:

> pip install --upgrade "agentmake[genai]"

2. Run `ai -ec`

3. Fill in the value of `VERTEXAI_API_KEY` like this:

> VERTEXAI_API_KEY=~/agentmake/credentials_google_cloud.json

4. Optionally, you can set the default backend to `vertexai`:

> DEFAULT_AI_BACKEND=vertexai

5. Use backend `vertexai` without setting it as default:

> agentmake -b vertexai