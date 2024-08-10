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

class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #171717;
            } 
            QGroupBox{
                background-color: #818589;
                border: 5px solid #303030
            } 
            QPushButton{
                background-color: #626262;
                color: white;
                border: 1px solid #808080;
                border-radius: 6px; 
                padding: 2px 5px;
            }
            QPushButton:hover {
                background: #9B9B9B;
                border: 1px solid #C0C0C0;
            }
        """)

class TableCheckBox(QCheckBox):
    def __init__(self, text=None):
        super().__init__()
        self.setText(text)
        self.setStyleSheet('background-color: #171717')

    def setSelected(self, selected):
        if selected:
            self.setStyleSheet('background-color: #565656')
        else:
            self.setStyleSheet('background-color: #171717')

class TableLabel(QLabel):
    def __init__(self, text=None):
        super().__init__()
        self.setText(text)
        self.setStyleSheet('background-color: #171717')

    def setSelected(self, selected):
        if selected:
            self.setStyleSheet('background-color: #565656')
        else:
            self.setStyleSheet('background-color: #171717')

class GroupLabel(QLabel):
    def __init__(self, text=None):
        super().__init__()
        self.setText(text)
        self.setStyleSheet('background-color: #303030')

class GroupRadioButton(QRadioButton):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.setStyleSheet('background-color: #303030')

class GroupCheckBox(QCheckBox):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.setStyleSheet('background-color: #303030')
        
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
