def getRagPrompt(query: str, context: str) -> str:
    return context if not query else f"""# Provided Context

{context}

# My question:

{query}

# Instruction

Select all the relevant information from the provided context to answer my question in as much detail as possible."""