try:
    from opencc import OpenCC
except:
    from agentmake.utils.manage_package import installPipPackage
    installPipPackage(f"--upgrade opencc-python-reimplemented")
    from opencc import OpenCC

def convert_simplified_chinese(content, **kwargs):
    try:
        return OpenCC('s2t').convert(content)
    except:
        return content

CONTENT_PLUGIN = convert_simplified_chinese