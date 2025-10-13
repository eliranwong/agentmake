# Backend Setup - Anthropic

1. Register an Anthropic API key at https://www.anthropic.com/api

2. Run `ai -ec`

3. Fill in the value of `ANTHROPIC_API_KEY` like this:

> ANTHROPIC_API_KEY=xxxxxxxxxxxxxxxxxx

4. Optionally, you can set the default backend to `anthropic`:

> DEFAULT_AI_BACKEND=anthropic

5. Use backend `anthropic` without setting it as default:

> agentmake -b anthropic