"""
Convert Traditional Chinese characters into Simplified Chinese characters
"""

try:
    from opencc import OpenCC
except:
    from agentmake.utils.manage_package import installPipPackage
    installPipPackage(f"--upgrade opencc-python-reimplemented")
    from opencc import OpenCC

def convert_traditional_chinese(content, **kwargs):
    from opencc import OpenCC
    try:
        converted = OpenCC('t2s').convert(content)
        if kwargs.get("print_on_terminal"):
            print(f"```\n{converted}\n```")
        return converted
    except:
        return content

CONTENT_PLUGIN = convert_traditional_chinese