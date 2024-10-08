import yaml
import platform
import pathlib

REPO_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
PACKAGE_DIR = pathlib.Path(__file__).parent.parent.resolve()

class OSConfig:
    def __init__(self):
        self.os = platform.system()
        self.fit_win_upld_box_len = 0
        self.fit_win_upld_box_ht = 0
        self.fit_res_mini_plt_dpi = 0
        self.fit_res_mini_plt_r = 0
        self.full_plt_dpi = 0
        self.full_plt_len = 0
        self.invalid_os = False
        self.style_sheet = ''

    def set_config(self) -> None:
        if not self.os in ['Windows', 'Darwin', 'Linux']:
            self.invalid_os = True
            return

        styles_path = f'{PACKAGE_DIR}/styles/{self.os.lower()}_styles.qss'
        config_path = f'{PACKAGE_DIR}/configs/{self.os.lower()}_config.yaml'
    
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        file.close()

        self.fit_win_upld_box_len = config['fit_win_upld_box_len']
        self.fit_win_upld_box_ht = config['fit_win_upld_box_ht']
        self.fit_res_mini_plt_dpi = config['fit_res_mini_plt_dpi']
        self.fit_res_mini_plt_r = config['fit_res_mini_plt_r']
        self.full_plt_dpi = config['full_plt_dpi']
        self.full_plt_len = config['full_plt_len']

        with open(styles_path, 'r') as file:
            self.style_sheet = file.read() 
        file.close()

OS_CONFIG = OSConfig()
