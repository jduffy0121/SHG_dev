import sys
import pathlib
import os
import pandas as pd
import markdown
from typing import List, Union, Tuple
from dataclasses import dataclass, field
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QGridLayout, QLabel, 
    QHBoxLayout, QVBoxLayout, QCheckBox, QFileDialog, QMessageBox, 
    QRadioButton, QButtonGroup, QTextEdit, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFontMetrics, QTextOption

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()

@dataclass
class SimInputConfig:
    geometry: str = 'trans'
    channels: List[Tuple[str, List[Tuple[float, float]]]] = field(default_factory=lambda: [('parallel', None)])
    source: str = 'e_dip'
    sys: str = 'triclinic'
    plane: str = '001' 

class HelpWindow(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Infromation")
        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(False)

        self.background_txt = QTextEdit()
        self.sim_txt = QTextEdit()
        self.about_txt = QTextEdit()
        self.background_txt.setReadOnly(True)
        self.sim_txt.setReadOnly(True)
        self.about_txt.setReadOnly(True)
        self.background_txt.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.sim_txt.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.about_txt.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.set_txt_files()

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

class SimulationResults(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Simulation")
        self.layout = QGridLayout()
        self.label = QLabel("Eventually, we will do some cool physics magic and show something here")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

class SimulationWindow(QWidget): 
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Simulation")
        
        self.layout = QVBoxLayout()
        self.import_layout = QGridLayout()

        self.header_label = QLabel("Please import your data:")
        self.layout.addWidget(self.header_label)

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

        self.help_button = QPushButton("Information")
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
        self.confirm_layout, self.confirm_button_group = self.win_create_new_layer(list_itr=self.confirms,
                                                                                   text_label="Confirmation", 
                                                                                   exclusive=False)
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
        label = QLabel("Import Data")
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
           
        prev_label = QLabel("Preview")
        prev_img = QLabel(self)
        img_pixmap = QPixmap(f"{SCRIPT_DIR}/imgs/prev.png")
        scaled_img = img_pixmap.scaled(200, 200)
        prev_img.setPixmap(scaled_img)
        layout.addWidget(prev_label)
        layout.addWidget(prev_img)

        return layout, data_button_group, upload_group

    def win_create_new_layer(self, list_itr: List[str], 
                             text_label: str, exclusive: bool=True) -> (QVBoxLayout(), QButtonGroup()):
        layout = QVBoxLayout()
        label = QLabel(f"{text_label}")
        layout.addWidget(label)
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
        layout.addLayout(self.chan_layout, 0, 1, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.source_layout, 0, 2, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.sys_layout, 1, 0, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.lat_layout, 1, 1, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self.confirm_layout, 1, 2, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.run_button, 2, 2)
        layout.addWidget(self.back_button, 2, 1)
        layout.addWidget(self.help_button, 2, 0)
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
        elif self.geo_button_group.checkedButton().text() == "Reflection":
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
            self.results_win = SimulationResults()
            self.results_win.show()
            print(config)
        else:
            self.error_win(message=config)
        self.run_button.setEnabled(True)  

    def read_data(self, data_path: pathlib.Path) -> Union[List[Tuple[float, float]], str]: 
        try:
            df = pd.read_csv(data_path) 
            if df.shape[1] > 2:
                return "Too many columns"
            elif df.shape[1] < 2:
                return "Too few columns"
            data_list = list(zip(df.iloc[:, 0], df.iloc[:, 1]))
            for (x,y) in data_list:
                try:
                    if isinstance(float(x), float) == False or isinstance(float(y), float) == False:
                        return "Incorrect dtype"
                except ValueError:
                    return "Incorrect dtype"
            return list(zip(df.iloc[:, 0], df.iloc[:, 1]))             
        except pd.errors.EmptyDataError:
            return "No data"
    
    def convert_to_config_str(self, gui_name: str) -> str:
        name_scheme = {'||': 'parallel', '⊥': 'perpendicular', 'Transmission': 'trans', 'Reflection': 'refl', 
                       'Electric Dipole': 'e_dip', 'Electric Quadrupole': 'e_quad', 'Magnetic Dipole': 'm_dip', 
                       '(0 0 1)': '001','Rotz(90°)': 'rotz90'}
        try:
            return name_scheme[f'{gui_name}']
        except KeyError:
            return gui_name.lower()

    def get_current_inputs(self) -> Union[SimInputConfig, str]:
        config = SimInputConfig()

        if all(data is None for data in self.data_files):
            return "No data files uploaded"
        try:
            config.geometry = self.convert_to_config_str(self.geo_button_group.checkedButton().text())
        except AttributeError:
            return "Missing geometry selection"
        if self.geo_button_group.checkedButton().text() == "Transmission":
            combined_list = [
                (self.convert_to_config_str(self.channels_trans[i]), self.read_data(self.data_files[i])) 
                for i in range(2) if (self.channels_trans[i] in self.valid_channels)
            ]
        else:
            combined_list = [
                (self.convert_to_config_str(self.channels_reflec[i]), self.read_data(self.data_files[i+2]))
                for i in range(4) if (self.channels_reflec[i] in self.valid_channels)
            ]
    
        no_data = [channel for channel, data in combined_list if data == "No data"]
        too_many_columns = [channel for channel, data in combined_list if data == "Too many columns"]
        too_few_columns = [channel for channel, data in combined_list if data == "Too few columns"]
        incorrect_types = [channel for channel, data in combined_list if data == "Incorrect dtype"]

        if len(no_data) > 0:
            return f"No data in uploaded file(s) for channel(s): {', '.join(no_data)}"
        elif len(too_many_columns) > 0:
            return f"Too many data columns in uploaded file(s) for channel(s): {', '.join(too_many_columns)}"
        elif len(too_few_columns) > 0:
            return f"Missing required data columns in uploaded file(s) for channel(s): {', '.join(no_data)}"
        elif len(incorrect_types) > 0:
            return f"Incorrect data types for data in uploaded file(s) for channel(s): {', '.join(incorrect_types)}"
        
        config.channels = combined_list
        config.source = self.convert_to_config_str(self.source_button_group.checkedButton().text())
        config.sys = self.convert_to_config_str(self.sys_button_group.checkedButton().text())
        config.plane = self.convert_to_config_str(self.lat_button_group.checkedButton().text())

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
