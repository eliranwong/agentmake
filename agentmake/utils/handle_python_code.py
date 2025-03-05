import textwrap, re

def fineTunePythonCode(code):
    # dedent
    code = textwrap.dedent(code).rstrip()
    code = re.sub("^python[ ]*\n", "", code)
    # extract from code block, if any
    if code_only := re.search('```python\n(.+?)```', code, re.DOTALL):
        code = code_only.group(1).strip()
    # make sure it is run as main program
    if "\nif __name__ == '__main__':\n" in code:
        code, main = code.split("\nif __name__ == '__main__':\n", 1)
        code = code.strip()
        main = "\n" + textwrap.dedent(main)
    elif '\nif __name__ == "__main__":\n' in code:
        code, main = code.split('\nif __name__ == "__main__":\n', 1)
        code = code.strip()
        main = "\n" + textwrap.dedent(main)
    else:
        main = ""
    return f"{code}{main}"