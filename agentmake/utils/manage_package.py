from packaging import version
from importlib_metadata import version as lib_version
import requests, shutil, sys, subprocess, re


def isCommandInstalled(package):
    return True if shutil.which(package.split(" ", 1)[0]) else False

def getPackageInstalledVersion(package):
    try:
        installed_version = lib_version(package)
        return version.parse(installed_version)
    except:
        return None

def getPackageLatestVersion(package):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
        latest_version = response.json()['info']['version']
        return version.parse(latest_version)
    except:
        return None

def list_installed_packages():
    import importlib.metadata
    packages = importlib.metadata.distributions()
    for package in packages:
        print(f"{package.metadata['Name']} {package.version}")

def updatePip():
    if isCommandInstalled("pip"):
        pipInstallCommand = f"{sys.executable} -m pip install"
        pipFailedUpdated = "pip tool failed to be updated!"
        try:
            # Update pip tool in case it is too old
            updatePip = subprocess.Popen(f"{pipInstallCommand} --upgrade pip", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            *_, stderr = updatePip.communicate()
            if not stderr:
                print("pip tool updated!")
            else:
                print(pipFailedUpdated)
        except:
            print(pipFailedUpdated)

def installPipPackage(module, update=False):
    #executablePath = os.path.dirname(sys.executable)
    #pippath = os.path.join(executablePath, "pip")
    #pip = pippath if os.path.isfile(pippath) else "pip"
    #pip3path = os.path.join(executablePath, "pip3")
    #pip3 = pip3path if os.path.isfile(pip3path) else "pip3"

    if isCommandInstalled("pip"):
        pipInstallCommand = f"{sys.executable} -m pip install"

        if update:
            updatePip()
        try:
            upgrade = (module.startswith("-U ") or module.startswith("--upgrade "))
            if upgrade:
                moduleName = re.sub("^[^ ]+? (.+?)$", r"\1", module)
            else:
                moduleName = module
            print(f"{'Upgrading' if upgrade else 'Installing'} '{moduleName}' ...")
            installNewModule = subprocess.Popen(f"{pipInstallCommand} {module}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            *_, stderr = installNewModule.communicate()
            if not stderr:
                print(f"Package '{moduleName}' {'upgraded' if upgrade else 'installed'}!")
            else:
                print(f"Failed {'upgrading' if upgrade else 'installing'} package '{moduleName}'!")
                print(stderr)
            return True
        except:
            return False

    else:
        print("pip command is not found!")
        return False