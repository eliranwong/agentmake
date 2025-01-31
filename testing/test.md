
> messages = generate("What is the most effective method for training AI models?", backend="openai")

> messages = generate(messages, backend="googleai", follow_up_prompt="Can you give me some different options?")

> messages = generate(messages, backend="xai", follow_up_prompt="What are the limitations or potential biases in this information?")

> generate(messages, backend="mistral", follow_up_prompt="Please provide a summary of the discussion so far.")


As you may see, the `generate` function returns the `messages` list, which is passed to the next `generate` function in turns.

Therefore, it is very simple to create a chatbot application, you can do it as few as five lines or less, e.g.:


> messages = [{"role": "system", "content": "You are an AI assistant."}]

> user_input = "Hello!"

> while user_input:

>     messages = generate(messages, follow_up_prompt=user_input, stream=True)

>     user_input = input("Enter your query:\n(enter a blank entry to exit)\n>>> ")


####################


```
messages = generate("What is the most effective method for training AI models?", backend="openai")
messages = generate(messages, backend="googleai", follow_up_prompt="Can you give me some different options?")
messages = generate(messages, backend="xai", follow_up_prompt="What are the limitations or potential biases in this information?")
generate(messages, backend="mistral", follow_up_prompt="Please provide a summary of the discussion so far.")
```

As you may see, the `generate` function returns the `messages` list, which is passed to the next `generate` function in turns.

Therefore, it is very simple to create a chatbot application, you can do it as few as five lines or less, e.g.:

```
messages = [{"role": "system", "content": "You are an AI assistant."}]
user_input = "Hello!"
while user_input:
    messages = generate(messages, follow_up_prompt=user_input, stream=True)
    user_input = input("Enter your query:\n(enter a blank entry to exit)\n>>> ")
```