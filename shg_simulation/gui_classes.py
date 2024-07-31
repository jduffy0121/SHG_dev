import numpy as np
import types
import platform
from urllib.parse import quote
import pathlib
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QComboBox
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
    selection_mode: str = ''
    selected_channels: List[str] = field(default_factory=lambda: [])
    plots_showing: List[str] = field(default_factory=lambda: [])
    prev_selected: List[str] = field(default_factory=lambda: [])
    expanded_window: bool = False
    figures: List[Tuple[matplotlib.figure, matplotlib.axes]] = field(default_factory=lambda: [()])

@dataclass
class FitConfig:
    geometry: str = ''
    channels: List[str] = field(default_factory=lambda: [])
    data: Dict[str, List[float]] = field(default_factory=lambda: {})
    source: str = ''
    sys: str = ''
    plane: str = ''

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
        self.set_config()

    def set_config(self) -> None:
        windows_config = {'fit_win_upld_box_len': 300, 'fit_win_upld_box_ht': 15,
                      'fit_res_mini_plt_dpi': 70, 'fit_res_mini_plt_r': 145, 'full_plt_dpi': 210,
                      'full_plt_len': 280}
        mac_config = {'fit_win_upld_box_len': 300, 'fit_win_upld_box_ht': 15,
                      'fit_res_mini_plt_dpi': 70, 'fit_res_mini_plt_r': 145, 'full_plt_dpi': 210,
                      'full_plt_len': 280}
        linux_config = {'fit_win_upld_box_len': 300, 'fit_win_upld_box_ht': 15,
                      'fit_res_mini_plt_dpi': 70, 'fit_res_mini_plt_r': 145, 'full_plt_dpi': 210,
                      'full_plt_len': 280}
        if self.os == 'Windows':
            self.fit_win_upld_box_len = windows_config['fit_win_upld_box_len']
            self.fit_win_upld_box_ht = windows_config['fit_win_upld_box_ht']
            self.fit_res_mini_plt_dpi = windows_config['fit_res_mini_plt_dpi']
            self.fit_res_mini_plt_r = windows_config['fit_res_mini_plt_r']
            self.full_plt_dpi = windows_config['full_plt_dpi']
            self.full_plt_len = windows_config['full_plt_len']
            self.invalid_os = False
        elif self.os == 'Darwin':
            self.fit_win_upld_box_len = mac_config['fit_win_upld_box_len']
            self.fit_win_upld_box_ht = mac_config['fit_win_upld_box_ht']
            self.fit_res_mini_plt_dpi = mac_config['fit_res_mini_plt_dpi']
            self.fit_res_mini_plt_r = mac_config['fit_res_mini_plt_r']
            self.full_plt_dpi = mac_config['full_plt_dpi']
            self.full_plt_len = mac_config['full_plt_len']
            self.invalid_os = False
        elif self.os == 'Linux':
            self.fit_win_upld_box_len = linux_config['fit_win_upld_box_len']
            self.fit_win_upld_box_ht = linux_config['fit_win_upld_box_ht']
            self.fit_res_mini_plt_dpi = linux_config['fit_res_mini_plt_dpi']
            self.fit_res_mini_plt_r = linux_config['fit_res_mini_plt_r']
            self.full_plt_dpi = linux_config['full_plt_dpi']
            self.full_plt_len = linux_config['full_plt_len']
            self.invalid_os = False
        else:
            self.invalid_os = True
        file_name = f'{pathlib.Path(__file__).parent.resolve()}/style_sheets/{self.os.lower()}_styles.qss'
        with open(file_name, 'r') as file:
            self.style_sheet = file.read()
        file.close()
    
class CustomComboBox(QComboBox):
    box_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.currentIndexChanged.connect(self.selection_change)

    def selection_change(self, event):
        self.box_signal.emit(self.currentText())

class ComboBoxGroup:
    def __init__(self):
        self.combo_boxes = []

    def addComboBox(self, combo_box):
        self.combo_boxes.append(combo_box)

class ClickableFigureCanvas(FigureCanvas):
    canvas_signal = pyqtSignal(int)
    def __init__(self, figure, plot_id, radius):
        super().__init__(figure)
        self.plot_id = plot_id
        self.radius = radius
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setMouseTracking(True)
        self.canvas_rect = None
        self.glow = None
        self.apply_custom_shape()

    def mousePressEvent(self, event):
        self.canvas_signal.emit(self.plot_id) 
        super().mousePressEvent(event)
    
    def apply_custom_shape(self):
        path = QPainterPath()
        rect = QRectF(0, 0, self.radius * 2, self.radius * 2)
        center = rect.center()
        radius = self.radius
        path.addEllipse(center, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def apply_glow_effect(self):
        glow_effect = QGraphicsDropShadowEffect(self)
        glow_effect.setBlurRadius(100)
        glow_effect.setColor(QColor(255, 0, 0, 160))  
        glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(glow_effect)

    def remove_glow_effect(self):
        self.setGraphicsEffect(None)
        self.glow = None
