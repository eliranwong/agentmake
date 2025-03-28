from agentmake import agentmake
messages = [{"role": "system", "content": "You are an AI assistant."}]

import mesop as me
import mesop.labs as mel


def on_load(e: me.LoadEvent):
  me.set_theme_mode("system")


@me.page(
  security_policy=me.SecurityPolicy(
    allowed_iframe_parents=["https://mesop-dev.github.io"]
  ),
  title="AgentMake AI",
  on_load=on_load,
)
def page():
  mel.chat(transform, title="AgentMake AI", bot_user="AgentMake AI")


def transform(input: str, history: list[mel.ChatMessage]):
    global messages
    messages = agentmake(messages, follow_up_prompt=input)
    yield messages[-1].get("content", "")

