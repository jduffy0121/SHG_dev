import pathlib
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

def convert_to_config_str(gui_name: str) -> str:
    name_scheme = {'||': 'Parallel', '⊥': 'Perpendicular', 'Reflection': 'refl', 
                   'Electric Dipole': 'e_dip', 'Electric Quadrupole': 'e_quad', 'Magnetic Dipole': 'm_dip', 
                   '(0 0 1)': '001','Rotz(90°)': 'rotz90'}
    try:
        return name_scheme[f'{gui_name}']
    except KeyError:
        return gui_name

def polar_plot(title: str, data_list: List[Tuple[float, float]], width: int, height: int, dpi: int, add_func = None):
    r_values = [r for theta, r in data_list]
    theta_values = [theta for theta, r in data_list]
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(width, height), dpi=dpi)
    ax.scatter(theta_values, r_values)
    ax.set_title(title)
    ax.set_aspect('equal')
    return fig, ax
