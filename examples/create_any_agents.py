from agentmake import agentmake

print("""# Example: Create any agents based on your request\n""")

user_request = input("Enter your request: ")
while user_request:
    agentmake(user_request, system="create_agent")
    user_request = input("Enter your request: ")