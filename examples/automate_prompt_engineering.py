from agentmake import agentmake

messages = [{"role": "system", "content": "You are an AI assistant."}]
user_input = "Hello!"
while user_input:
    messages = agentmake(messages, follow_up_prompt=user_input, system="auto", input_content_plugin="improve_prompt", stream=True)
    user_input = input("Enter your query:\n(enter a blank entry to exit)\n>>> ")