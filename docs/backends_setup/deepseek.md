# Backend Setup - DeepSeek

1. Create an DeepSeek API key at: https://platform.deepseek.com/sign_in

2. Run `ai -ec`

3. Fill in the value of `DEEPSEEK_API_KEY` like this:

> DEEPSEEK_API_KEY=xxxxxxxxxxxxxxxxxx

4. Optionally, you can set the default backend to `deepseek`:

> DEFAULT_AI_BACKEND=deepseek

5. Use backend `deepseek` without setting it as default:

> agentmake -b deepseek
