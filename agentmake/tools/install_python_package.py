def install_python_package(python_package_name: str, **kwargs):
    from agentmake.utils.manage_package import installPipPackage
    
    if python_package_name:
        install = installPipPackage(f"--upgrade {python_package_name}")
        return "Installed!" if install else f"Failed to install '{python_package_name}'!"
    return ""

# Function Signature
TOOL_SCHEMA = {
    "name": "install_python_package",
    "description": f'''Install a python package''',
    "parameters": {
        "type": "object",
        "properties": {
            "python_package_name": {
                "type": "string",
                "description": "Python package name",
            },
        },
        "required": ["python_package_name"],
    },
}

TOOL_FUNCTION = install_python_package