import sys
import pathlib
import os
import pandas as pd
import markdown
import math
import sipbuild
from .utils import *
from .gui_classes import *
from .fitting import *
import numpy as np
from typing import List, Union, Tuple
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar, FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QGridLayout, QLabel, QTableWidgetItem, QTableWidget,
    QHBoxLayout, QVBoxLayout, QCheckBox, QFileDialog, QMessageBox, QGraphicsDropShadowEffect, QHeaderView,
    QRadioButton, QButtonGroup, QTextEdit, QTabWidget, QTextBrowser, QStackedLayout, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QRectF
from PyQt6.QtGui import QPixmap, QFontMetrics, QTextOption, QDesktopServices, QColor, QRegion, QPainterPath

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
MINI_PLOT_DPI = 70
FULL_PLOT_DPI = 210

class HelpWindow(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Infromation")
        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(False)

        self.background_txt = QTextBrowser()
        self.sim_txt = QTextBrowser()
        self.about_txt = QTextBrowser()
        self.background_txt.setReadOnly(True)
        self.sim_txt.setReadOnly(True)
        self.about_txt.setReadOnly(True)
        self.background_txt.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.sim_txt.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.about_txt.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.set_txt_files()

        self.background_txt.anchorClicked.connect(self.url_click)
        self.sim_txt.anchorClicked.connect(self.url_click)
        self.about_txt.anchorClicked.connect(self.url_click)

        self.tabs.addTab(self.background_txt, "Physics Background")
        self.tabs.addTab(self.sim_txt, "How to use Simulation")
        self.tabs.addTab(self.about_txt, "About Us")
        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)

        self.setFixedSize(self.layout.sizeHint())

    def set_txt_files(self) -> None:
        dir = [file for file in os.listdir(f'{SCRIPT_DIR}/ref_txt') if file[-3:] == '.md']
        for readme_file in dir:
            with open(f'{SCRIPT_DIR}/ref_txt/{readme_file}', 'r') as file: 
                html_format = markdown.markdown(file.read())
                if readme_file == 'background.md':
                    self.background_txt.setHtml(html_format)
                elif readme_file == 'sim.md': 
                    self.sim_txt.setHtml(html_format)
                else:
                    self.about_txt.setHtml(html_format)
            file.close()

    def url_click(self, url):
        QDesktopServices.openUrl(url)
        self.set_txt_files()

class PlotWindow(QWidget):
    def __init__(self, channel: list, fitting_func = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f'{channel[0]} Plot')
        self.fig, self.ax = polar_plot(title=channel[0], data_list=channel[1], width=280, height=280, dpi=FULL_PLOT_DPI, add_func=fitting_func)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def closeEvent(self, event) -> None:
        plt.close(self.fig)
        event.accept()

