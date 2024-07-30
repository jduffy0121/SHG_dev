import numpy as np
import types
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainterPath, QRegion, QColor

@dataclass
class PointGroupFit:
    name: str = 'C_1'
    channel: str = 'SS'
    func: types.FunctionType = field(default_factory=lambda x: a * np.sin(x + const) ** 2)
    weights: List[Tuple[str, float]] = field(default_factory=lambda: [()])
    fit_r: List[float] = field(default_factory=lambda: [0.0])
    fit_phi: List[float] = field(default_factory=lambda: [0.0])
    r2: float = 1.0
    legend: str = 'Red'
    active: bool = False

@dataclass
class FitManager:
    point_groups: List[PointGroupFit] = field(default_factory=lambda: [])
    selection_mode: str = 'Single'
    selected_channels: List[str] = field(default_factory=lambda: [])
    plots_showing: List[str] = field(default_factory=lambda: [])
    prev_selected: List[str] = field(default_factory=lambda: [])
    expanded_window: bool = False
    figures: List[Tuple[matplotlib.figure, matplotlib.axes]] = field(default_factory=lambda: [()])

@dataclass
class FitConfig:
    geometry: str = 'trans'
    channels: List[str] = field(default_factory=lambda: [])
    data: Dict[str, List[float]] = field(default_factory=lambda: {})
    source: str = 'e_d'
    sys: str = 'triclinic'
    plane: str = '001'

class FittingResultsLayout:
    def __init__(self):
        self.tabs_layout = QVBoxLayout()
        self.expanded_layout = QHBoxLayout()
        self.no_plots_layout = QVBoxLayout()
        self.add_button_layout = QVBoxLayout()

        self.add_button_group = None

        self.expanded = False

    def set_initial_layout(self):
        pass

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
    def __init__(self, figure, plot_id):
        super().__init__(figure)
        self.plot_id = plot_id
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
        rect = QRectF(0, 0, 290, 290)
        center = rect.center()
        radius = 290/2
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
