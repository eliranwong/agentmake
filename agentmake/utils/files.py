from agentmake import USER_OS
import glob
import os, re

def searchFolder(folder, query, filter="*.txt"):
    # Linux/macOS: find chats/ -name "*.txt" -type f -exec grep -rin --color=auto "your_string" {} +
    # Windows: findstr /s "your_string" *.txt /path/to/your/folder
    if USER_OS == "Windows":
        cli = '''findstr /s "{2}" "{1}" "{0}"'''.format(folder, filter, query)
    else:
        cli = '''find "{0}" -iname "{1}" -type f -exec grep -Erin --color=auto "{2}" {3}{4} +'''.format(folder, filter, query, "{", "}")
    os.system(cli)

def find_last_added_file(folder_path, ext=".mp3"):
    """
    Finds the filename of the last added .mp3 file in a folder.
    Args:
        folder_path: The path to the folder containing the MP3 files.
    Returns:
        The filename of the last added .mp3 file, or None if no such file is found.
    """
    files = glob.glob(os.path.join(folder_path, f'*{ext}'))
    if not files:
        return None

    # Sort files by creation time (oldest to newest)
    files.sort(key=os.path.getctime)
    return os.path.basename(files[-1])

def getFileSizeInMB(file_path):
    # Get the file size in bytes
    file_size = os.path.getsize(file_path)
    # Convert bytes to megabytes
    return file_size / (1024 * 1024)

def isExistingPath(docs_path):
    # handle document path dragged to the terminal
    docs_path = docs_path.strip()
    search_replace = (
        ("^'(.*?)'$", r"\1"),
        ('^(File|Folder): "(.*?)"$', r"\2"),
    )
    for search, replace in search_replace:
        docs_path = re.sub(search, replace, docs_path)
    if "\\ " in docs_path or r"\(" in docs_path:
        search_replace = (
            ("\\ ", " "),
            (r"\(", "("),
        )
        for search, replace in search_replace:
            docs_path = docs_path.replace(search, replace)
    return docs_path if os.path.exists(os.path.expanduser(docs_path)) else ""

def getUnstructuredFiles(dir_path: str) -> list:
    full_paths = []
    for dirpath, _, files in os.walk(dir_path):
        for filename in files:
            _, file_extension = os.path.splitext(filename)
            if file_extension[1:] in TEXT_FORMATS:
                filepath = os.path.join(dirpath, filename)
                full_paths.append(filepath)
    return full_paths

def getFilenamesWithoutExtension(dir, ext):
    # Note: pathlib.Path(file).stem does not work with file name containg more than one dot, e.g. "*.db.sqlite"
    #files = glob.glob(os.path.join(dir, "*.{0}".format(ext)))
    #return sorted([file[len(dir)+1:-(len(ext)+1)] for file in files if os.path.isfile(file)])
    return sorted([f[:-(len(ext)+1)] for f in os.listdir(dir) if f.lower().endswith(f".{ext}") and os.path.isfile(os.path.join(dir, f))])
