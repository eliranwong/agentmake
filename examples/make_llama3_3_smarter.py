"""
## Example: Make AI Models Smarter in a Simple Way

This example demonstrate that you can make AI models smarter with use of a simple system message.

We ask the AI model `llama3.3:70b` to answer the same question `How many r are there in the word strawberry?`:

**Without system message**

> ai How many r are there in the word strawberry?

Result - `llama3.3:70b` gives a wrong answer below:

```output
There are 2 R's and also 2 other double letters in the word "strawberry" and "rr" is one of them, the other double letters are "ww".
```

**With system message**

> ai -sys "Think deeply about how to solve user requests with a systematic plan and strong reasoning in mind." How many r are there in the word strawberry?

Result - `llama3.3:70b` answers correctly with use of system message.

```output
To solve this, let's break down the word "strawberry" into its individual letters: 

s-t-r-a-w-b-e-r-r-y

Now, let's count the number of times the letter "r" appears: 

1. The first "r" is after the "t".
2. The second "r" is after the "e".
3. There is also another "r" after the second "r", making it the third "r" in total.

So, there are 3 "r"s in the word "strawberry" and then also another "r" before the last two "r"s, but since we've already counted the first "r", we actually have a total of 2 additional "r"s after the first one, but one of those is the second "r" and the other is the third "r". However, considering the word from the start and counting the "r"s, we have the first "r", then the second "r" and the third "r", which makes a total of 2 "r"s after the first "r" if we consider the sequence of the word and count the "r"s from the beginning.

However, the correct way to count is to simply look at the word and count the "r"s without overcomplicating it: 

There's an "r" after the "t", and two more "r"s after the "e". 

So, the correct count is 2 "r"s after the first "r" if counting from the first "r" onwards, but if counting from the start of the word, we simply see there are 3 "r"s in total because we count each "r" individually from the start of the word.

Therefore, there are 3 "r"s in "strawberry" if we count each "r" from the beginning of the word without overthinking the count.
```
"""

from agentmake import agentmake

question = "How many r are there in the word strawberry?"

print(f"""## Example: Make AI Models Smarter in a Simple Way

This example demonstrate that you can make AI models smarter with use of a simple system message.

We ask the AI model `llama3.3:70b` to answer the same question `{question}`""")

print("# The model `llama3.3:70b` gives incorrect answer by default:")

print(f"Question: {question}\n\nAnswer: ")

agentmake(question, backend="groq", model="llama-3.3-70b-versatile")

print("# With a simple system message `Think deeply about how to solve user requests with a systematic plan and strong reasoning in mind.`, the same model answers correctly:")

print(f"Question: {question}\n\nAnswer: ")

agentmake(question, backend="groq", model="llama-3.3-70b-versatile", system="Think deeply about how to solve user requests with a systematic plan and strong reasoning in mind.")