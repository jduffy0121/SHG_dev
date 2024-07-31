import inspect
import numpy as np
from scipy.optimize import curve_fit

from .gui_classes import *
from .utils import *

def init_fit_classes(config: FitConfig, manager: FitManager) -> None:
    point_groups = get_point_groups(source=config.source, sys=config.sys)
    colors = ['Red', 'Green', 'Orange', 'Purple', 'Brown', 'Blue']
    for channel in config.channels:
        i = 0
        for group in point_groups:
            group_class = PointGroupFit(name=group, channel=channel, func=get_fit_func(point_group=group), legend=colors[i])
            group_class.fit_phi, group_class.fit_r, group_class.r2, group_class.weights = get_fit_results(data=config.data[channel], 
                                                                                                            func=group_class.func)
            manager.point_groups.append(group_class)
            i = i + 1

def get_fit_func(point_group: str):
    fit_func={'C_1': lambda x,a, const, *p: a * np.sin(x + const) ** 2, 'C_2': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 
              'C_1h': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'D_2': lambda x,a, const, *p: a * np.sin(x + const) ** 2,
              'C_2v': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'C_4': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 
              'S_4': lambda x, a, const, *p: a * np.sin(2 * x + 2 * const) ** 2, 'D_4': lambda x, a, b, const, *p: a * np.sin(x + const) ** 2 + b * np.cos(x + const) ** 2, 
              'C_4v': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'D_2d': lambda x, a, const, *p: a * np.sin(x + const) ** 2,
              'C_3': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'D_3': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 
              'C_3v': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'C_6': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 
              'C_3h': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'D_6': lambda x, a, const, *p: a * np.sin(x + const) ** 2,
              'C_6v': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'D_3h': lambda x, a, const, *p: a * np.sin(x + const) ** 2,
              'T': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'O': lambda x, a, const, *p: a * np.sin(x + const) ** 2,
              'T_d': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'S_2': lambda x, a, const, *p: a * np.sin(x + const) ** 2,
              'D_2h': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'C_4h': lambda x, a, const, *p: a * np.sin(x + const) ** 2,
              'D_4h': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'C_6': lambda x, a, const, *p: a * np.sin(x + const) ** 2,
              'D_3d': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'C_6h': lambda x, a, const, *p: a * np.sin(x + const) ** 2,
              'D_6h': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'T_h': lambda x, a, const, *p: a * np.sin(x + const) ** 2,
              'O_h': lambda x, a, const, *p: a * np.sin(x + const) ** 2, 'C_2h':  lambda x, a, const, *p: a * np.sin(x + const) ** 2}
    return fit_func[point_group]

def get_readable_fit_func(point_group:str) -> str:
    readable_func={'C_1': 'a * sin²(Φ + const)', 'C_2': 'a * sin²(Φ + const)', 
              'C_1h': 'a * sin²(Φ + const)', 'D_2': 'a * sin²(Φ + const)',
              'C_2v': 'a * sin²(Φ + const)', 'C_4': 'a * sin²(Φ + const)', 
              'S_4': 'a * sin²(2(Φ + const))', 'D_4': 'a * sin²(Φ + const) + b * cos²(Φ + const) ', 
              'C_4v': 'a * sin²(Φ + const)', 'D_2d': 'a * sin²(Φ + const)',
              'C_3': 'a * sin²(Φ + const)', 'D_3': 'a * sin²(Φ + const)', 
              'C_3v': 'a * sin²(Φ + const)', 'C_6': 'a * sin²(Φ + const)', 
              'C_3h': 'a * sin²(Φ + const)', 'D_6': 'a * sin²(Φ + const)',
              'C_6v': 'a * sin²(Φ + const)', 'D_3h': 'a * sin²(Φ + const)',
              'T': 'a * sin²(Φ + const)', 'O': 'a * sin²(Φ + const)',
              'T_d': 'a * sin²(Φ + const)', 'S_2': 'a * sin²(Φ + const)',
              'D_2h': 'a * sin²(Φ + const)', 'C_4h': 'a * sin²(Φ + const)',
              'D_4h': 'a * sin²(Φ + const)', 'C_6': 'a * sin²(Φ + const)',
              'D_3d': 'a * sin²(Φ + const)', 'C_6h': 'a * sin²(Φ + const)',
              'D_6h': 'a * sin²(Φ + const)', 'T_h': 'a * sin²(Φ + const)',
              'O_h': 'a * sin²(Φ + const)'}
    return readable_func[point_group]

def get_fit_results(data, func, weights=None):
    r_values = np.array([r for phi, r in data])
    phi_values = np.array([phi for phi, r in data])
    fit_function = func
    sig = inspect.signature(fit_function)
    fit_params = sig.parameters
    num_of_fit_params = len(fit_params) - 2
    if num_of_fit_params > 0:
        p0=np.zeros(num_of_fit_params)
    else:
        p0=np.zeros(1)
    params, params_covariance = curve_fit(fit_function, phi_values, r_values, p0=p0)
    weights = []
    i = 0
    for param_str, param in fit_params.items():
        if not param_str in ['x', 'p']:
            weights.append((param_str, params[i]))
            i = i + 1
    r_pred = fit_function(phi_values, *params)
    res = np.sum((r_values - r_pred) ** 2)
    tot = np.sum((r_values - np.mean(r_values)) ** 2)
    r2 = 1 - (res / tot)
    return phi_values, r_pred, r2, weights
