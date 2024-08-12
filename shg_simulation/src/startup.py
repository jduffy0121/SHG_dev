from .sys_config import OS_CONFIG
from .shg_gui import init_gui
from .check_repo_files import check_files, pull_missing_files

def main():
    all_files = check_files()
    if isinstance(all_files, str):
        print(f"Missing the following project files:{all_files}")
        while True:
            print("\n0\tReclone package from live git (will overwrite any custom files) \nq\tQuit program\t")
            user_input = input("Selection: ")
            if user_input == '0':
                pull_missing_files()
                break 
            elif user_input == 'q':
                return
    OS_CONFIG.set_config()
    if OS_CONFIG.invalid_os == True: #Test to see if the os is valid before starting application, kills script if it is invalid
        print(f"Version {pkg_resources.get_distribution('shg_simulation').version} of SHG Simulation Package is not supported on this operating system.")
        print("Supported operating systems: Windows, macOS, and Linux.")
        return
    init_gui()
