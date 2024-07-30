import pathlib
import inspect
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas as df
from typing import List, Tuple, Union
from .gui_classes import *

def read_data(data_path: pathlib.Path) -> Union[List[Tuple[float, float]], str]: 
    try:
        df = pd.read_csv(data_path) 
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
    name_scheme = {'||': 'Parallel', '⊥': 'Perpendicular', 'Reflection': 'refl', 
                   'Electric Dipole': 'e_d', 'Electric Quadrupole': 'e_q', 'Magnetic Dipole': 'm_d', 
                   '(0 0 1)': '001','Rotz(90°)': 'rotz90'}
    try:
        return name_scheme[f'{gui_name}']
    except KeyError:
        return gui_name

def polar_plot(title: str, data: List[Tuple[float, float]], width: int, height: int, dpi: int, fits=None):
    r_values = [r for phi, r in data]
    phi_values = [phi for phi, r in data]
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(width, height), dpi=dpi)
    ax.scatter(phi_values, r_values)
    if fits != None:
        for fit in fits:
            ax.plot(fit.fit_phi, fit.fit_r, color=fit.legend.lower())
    ax.set_title(title)
    ax.set_aspect('equal')
    return fig, ax
