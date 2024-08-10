import numpy as np
import types
import yaml
import platform
from urllib.parse import quote
import pathlib
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QComboBox, QWidget, QLabel, QCheckBox, QRadioButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainterPath, QRegion, QColor

@dataclass
class PointGroupFit:
    name: str = ''
    channel: str = ''
    func: types.FunctionType = field(default_factory=lambda x: x)
    weights: List[Tuple[str, float]] = field(default_factory=lambda: [()])
    fit_r: List[float] = field(default_factory=lambda: [0.0])
    fit_phi: List[float] = field(default_factory=lambda: [0.0])
    r2: float = 1.0
    legend: str = ''
    active: bool = False

@dataclass
class FitManager:
    point_groups: List[PointGroupFit] = field(default_factory=lambda: [])
    selection_mode: str = 'Single'
    selected_channels: List[str] = field(default_factory=lambda: [])
    plots_showing: List[str] = field(default_factory=lambda: [])
    prev_selected: List[str] = field(default_factory=lambda: [])
    expanded_window: bool = False
    figures: List[Tuple[matplotlib.figure, matplotlib.axes]] = field(default_factory=lambda: [])

@dataclass
class FitConfig:
    geometry: str = ''
    channels: List[str] = field(default_factory=lambda: [])
    data: Dict[str, List[float]] = field(default_factory=lambda: {})
    data_files: List[pathlib.Path] = field(default_factory=lambda: [None] * 6)
    column_headers: bool = False
    source: str = ''
    sys: str = ''
    plane: str = ''

@dataclass
class FitInputManager:
    valid_channels: List[str] = field(default_factory=lambda: [])
    data_files: List[pathlib.Path] = field(default_factory=lambda: [None] * 6)
    column_headers: bool = False

@dataclass
class SimInputManager:
    crystal_type: str = 'Unary'
    unary_crysal: str = ''
    binary_crysal: str = ''
    tertiary_crystal: str = ''

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

        styles_path = f'{pathlib.Path(__file__).parent.parent.resolve()}/styles/{self.os.lower()}_styles.qss'
        config_path = f'{pathlib.Path(__file__).parent.parent.resolve()}/configs/{self.os.lower()}_config.yaml'
    
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
