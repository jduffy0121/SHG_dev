from dataclasses import dataclass, field
from typing import List, Tuple
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainterPath, QRegion, QColor

@dataclass
class SimInputConfig:
    geometry: str = 'trans'
    channels: List[Tuple[str, List[Tuple[float, float]]]] = field(default_factory=lambda: [('Parallel', None)])
    source: str = 'e_dip'
    sys: str = 'triclinic'
    plane: str = '001'

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
