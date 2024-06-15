import platform
import pkg_resources
from .windows_gui import startup_win
from .mac_gui import startup_mac
from .linux_gui import startup_linux

def main():
    if platform.system() == 'Windows':
        #startup_win()
        startup_mac()
    elif platform.system() == "Darwin":
        startup_mac()
    elif platform.system() == "Linux":
        #startup_linux()
        startup_mac()
    else: 
        print(f"Version {pkg_resources.get_distribution('shg_simulation').version} of SHG Simulation Package is not supported on this operating system."+
            "\nSupported operating systems: Windows, macOS, and Linux.")
