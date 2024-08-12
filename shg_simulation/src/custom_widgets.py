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
    signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.currentIndexChanged.connect(self.selection_change)

    def selection_change(self, event):
        self.signal.emit(self.currentText())

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
        glow_effect.setColor(QColor(0, 0, 255, 160))  
        glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(glow_effect)

    def remove_glow_effect(self):
        self.setGraphicsEffect(None)
        self.glow = None