class SimulationResults(QWidget):
    def __init__(self, config: SimInputConfig, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Simulation")
        self.layout = QGridLayout()
        
        self.config = config

        self.tabs_layout, self.fit_check_group, self.legend_group = win_create_fit_tabs_layer(config=self.config)

        self.no_plots = QLabel("To display plots, click \'plots\'")
        self.expand_plots_button = QPushButton(">")
        self.expand_plots_button.clicked.connect(self.expand_plots_button_clicked)
        self.expanded = False
        self.plots_showing = None
        self.figures = []
        self.sel_chan = None
        self.sel_chan_txt = QLabel(f"Selected channel: {self.sel_chan}", alignment=Qt.AlignmentFlag.AlignRight)

        self.add_button_layout, self.add_button_group, self.swap_button_group = self.win_create_add_plot_layer()
        self.plot_layout, self.full_button_group, self.close_button_group = self.win_create_plot_layer(channels=self.config.channels)
        
        self.no_layout = QVBoxLayout()
        self.no_layout.addWidget(self.no_plots)
        self.expand_layout = QHBoxLayout()
        self.expand_layout.addWidget(self.expand_plots_button, alignment=Qt.AlignmentFlag.AlignBottom)

        self.help_button = QPushButton("ⓘ")
        self.help_button.clicked.connect(self.open_help_win)
        
        self.layout.addLayout(self.tabs_layout, 0, 0)
        self.layout.addLayout(self.expand_layout, 0, 1)
        self.layout.addLayout(self.no_layout, 0, 2)
        self.layout.addLayout(self.plot_layout, 0, 2)
        self.layout.addWidget(self.help_button, 1, 0)
        self.layout.addWidget(self.sel_chan_txt, 1, 2)

        self.help_win = None

        self.setLayout(self.layout)
        self.setFixedSize(1350,750)   
        
        self.clear_plots()

    def win_create_plot_layer(self, channels: list) -> (QGridLayout(), QButtonGroup(), QButtonGroup()):
        layout = QGridLayout()
        full_button_group = QButtonGroup()
        close_button_group = QButtonGroup()
        plot_id = 0
        plots_showing = []
        self.figures = []
        for channel, data_list in channels:
            sub_layout = QGridLayout()
            button_layout = QVBoxLayout()

            enlarge_button = QPushButton('⤢')
            close_button = QPushButton('✕')
            
            full_button_group.addButton(enlarge_button)
            full_button_group.setId(enlarge_button, plot_id)
            close_button_group.addButton(close_button)
            close_button_group.setId(close_button, plot_id)

            enlarge_button.clicked.connect(self.full_button_clicked)
            close_button.clicked.connect(self.close_button_clicked) 
            
            fig, ax = polar_plot(title=channel, data_list=data_list, width=290/MINI_PLOT_DPI, height=290/MINI_PLOT_DPI, dpi=MINI_PLOT_DPI)
            canvas = ClickableFigureCanvas(fig, plot_id)
            canvas.canvas_signal.connect(self.canvas_clicked)
            self.figures.append((fig, canvas))
            canvas.setFixedSize(290, 290)

            sub_layout.addWidget(canvas, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
            button_layout.addWidget(enlarge_button)
            button_layout.addWidget(close_button)
            sub_layout.addLayout(button_layout, 0, 1, alignment=Qt.AlignmentFlag.AlignTop)
            
            plots_showing.append((channel, data_list))

            if plot_id == 0:
                layout.addLayout(sub_layout, 0, 0)
            elif plot_id == 1:
                layout.addLayout(sub_layout, 0, 1)
            elif plot_id == 2:
                layout.addLayout(sub_layout, 1, 0)
            else:
                layout.addLayout(sub_layout, 1, 1)
            plot_id = plot_id + 1

        self.plots_showing = plots_showing
        return layout, full_button_group, close_button_group
    
    def win_create_add_plot_layer(self) -> (QVBoxLayout(), QButtonGroup(), QButtonGroup()):
        layout = QVBoxLayout()
        add_button_group = QButtonGroup()
        swap_button_group = QButtonGroup()
        button_id = 0
        for channel, data_list in self.config.channels:
            label = QLabel(f'{channel}')
            sub_layout = QHBoxLayout()
            sub_layout.addWidget(label)
            button_layout = QVBoxLayout()
            add_button = QPushButton('+')
            add_button.clicked.connect(self.add_button_clicked) 
            add_button_group.setId(add_button, button_id)
            swap_button = QPushButton('⇆')
            swap_button.clicked.connect(self.swap_button_clicked)
            swap_button_group.setId(swap_button, button_id)
            button_layout.addWidget(add_button)
            button_layout.addWidget(swap_button)
            sub_layout.addLayout(button_layout)
            button_id = button_id + 1
            if self.plots_showing is not None:
                plotted_chans = [chan for chan, dlist in self.plots_showing]
                if channel in plotted_chans:
                    add_button.setEnabled(False)
            if self.sel_chan is not None:
                if channel == self.sel_chan[0]:
                    swap_button.setEnabled(False)
            layout.addLayout(sub_layout)
        return layout, add_button_group, swap_button_group

    def full_button_clicked(self) -> None:
        button = self.sender()
        button_id = self.full_button_group.id(button)
        channel = self.plots_showing[button_id]
        self.sel_chan = channel
        self.update_selections()
        self.plot_window = PlotWindow(channel=channel)
        self.plot_window.show()

    def expand_plots_button_clicked(self) -> None:
        if self.expand_plots_button.text() == '>':
            self.expanded = True
            self.expand_layout.removeWidget(self.expand_plots_button)
            self.expand_plots_button.deleteLater()
            self.expand_plots_button.setParent(None)

            self.expand_layout = QHBoxLayout()
            self.expand_plots_button = QPushButton('<')
            self.expand_plots_button.clicked.connect(self.expand_plots_button_clicked)
            self.add_button_layout, self.add_button_group, self.swap_button_group = self.win_create_add_plot_layer()
            self.expand_layout.addWidget(self.expand_plots_button, alignment=Qt.AlignmentFlag.AlignBottom)
            self.expand_layout.addLayout(self.add_button_layout)
        else:
            self.expanded = False
            self.expand_plots_button.deleteLater()
            self.expand_plots_button.setParent(None)
            for i in range(self.expand_layout.count()):
                item_1 = self.expand_layout.itemAt(i)
                if item_1 is None:
                    break
                if isinstance(item_1.layout(), QVBoxLayout):
                    for j in reversed(range(item_1.count())):
                        item_2 = item_1.itemAt(j)
                        for k in reversed(range(item_2.count())):
                            item_3 = item_2.itemAt(k)
                            if isinstance(item_3.layout(), QVBoxLayout):
                                for l in reversed(range(item_3.count())):
                                    item_4 = item_3.itemAt(l)
                                    item_3.setParent(None)
                                    widget = item_4.widget()
                                    item_3.removeWidget(widget)
                                    widget.deleteLater()
                                    widget.setParent(None)
                            else:
                                widget = item_3.widget()
                                widget.deleteLater()
                                widget.setParent(None)
            self.expand_layout = QHBoxLayout()
            self.expand_plots_button = QPushButton('>')
            self.expand_plots_button.clicked.connect(self.expand_plots_button_clicked)
            self.expand_layout.addWidget(self.expand_plots_button, alignment=Qt.AlignmentFlag.AlignBottom)
        self.layout.addLayout(self.expand_layout, 0, 1)
        self.setLayout(self.layout)

    def close_button_clicked(self) -> None:
        button = self.sender()
        button_id = self.close_button_group.id(button)
        channel = self.plots_showing[button_id]
        channel_id = self.config.channels.index(channel)
        if self.expanded:
            self.add_button_group.button(channel_id).setEnabled(True)
        num_of_plts = len(self.plots_showing)
        if num_of_plts == 1:
            no_plots = QLabel("To display plots, click \'plots\'")
            self.clear_plots()
            self.no_layout.addWidget(no_plots)
            self.setLayout(self.layout)
            self.sel_chan = None
            self.update_selections()
            return
        plot_list = self.plots_showing[:button_id] + self.plots_showing[button_id+1:]
        self.clear_plots()
        self.plot_layout, self.full_button_group, self.close_button_group = self.win_create_plot_layer(channels=plot_list)
        self.layout.addLayout(self.plot_layout, 0, 2)
        self.setLayout(self.layout)
        self.sel_chan = self.plots_showing[0]
        self.update_selections()

    def add_button_clicked(self) -> None:
        button = self.sender()
        button.setEnabled(False)
        button_id = self.add_button_group.id(button)
        channel = self.config.channels[button_id]
        if self.plots_showing is None:
            total_channels = [channel]
            text = self.no_layout.itemAt(0).widget()
            self.no_layout.removeWidget(text)
            text.deleteLater()
            text.setParent(None)
        else:
            total_channels = self.plots_showing + [channel]
            self.clear_plots()
        self.plot_layout, self.full_button_group, self.close_button_group = self.win_create_plot_layer(channels = total_channels)
        self.layout.addLayout(self.plot_layout, 0, 2)
        self.sel_chan = channel
        self.update_selections()

    def swap_button_clicked(self) -> None:
        if not self.plots_showing:
            return
        button = self.sender()
        button_id = self.swap_button_group.id(button)
        channel = self.config.channels[button_id]
        selected_id = self.plots_showing.index(self.sel_chan)
        plot_list = self.plots_showing
        if (self.sel_chan in self.plots_showing) and (self.config.channels[button_id] in self.plots_showing):
            plot_id = self.plots_showing.index(channel)
            plot_list[selected_id], plot_list[plot_id] = plot_list[plot_id], plot_list[selected_id]
            self.clear_plots()
            self.plot_layout, self.full_button_group, self.close_button_group = self.win_create_plot_layer(channels = plot_list)
            self.layout.addLayout(self.plot_layout, 0, 2)
            self.sel_chan = channel
            self.update_selections()

        else:
            plot_list[selected_id] = channel
            self.clear_plots()
            self.plot_layout, self.full_button_group, self.close_button_group = self.win_create_plot_layer(channels = plot_list)
            self.layout.addLayout(self.plot_layout, 0, 2)
            self.sel_chan = channel
            self.update_selections()
         
    def canvas_clicked(self, plot_id) -> None:
        self.sel_chan = self.plots_showing[plot_id]
        self.update_selections()

    def update_selections(self, disable_swap = False) -> None:
        text = self.layout.itemAtPosition(1,2).widget()
        self.layout.removeWidget(text)
        text.deleteLater()
        text.setParent(None)
        try:
            new_label = self.sel_chan[0]
        except TypeError:
            new_label = None
        for fig, canvas in self.figures:
            canvas.remove_glow_effect()
        if self.sel_chan is not None:
            selected_id = self.plots_showing.index(self.sel_chan)
            self.figures[selected_id][1].apply_glow_effect()
        self.sel_chan_txt = QLabel(f"Selected channel: {new_label}", alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.sel_chan_txt, 1, 2)
        self.setLayout(self.layout)
        if self.expanded:
            for channel in self.config.channels:
                channel_id = self.config.channels.index(channel)
                if channel == self.sel_chan:
                    self.swap_button_group.button(channel_id).setEnabled(False)
                else:
                    self.swap_button_group.button(channel_id).setEnabled(True)

    def clear_plots(self):
        for fig, canvas in self.figures:
            plt.close(fig)
        for k in range(self.plot_layout.count()):
            item_1 = self.plot_layout.itemAt(k)
            if item_1 is None:
                self.plot_layout = None
                return
            for i in reversed(range(item_1.count())):
                item_2 = item_1.itemAtPosition(0,i)
                if isinstance(item_2.layout(), QVBoxLayout):
                    for j in reversed(range(item_2.count())):
                        item_3 = item_2.itemAt(j)
                        item_2.setParent(None)
                        widget = item_3.widget()
                        item_2.removeWidget(widget)
                        widget.deleteLater()
                        widget.setParent(None)
                else:
                    widget = item_2.widget()
                    widget.deleteLater()
                    widget.setParent(None)
        self.plots_showing = None
        
    def open_help_win(self) -> None:
        self.help_win = HelpWindow()
        self.help_win.show()

    def closeEvent(self, event) -> None:
        for fig, canvas in self.figures:
            plt.close(fig)
        if self.help_win is not None and self.help_win.isVisible():
            self.help_win.close()
        event.accept()

class SimulationWindow(QWidget): 
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Simulation")
        
        self.layout = QVBoxLayout()
        self.import_layout = QGridLayout()

        self.header_label = QLabel("Please import your data:")
        self.layout.addWidget(self.header_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.channels_trans = ["||", "⊥"]
        self.channels_reflec = ["SS", "PP", "SP", "PS"]
        self.geos = ["Transmission", "Reflection"]
        self.sources = ["Electric Dipole", "Electric Quadrupole", "Magnetic Dipole"]
        self.systems = ["Triclinic", "Monoclinic", "Orthorhombic", "Tetragonal", "Trigonal", "Hexagonal", "Cubic"]
        self.planes = ["(0 0 1)", "Rotz(90°)"]
        self.confirms = ["Geometry", "Channels", "Source", "System", "Lattice Plane"]
        self.channels = self.channels_trans + self.channels_reflec

        self.data_files = [None] * 6

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_sim)
        self.run_button.setEnabled(False)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.back_to_main)

        self.help_button = QPushButton("ⓘ")
        self.help_button.clicked.connect(self.open_help_win)

        self.data_layout, self.data_button_group, self.upload_group = self.win_create_data_layer_group()
        self.geo_layout, self.geo_button_group = self.win_create_new_layer(list_itr=self.geos,
                                                                           text_label="Geometry")
        self.chan_layout, self.chan_button_group = self.win_create_new_layer(list_itr=self.channels,
                                                                             text_label="Channels",
                                                                             exclusive=False)
        self.source_layout, self.source_button_group = self.win_create_new_layer(list_itr=self.sources,
                                                                                 text_label="Source") 
        self.sys_layout, self.sys_button_group = self.win_create_new_layer(list_itr=self.systems,
                                                                           text_label="System")
        self.lat_layout, self.lat_button_group = self.win_create_new_layer(list_itr=self.planes,
                                                                           text_label="Lattice Plane")
        
        self.config_layout = self.win_create_config_layer_group()
        self.import_layout.addLayout(self.data_layout, 0, 0)
        self.import_layout.addLayout(self.config_layout, 0, 1)
        
        self.layout.addLayout(self.import_layout)
        self.setLayout(self.layout)
        
        self.valid_channels = None
        self.help_win = None

        self.setFixedSize(self.layout.sizeHint())

    def win_create_data_layer_group(self) -> (QVBoxLayout(), QButtonGroup(), QButtonGroup()):
        layout = QVBoxLayout()
        label = QLabel("Import Data", alignment=Qt.AlignmentFlag.AlignCenter)
        sub_label = QLabel("Please select file location(s)")
        layout.addWidget(label)
        layout.addWidget(sub_label)
        
        data_button_group = QButtonGroup()
        upload_group = QButtonGroup()
        data_button_group.setExclusive(False)

        button_id = 0
        for chan in self.channels: 
            d_chan_layout = QHBoxLayout()
            box = QCheckBox(f"{chan}")
            box.clicked.connect(self.chan_button_clicked)

            text = QTextEdit(self)
            text.setReadOnly(True)
            font_metrics = QFontMetrics(text.font())
            line_height = font_metrics.lineSpacing()
            text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            text.setWordWrapMode(QTextOption.WrapMode.NoWrap)
            text.setFixedSize(300, line_height + 15)

            upload = QPushButton("...")
            upload.clicked.connect(self.upload_files)
            upload_group.addButton(upload)
            upload_group.setId(upload, button_id)

            d_chan_layout.addWidget(box)
            d_chan_layout.addWidget(text)
            d_chan_layout.addWidget(upload)

            data_button_group.addButton(box) 
            data_button_group.setId(box, button_id)

            layout.addLayout(d_chan_layout)
            button_id = button_id+1
           
        prev_label = QLabel("Preview", alignment=Qt.AlignmentFlag.AlignCenter)
        prev_img = QLabel(self)
        img_pixmap = QPixmap(f"{SCRIPT_DIR}/imgs/prev.png")
        scaled_img = img_pixmap.scaled(200, 200)
        prev_img.setPixmap(scaled_img)
        layout.addWidget(prev_label)
        layout.addWidget(prev_img, alignment=Qt.AlignmentFlag.AlignCenter)

        return layout, data_button_group, upload_group

    def win_create_new_layer(self, list_itr: List[str], 
                             text_label: str, exclusive: bool=True) -> (QVBoxLayout(), QButtonGroup()):
        layout = QVBoxLayout()
        label = QLabel(f"{text_label}")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        button_group = QButtonGroup()
        button_group.setExclusive(exclusive)
        button_id = 0
        for button_label in list_itr:
            if exclusive:
                button = QRadioButton(f"{button_label}")
            else:
                button = QCheckBox(f"{button_label}")
            layout.addWidget(button)
            button_group.addButton(button)
            button_group.setId(button, button_id)
            button_id = button_id + 1
            if text_label == "Geometry":
                button.toggled.connect(self.geo_button_clicked)
            elif text_label == "Channels":
                button.toggled.connect(self.chan_button_clicked)
            else:
                button.toggled.connect(self.test_button_groups) 
        return layout, button_group

    def win_create_config_layer_group(self) -> QGridLayout():
        layout = QGridLayout()
        layout.addLayout(self.geo_layout, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.chan_layout, 1, 0, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.source_layout, 2, 0, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.sys_layout, 3, 0, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.lat_layout, 4, 0, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.run_button, 5, 0)
        layout.addWidget(self.back_button, 6, 0)
        layout.addWidget(self.help_button, 7, 0)
        return layout

    def upload_files(self) -> None:
        button = self.sender()
        button_id = self.upload_group.id(button)
        text_box = self.data_layout.itemAt(button_id+2).layout().itemAt(1).widget()
        file = QFileDialog.getOpenFileName(self, 'Open file', '','csv files (*.csv)')
        text_box.clear()
        if not file[0]:
            self.data_files[button_id] = None
        else:
            text_box.setText(file[0]) 
            self.data_files[button_id] = file[0]
        self.test_button_groups()

    def trans_button_clicked(self) -> None:
        i = 0
        for button in self.data_button_group.buttons() + self.chan_button_group.buttons():
            if button.text() in self.channels_reflec:
                button.setChecked(False)
                button.setEnabled(False)
                if i < 6:
                    text_box = self.data_layout.itemAt(i+2).layout().itemAt(1).widget()
                    text_box.clear()
                    self.data_files[i] = None
                    self.upload_group.buttons()[i].setEnabled(False)
            else:
                button.setEnabled(True)
                if i < 6:
                   self.upload_group.buttons()[i].setEnabled(True)
            i = i + 1
        self.geo_button_group.button(0).setChecked(True)

    def refl_button_clicked(self) -> None:
        i = 0
        for button in self.data_button_group.buttons() + self.chan_button_group.buttons():
            if button.text() in self.channels_trans:
                button.setChecked(False)
                button.setEnabled(False)
                if i < 6:
                    text_box = self.data_layout.itemAt(i+2).layout().itemAt(1).widget()
                    text_box.clear()
                    self.data_files[i] = None
                    self.upload_group.buttons()[i].setEnabled(False)
            else:
                button.setEnabled(True)
                if i < 6:
                    self.upload_group.buttons()[i].setEnabled(True)
            i = i + 1
        self.geo_button_group.button(1).setChecked(True)

    def geo_button_clicked(self) -> None:
        if self.geo_button_group.checkedButton().text() == "Transmission":
            self.trans_button_clicked()
        else:
            self.refl_button_clicked()
        self.test_button_groups()

    def chan_button_clicked(self) -> None:
        button = self.sender()
        button_id = max(self.data_button_group.id(button), self.chan_button_group.id(button))
        if button.text() in self.channels_trans:
            self.trans_button_clicked()
        else:
            self.refl_button_clicked()
        if button.isChecked():
            self.data_button_group.button(button_id).setChecked(True)
            self.chan_button_group.button(button_id).setChecked(True)
        else:
            self.data_button_group.button(button_id).setChecked(False)
            self.chan_button_group.button(button_id).setChecked(False)
        self.test_button_groups()

    def test_button_groups(self) -> None:
        button_groups = [self.data_button_group, self.geo_button_group, self.chan_button_group, 
                         self.source_button_group, self.sys_button_group, self.lat_button_group]
        if all(data is None for data in self.data_files):
            self.run_button.setEnabled(False)
            return
        if self.geo_button_group.button(0).isChecked():
            selected_channels = [button.text() for button in self.chan_button_group.buttons() if button.isChecked()]
            self.valid_channels = [
                self.channels_trans[i] for i in range(2) 
                if (self.data_files[i] is not None and self.channels_trans[i] in selected_channels)
            ]
            if not self.valid_channels:
                self.run_button.setEnabled(False)
                return
        elif self.geo_button_group.button(1).isChecked():
            selected_channels = [button.text() for button in self.chan_button_group.buttons() if button.isChecked()]
            self.valid_channels = [
                self.channels_reflec[i] for i in range(4) 
                if (self.data_files[i+2] is not None and self.channels_reflec[i] in selected_channels)
            ]
            if not self.valid_channels:
                self.run_button.setEnabled(False)
                return
        else:
            self.run_button.setEnabled(False)
            self.valid_channels = None
            return
        if (all(button_group.checkedButton() is not None for button_group in button_groups) 
                and all(data is not None for data in self.data_files) == False):
            self.run_button.setEnabled(True)
        else:
           self.run_button.setEnabled(False)

    def run_sim(self) -> None:
        self.run_button.setEnabled(False)
        config = self.get_current_inputs()
        if isinstance(config, SimInputConfig):
            self.config_win = SimulationResults(config=config)
            self.config_win.show()
        else:
            self.error_win(message=config)
        self.run_button.setEnabled(True)  

    def get_current_inputs(self) -> Union[SimInputConfig, str]:
        config = SimInputConfig()

        if all(data is None for data in self.data_files):
            return "No data files uploaded"
        config.geometry = convert_to_config_str(self.geo_button_group.checkedButton().text())
        if self.geo_button_group.checkedButton().text() == "Transmission":
            combined_list = [
                (convert_to_config_str(self.channels_trans[i]), read_data(self.data_files[i])) 
                for i in range(2) if (self.channels_trans[i] in self.valid_channels)
            ]
        else:
            combined_list = [
                (convert_to_config_str(self.channels_reflec[i]), read_data(self.data_files[i+2]))
                for i in range(4) if (self.channels_reflec[i] in self.valid_channels)
            ]
    
        no_data = [channel for channel, data in combined_list if data == "No data"]
        too_many_columns = [channel for channel, data in combined_list if data == "Too many columns"]
        too_few_columns = [channel for channel, data in combined_list if data == "Too few columns"]
        incorrect_types = [channel for channel, data in combined_list if data == "Incorrect dtype"]
        missing_types = [channel for channel, data in combined_list if data == "Missing data elem"]

        if len(no_data) > 0:
            return f"No data in uploaded file for channel(s): {', '.join(no_data)}"
        elif len(too_many_columns) > 0:
            return f"Too many data columns in uploaded file for channel(s): {', '.join(too_many_columns)}"
        elif len(too_few_columns) > 0:
            return f"Missing required data columns in uploaded file for channel(s): {', '.join(no_data)}"
        elif len(incorrect_types) > 0:
            return f"Incorrect data types for data in uploaded file for channel(s): {', '.join(incorrect_types)}"
        elif len(missing_types) > 0:
            return f"Missing data elements for data in uploaded file for channel(s): {', '.join(missing_types)}"
 
        config.channels = combined_list
        config.source = convert_to_config_str(self.source_button_group.checkedButton().text())
        config.sys = convert_to_config_str(self.sys_button_group.checkedButton().text())
        config.plane = convert_to_config_str(self.lat_button_group.checkedButton().text())

        return config

    def error_win(self, message: str) -> None:
        self.error = QMessageBox()
        self.error.setIcon(QMessageBox.Icon.Critical)
        self.error.setWindowTitle("Unable to Continue")
        self.error.setText(f"Error: \'{message}\'.\nPlease try again.")
        self.error.show()

    def back_to_main(self) -> None:
        self.win = MainWindow()
        self.win.show()
        self.close()

    def open_help_win(self) -> None:
        self.help_win = HelpWindow()
        self.help_win.show()

    def closeEvent(self, event) -> None:
        if self.help_win is not None and self.help_win.isVisible():
            self.help_win.close()
        event.accept()

class FittingWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fitting")

class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent) 
        self.setWindowTitle("SHG")     

        self.layout = QGridLayout()

        self.fit_label = QLabel("Fitting")
        self.fit_desc = QLabel("Description")
        self.fit_button = QPushButton("Select")
        self.fit_button.clicked.connect(self.show_fitting_window)
        self.layout.addWidget(self.fit_label, 0, 0)
        self.layout.addWidget(self.fit_desc, 1, 0)
        self.layout.addWidget(self.fit_button, 2, 0)

        self.sim_label = QLabel("Simulation")
        self.sim_desc = QLabel("Description")
        self.sim_button = QPushButton(text="Select", parent=self)
        self.sim_button.clicked.connect(self.show_simulation_window)
        self.layout.addWidget(self.sim_label, 0, 1)
        self.layout.addWidget(self.sim_desc, 1, 1)
        self.layout.addWidget(self.sim_button, 2, 1)

        self.set_layout = QWidget()
        self.set_layout.setLayout(self.layout)
        self.setCentralWidget(self.set_layout)

        self.setFixedSize(self.layout.sizeHint())
        
    def show_simulation_window(self) -> None:
        self.win = SimulationWindow()
        self.win.show()
        self.close()

    def show_fitting_window(self) -> None:
        self.win = FittingWindow()
        self.win.show()
        #self.close()

def startup_mac(): 
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
