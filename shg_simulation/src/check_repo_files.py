import pathlib
import os
from typing import Union
import git

REPO_DIR = pathlib.Path(__file__).parent.parent.resolve()
PACKAGE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()

def check_files() -> Union[bool, str]:
    missing_configs = []
    if os.path.exists(f'{REPO_DIR}/configs'):
        configs = os.listdir(f'{REPO_DIR}/configs')
        for file in ['darwin_config.yaml', 'windows_config.yaml', 'linux_config.yaml']:
            if file not in configs:
                missing_configs.append(file)
    else:
        missing_configs = ['darwin_config.yaml, windows_config.yaml', 'linux_config.yaml']

    missing_data = []
    if os.path.exists(f'{REPO_DIR}/data'):
        data = os.listdir(f'{REPO_DIR}/data')
        for file in ['default_crystals.yaml', 'point_groups.yaml']:
            if file not in data:
                missing_data.append(file)
    else:
        missing_data = ['default_crystals.yaml', 'point_groups.yaml']

    missing_fits = []
    if os.path.exists(f'{REPO_DIR}/fits'):
        fits = os.listdir(f'{REPO_DIR}/fits')
        for file in ['default_fits.yaml']:
            if file not in fits:
                missing_fits.append(file)
    else:
        missing_fits = ['default_fits.yaml']


    missing_imgs = []
    if os.path.exists(f'{REPO_DIR}/imgs'):
        imgs = os.listdir(f'{REPO_DIR}/imgs')
        for file in ['logo_full.png', 'logo_mini.png']:
            if file not in imgs:
                missing_imgs.append(file)
    else:
        missing_imgs = ['logo_full.png', 'logo_mini.png']

    missing_styles = []
    if os.path.exists(f'{REPO_DIR}/styles'):
        styles = os.listdir(f'{REPO_DIR}/styles')
        for file in ['darwin_styles.qss', 'windows_styles.qss','linux_styles.qss']:
            if file not in styles:
                missing_styles.append(file)
    else:
        missing_styles = ['logo_full.png', 'logo_mini.png']

    missing_roots = []
    if os.path.exists(f'{PACKAGE_DIR}'):
        roots = os.listdir(PACKAGE_DIR)
        for file in ['updates.txt', 'LICENSE']:
            if file not in roots:
                missing_roots.append(file)
    else:
        missing_roots = ['updates.txt', 'LICENSE']
    message = ''
    if missing_roots:
        message = message + f"\n\tRoot files in ~/: {', '.join(missing_roots)}"
    if missing_configs:
        message = message + f"\n\tConfig files in ~/config: {', '.join(missing_configs)}"
    if missing_data:
        message = message + f"\n\tData files in ~/data: {', '.join(missing_data)}"
    if missing_fits:
        message = message + f"\n\tFit files in ~/fit: {', '.join(missing_fits)}"
    if missing_imgs:
        message = message + f"\n\tImg files in ~/imgs: {', '.join(missing_imgs)}"
    if missing_styles:
        message = message + f"\n\tStyle files in ~/styles: {', '.join(missing_styles)}"

    if message == '':
        return True
    else:
        return message

def pull_missing_files() -> None:
    git_url = 'https://github.com/jduffy0121/SHG_dev.git'
    repo = git.Repo(PACKAGE_DIR)
    repo.remotes.origin.fetch()
    repo.git.reset('--hard', 'origin/main')
    print('\nRepository files successfully recovered.\nRestarting program...')
