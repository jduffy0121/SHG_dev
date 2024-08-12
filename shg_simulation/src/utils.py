import pathlib
import yaml
import pandas as pd
import requests
import numpy as np
import os
import matplotlib.pyplot as plt
from typing import List, Tuple, Union, Dict
from mp_api.client import MPRester

from .sys_config import PACKAGE_DIR, REPO_DIR
    
def search_api(crystal:str):
    with open(f'{PACKAGE_DIR}/configs/materials_project_api_key.txt', 'w') as file:
        api_key = file.read()
    file.close()
    with MPRester(api_key) as mpr:
        pass
        #materials = m.get_data(crystal)
    #return materials

def test_api_key(key=None) -> bool:
    file_path = f'{PACKAGE_DIR}/configs/materials_project_api_key.txt'
    if not key:
        if not pathlib.Path(file_path).exists():
            return False
        with open(file_path, 'r') as file:
            api_key = file.read()
        file.close()
    else:
        api_key = key
    try:
        with MPRester(api_key) as mpr:
            material = mpr.summary.search(material_ids=["mp-149"])
        return True
    except Exception:
        if pathlib.Path(file_path).exists():
            os.remove(file_path)
        return False

def check_internet_connection() -> bool:
    try:
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            return True
        else: 
            return False
    except requests.ConnectionError:
        return False
    except requests.Timeout:
        return False

def remove_crystal(crystal_name: str, file_path_to_read: pathlib.Path, file_path_to_write: pathlib.Path) -> None:
    data = read_crystal_file(file_path=file_path_to_read)
    updated_data = [crystal for crystal in data if f'{crystal["name"]} ({crystal["symbol"]})' != crystal_name]
    with open(file_path_to_write, 'w') as file:
        yaml.dump(updated_data, file)
    file.close()

def read_crystal_file(file_path: pathlib.Path) -> List[Dict]:
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    file.close()
    return data

def read_data(data_path: pathlib.Path, header: bool) -> Union[List[Tuple[float, float]], str]: 
    try:
        if header:
            df = pd.read_csv(data_path)
        else:
            df = pd.read_csv(data_path, header=None)
        if df.shape[1] > 2:
            return "Too many columns"
        elif df.shape[1] < 2:
            return "Too few columns"
        data_list = list(zip(df.iloc[:, 0], df.iloc[:, 1]))
        for (x,y) in data_list:
            try:
                if np.isnan(x) or np.isnan(y):
                    return "Missing data elem"
            except TypeError:
                return "Incorrect dtype"
        return data_list 
    except pd.errors.EmptyDataError:
        return "No data"

def get_point_groups(source: str, sys: str) -> List[str]:
    e_d_point_groups = {'Triclinic': ['C_1'], 'Monoclinic': ['C_2', 'C_1h'], 'Orthorhombic': ['D_2', 'C_2v'], 'Tetragonal': ['C_4', 'S_4', 'D_4', 'C_4v', 'D_2d'], 
                        'Trigonal': ['C_3', 'D_3', 'C_3v'], 'Hexagonal': ['C_6', 'C_3h', 'D_6', 'C_6v', 'D_3h'], 'Cubic': ['T', 'O', 'T_d']}
    e_q_or_m_d_point_groups = {'Triclinic': ['S_2'], 'Monoclinic': ['C_2h'], 'Orthorhombic': ['D_2h'], 'Tetragonal': ['C_4h', 'D_4h'], 
                               'Trigonal': ['C_6', 'D_3d'], 'Hexagonal': ['C_6h', 'D_6h'], 'Cubic': ['T_h', 'O_h']}
    if source == 'e_d':
        return e_d_point_groups[sys]
    else:
        return e_q_or_m_d_point_groups[sys]

def convert_to_config_str(gui_name: str) -> str:
    name_scheme = {'||': 'Parallel', '⊥': 'Perpendicular', 'Reflection': 'refl', 'Transmission': 'trans', 
                   'Electric Dipole': 'e_d', 'Electric Quadrupole': 'e_q', 'Magnetic Dipole': 'm_d', 
                   '(0 0 1)': '001','Rotz(90°)': 'rotz90'}
    try:
        return name_scheme[f'{gui_name}']
    except KeyError:
        return gui_name

def polar_plot(title: str, data: List[Tuple[float, float]], width: int, height: int, dpi: int, data_color: str, fits=None):
    r_values = [r for phi, r in data]
    phi_values = [phi for phi, r in data]
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(width, height), dpi=dpi)
    ax.scatter(phi_values, r_values, color=data_color)
    if fits != None:
        for fit in fits:
            ax.plot(fit.fit_phi, fit.fit_r, color=fit.legend.lower())
    ax.set_title(title)
    ax.set_aspect('equal')
    return fig, ax
