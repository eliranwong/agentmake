import socket, webbrowser, shutil
from agentmake.utils.system import runSystemCommand

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

def openURL(url):
    if shutil.which("termux-open-url"):
        command = f'''termux-open-url "{url}"'''
        runSystemCommand(command)
    else:
        webbrowser.open(url)