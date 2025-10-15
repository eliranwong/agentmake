import socket, webbrowser, shutil, re, requests, os, traceback, subprocess
from bs4 import BeautifulSoup
from urllib.parse import quote

def runSystemCommand(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout  # Captured standard output
    error = result.stderr  # Captured standard error
    response = ""
    response += f"# Output:\n{output}"
    if error.strip():
        response += f"\n# Error:\n{error}"
    return response

def showErrors(e=None, message=""):
    if message:
        trace = message
    else:
        trace = f"An error occurred: {e}" if e else "An error occurred!"
    print(trace)
    if os.getenv("DEVELOPER_MODE") and os.getenv("DEVELOPER_MODE").upper() == "TRUE":
        details = traceback.format_exc()
        trace += "\n"
        trace += details
        print("```error")
        print(details)
        print("```")
    return trace

def openURL(url):
    if shutil.which("termux-open-url"):
        command = f'''termux-open-url "{url}"'''
        runSystemCommand(command)
    else:
        webbrowser.open(url)

def get_wan_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        data = response.json()
        return data['ip']
    except:
        return ""

def get_local_ip():
    """
    Gets the local IP address of the machine.
    Returns:
        str: The local IP address.
    """
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a known external server (e.g., Google's DNS server)
        s.connect(("8.8.8.8", 80))
        # Get the local IP address assigned to the socket
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        #print(f"Error getting local IP address: {e}")
        return "127.0.0.1"

def hostnameToIp(hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.gaierror as e:
        print(f"DNS lookup failed: {e}")
        return None

def isServerAlive(ip, port):
    if ip.lower() == "localhost":
        ip = "127.0.0.1"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)  # Timeout in case of server not responding
    try:
        sock.connect((ip, port))
        sock.close()
        return True
    except socket.error:
        return False

def openURL(url):
    if shutil.which("termux-open-url"):
        command = f'''termux-open-url "{url}"'''
        runSystemCommand(command)
    else:
        webbrowser.open(url)

def isUrlAlive(url):
    #print(urllib.request.urlopen("https://letmedoit.ai").getcode())
    try:
        request = requests.get(url, timeout=5)
    except:
        return False
    return True if request.status_code == 200 else False

def is_valid_url(url: str) -> bool:
    # Regular expression pattern for URL validation
    pattern = re.compile(
        r'^(http|https)://'  # http:// or https://
        r'([a-zA-Z0-9.-]+)'  # domain name
        r'(\.[a-zA-Z]{2,63})'  # dot and top-level domain (e.g. .com, .org)
        r'(:[0-9]{1,5})?'  # optional port number
        r'(/.*)?$'  # optional path
    )
    return bool(re.match(pattern, url))

def getWebText(url):
    try:
        # Download webpage content
        response = requests.get(url, timeout=30)
        # Parse the HTML content to extract text
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except:
        return ""

def downloadFile(url, localpath, timeout=60):
    response = requests.get(url, timeout=timeout)
    with open(localpath, 'wb') as fileObj:
        fileObj.write(response.content)

def downloadWebContent(url, timeout=60, folder="", ignoreKind=False):
    print("Downloading web content ...")
    hasExt = re.search(r"\.([^\./]+?)$", url)
    supported_documents = TEXT_FORMATS[:]
    supported_documents.remove("org")

    response = requests.get(url, timeout=timeout)
    folder = folder if folder and os.path.isdir(folder) else os.path.join(config.toolMateAIFolder, "temp")
    filename = quote(url, safe="")
    def downloadBinary(filename=filename):
        filename = os.path.join(folder, filename)
        with open(filename, "wb") as fileObj:
            fileObj.write(response.content)
        return filename
    def downloadHTML(filename=filename):
        filename = os.path.join(folder, f"{filename}.html")
        with open(filename, "w", encoding="utf-8") as fileObj:
            fileObj.write(response.text)
        return filename

    try:
        if ignoreKind:
            filename = downloadBinary()
            print(f"Downloaded at: {filename}")
            return ("any", filename)
        elif hasExt and hasExt.group(1) in supported_documents:
            return ("document", downloadBinary())
        elif is_valid_image_url(url):
            return ("image", downloadBinary())
        else:
            # download content as text
            # Save the content to a html file
            return ("text", downloadHTML())
    except Exception as e:
        showErrors(e)
        return ("", "")