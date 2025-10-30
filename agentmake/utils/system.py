import os, re, subprocess, datetime, psutil, platform, socket, getpass, geocoder, pendulum
from agentmake.utils.online import isServerAlive, get_wan_ip, get_local_ip

def getCliOutput(cli):
    try:
        process = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, *_ = process.communicate()
        return stdout.decode("utf-8")
    except:
        return ""

def getCpuThreads():
    physical_cpu_core = psutil.cpu_count(logical=False)
    return physical_cpu_core if physical_cpu_core and physical_cpu_core > 1 else 1

def getCurrentDateTime():
    current_datetime = datetime.datetime.now()
    return current_datetime.strftime("%Y-%m-%d_%H_%M_%S")

def getDeviceInfo(includeIp=True, isLite=False):
    """Get device information"""
    if isServerAlive("8.8.8.8", 53):
        g = geocoder.ip('me')
        location = f"""Latitude & longitude: {g.latlng}
Country: {g.country}
State: {g.state}
City: {g.city}"""
    else:
        location = ""
    if isServerAlive("8.8.8.8", 53) and includeIp:
        wan_ip = get_wan_ip()
        local_ip = get_local_ip()
        ipInfo = f'''Wan ip: {wan_ip}
Local ip: {local_ip}
'''
    else:
        ipInfo = ""
    if isLite:
        dayOfWeek = ""
    else:
        dayOfWeek = pendulum.now().format('dddd')
        dayOfWeek = f"Current day of the week: {dayOfWeek}"
    user_os = "macOS" if platform.system() == "Darwin" else platform.system()
    if user_os == "Linux":
        user_os = "Linux (" + get_linux_distro().get("name", "") + ")"
    return f"""Machine: {platform.machine()}
Architecture: {platform.architecture()[0]}
Processor: {platform.processor()}
CPU threads: {getCpuThreads()}
RAM: {str(round(psutil.virtual_memory().total / (1024.0 **3)))} GB
Operating system: {user_os}
OS Version: {platform.version()}
Hostname: {socket.gethostname()}
Username: {getpass.getuser()}
Python version: {platform.python_version()}
Python implementation: {platform.python_implementation()}
Current directory: {os.getcwd()}
Current time: {str(datetime.datetime.now())}
{dayOfWeek}
{ipInfo}{location}"""

def get_linux_distro():
    """
    Detects the Linux distribution using various methods.

    Returns:
    A dictionary containing information about the distribution, or None if 
    the distribution could not be determined.
    """

    if os.path.isdir("/data/data/com.termux/files/home") and not os.getcwd().startswith("/root"):
        return {"name": "Android Termux", "version": ""}

    # Method 1: Check /etc/os-release (most reliable)
    try:
        with open("/etc/os-release", "r") as f:
            os_release_content = f.readlines()
            distro_info = {}
            for line in os_release_content:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    distro_info[key.lower()] = value.strip('"')
        
        # Prioritize 'pretty_name' or 'name' if available.
        if distro_info.get("pretty_name"):
            distro_info["name"] = distro_info["pretty_name"]
        else:
            distro_info["name"] = "Unknown"

        return distro_info
    except FileNotFoundError:
        pass

    # Method 2: Check for distro-specific files in /etc
    distro_files = {
        "redhat": "/etc/redhat-release",
        "fedora": "/etc/fedora-release",
        "centos": "/etc/centos-release",
        "oracle": "/etc/oracle-release",
        "debian": "/etc/debian_version",
        "ubuntu": "/etc/lsb-release",
        "linuxmint": "/etc/lsb-release",
        "gentoo": "/etc/gentoo-release",
        "alpine": "/etc/alpine-release",
        "arch": "/etc/arch-release",
        "manjaro": "/etc/lsb-release",
        "opensuse": "/etc/SuSE-release", 
        "suse": "/etc/SuSE-release" # older SUSE
    }

    for distro_name, file_path in distro_files.items():
        try:
            with open(file_path, "r") as f:
                content = f.read().strip()
                
                if distro_name == "ubuntu" or distro_name == "linuxmint" or distro_name == "manjaro":
                    # Parse lsb-release for Ubuntu, Mint and Manjaro
                    distro_info = {}
                    for line in content.splitlines():
                        key, value = line.split("=")
                        distro_info[key.lower()] = value.strip()
                    if distro_info.get("distrib_description"):
                        return {"name": distro_info["distrib_description"], "version": distro_info.get("distrib_release"), "codename": distro_info.get("distrib_codename")}
                    else:
                        return {"name": distro_info.get("distrib_id"), "version": distro_info.get("distrib_release"), "codename": distro_info.get("distrib_codename")}

                elif distro_name == "debian":
                    # Debian only has a version number 
                    return {"name": "Debian", "version": content}

                elif distro_name == "arch":
                    # Arch Linux typically has an empty /etc/arch-release
                    return {"name": "Arch Linux"}
                    
                else:
                    # Extract name and version for other distributions
                    # This regex tries to handle different formats
                    match = re.search(r"([\w\s]+)[\s|-]*release\s*([\d.abrc]+)?", content, re.IGNORECASE)

                    if match:
                        name = match.group(1).strip()
                        version = match.group(2).strip() if match.group(2) else None
                        
                        # Special case handling for CentOS to differentiate from RHEL
                        if name.lower().startswith("centos"):
                            return {"name": "CentOS", "version": version}
                        else:
                            return {"name": name, "version": version}
                    else:
                        return {"name": distro_name, "version": content}

        except FileNotFoundError:
            pass

    # Method 3: Use platform.linux_distribution() (deprecated)
    # try:
    #   # This is deprecated in Python 3.8+ and removed in Python 3.10
    #   distro_name, version, codename = platform.linux_distribution()
    #   if distro_name:
    #     return {"name": distro_name, "version": version, "codename": codename}
    # except AttributeError:
    #   pass
        
    # Method 4: Use lsb_release command (if available)
    try:
        # Check if lsb_release command exists
        if os.system("which lsb_release > /dev/null 2>&1") == 0:
            distro_info = {}
            output = os.popen("lsb_release -a").read()
            for line in output.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    distro_info[key.strip().lower().replace(" ", "_")] = value.strip()
            if distro_info.get("distributor_id"):
                return {"name": distro_info["distributor_id"], "version": distro_info.get("release"), "codename": distro_info.get("codename"), "description": distro_info.get("description")}
    except Exception:
        pass

    return {"name": "", "version": ""}  # Could not determine distro

# close open sockets at exit
def close_open_sockets():
    def terminate_connection(fd):
        # Iterate through all network connections
        for conn in psutil.net_connections(kind='inet'):
            if conn.fd == fd:  # Match the file descriptor
                try:
                    process = psutil.Process(conn.pid)
                    process.terminate()  # Kill the process holding the socket open
                    process.wait()  # Wait for the process to terminate
                except Exception as e:
                    print(f"Error terminating process: {e}")
    for conn in psutil.net_connections(kind='inet'):
        fd = None
        if found := re.search(r"sconn\(fd=([0-9]+?),.*?11434", str(conn)): # ollama
            fd = int(found.group(1))
        elif found := re.search(r"sconn\(fd=([0-9]+?),.*?'34.96.76.122'", str(conn)): # cohere
            fd = int(found.group(1))
        if fd:
            terminate_connection(fd)