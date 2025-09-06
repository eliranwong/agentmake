"""
Extra bible references from the given content
"""

def extract_exhausitive_bible_references(
    content,
    **kwargs,
):
    from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
    refs = BibleVerseParser(False).extractExhaustiveReferencesReadable(content)
    refs if refs else "[not found]"
    text_output = f"```references\n{refs}\n```"

    print_on_terminal = kwargs.get("print_on_terminal")
    if print_on_terminal:
        print(text_output)

    return text_output

CONTENT_PLUGIN = extract_exhausitive_bible_references