"""
Convert Simplified Chinese characters into Traditional Chinese characters
"""

try:
    from opencc import OpenCC
except:
    from agentmake.utils.manage_package import installPipPackage
    installPipPackage(f"--upgrade opencc-python-reimplemented")
    from opencc import OpenCC

def convert_simplified_chinese(content, **kwargs):
    from opencc import OpenCC
    try:
        converted = OpenCC('s2t').convert(content)
        if kwargs.get("print_on_terminal"):
            print(f"```\n{converted}\n```")
        return converted
    except:
        return content

CONTENT_PLUGIN = convert_simplified_chinese