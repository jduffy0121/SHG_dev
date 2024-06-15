import sys
import pathlib
from typing import List, Union, Tuple
from dataclasses import dataclass, field
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QGridLayout, QLabel, 
    QHBoxLayout, QVBoxLayout, QCheckBox, QFileDialog, QLineEdit, QMessageBox, 
    QRadioButton, QButtonGroup, QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFontMetrics, QTextOption

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()

@dataclass
class SimInputConfig:
    geometry: str = 'trans'                                                                         #['trans', 'refl']
    channels: List[Tuple[str, pathlib.Path]] = field(default_factory=lambda: [('para', None)])      #[('channel', 'data_for_this_channel'), ...]
    source: str = 'e_dip'                                                                           #['e_dip', 'e_quad', 'm_dip']
    sys: str = 'triclinic'                                                                          #['triclinic', 'monoclinic', 'orthorhombic', 'tetragonal', 'trigonal', 'hexagonal', 'cubic']
    plane: str = '001'                                                                              #['001', 'rotz90']

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

        self.data_layout = QVBoxLayout()
        self.geo_layout = QVBoxLayout()
        self.chan_layout = QVBoxLayout()
        self.source_layout = QVBoxLayout()
        self.sys_layout = QVBoxLayout()
        self.lat_layout = QVBoxLayout()
        self.confirm_layout = QVBoxLayout()

        self.header_label = QLabel("Please import your data:")
        self.layout.addWidget(self.header_label)
        
        self.data_label = QLabel("Import Data")
        self.data_sub_label = QLabel("Please select file location(s)")
        self.data_layout.addWidget(self.data_label)
        self.data_layout.addWidget(self.data_sub_label)

        self.geo_label = QLabel("Geometry")
        self.geo_layout.addWidget(self.geo_label)

        self.chan_label = QLabel("Channels")
        self.chan_layout.addWidget(self.chan_label)

        self.source_label = QLabel("Source")
        self.source_layout.addWidget(self.source_label)

        self.sys_label = QLabel("System")
        self.sys_layout.addWidget(self.sys_label)

        self.lat_label = QLabel("Lattice Plane")
        self.lat_layout.addWidget(self.lat_label)

        self.confirm_label = QLabel("Confirmation")
        self.confirm_layout.addWidget(self.confirm_label)

        self.channels_trans = ["||", "⊥"]
        self.channels_reflec = ["SS", "PP", "SP", "PS"]
        self.channels = self.channels_trans + self.channels_reflec
        self.geos = ["Transmission", "Reflection"]
        self.sources = ["Electric Dipole", "Electric Quadrupole", "Magnetic Dipole"]
        self.systems = ["Triclinic", "Monoclinic", "Orthorhombic", "Tetragonal", "Trigonal", "Hexagonal", "Cubic"]
        self.planes = ["(0 0 1)", "Rotz(90°)"]
        self.confirms = ["Geometry", "Channels", "Source", "System", "Lattice Plane"]
       
        self.data_button_group = QButtonGroup()
        self.upload_group = QButtonGroup()
        self.data_button_group.setExclusive(False)
        self.data_files = [None] * 6
        button_id = 0
        for chan in self.channels: 
            self.d_chan_layout = QHBoxLayout()
            self.box = QCheckBox(f"{chan}")

            self.text = QTextEdit(self)
            self.text.setReadOnly(True)
            self.font_metrics = QFontMetrics(self.text.font())
            self.line_height = self.font_metrics.lineSpacing()
            self.text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.text.setWordWrapMode(QTextOption.WrapMode.NoWrap)
            self.text.setFixedSize(300, self.line_height + 15)

            self.upload = QPushButton("...")
            self.upload.clicked.connect(self.upload_files)
            self.upload_group.addButton(self.upload)
            self.upload_group.setId(self.upload, button_id)

            self.d_chan_layout.addWidget(self.box)
            self.d_chan_layout.addWidget(self.text)
            self.d_chan_layout.addWidget(self.upload)

            self.data_button_group.addButton(self.box) 
            self.data_button_group.setId(self.box, button_id)

            self.data_layout.addLayout(self.d_chan_layout)
            button_id = button_id+1
           
        self.prev_label = QLabel("Preview")
        self.prev_img = QLabel(self)
        self.img_pixmap = QPixmap(f"{SCRIPT_DIR}/imgs/prev.png")
        self.scaled_img = self.img_pixmap.scaled(200, 200)
        self.prev_img.setPixmap(self.scaled_img)
        self.data_layout.addWidget(self.prev_label)
        self.data_layout.addWidget(self.prev_img)

        self.geo_button_group = QButtonGroup()
        self.geo_button_group.setExclusive(True)
        button_id = 0
        for geo in self.geos:
            self.box = QRadioButton(f"{geo}")
            self.geo_layout.addWidget(self.box)
            self.geo_button_group.addButton(self.box)
            self.geo_button_group.setId(self.box, button_id)
            self.box.toggled.connect(self.geo_button_clicked)
            button_id = button_id + 1
        
        self.chan_button_group = QButtonGroup()
        self.chan_button_group.setExclusive(False)
        button_id = 0
        for chan in self.channels:
            self.box = QCheckBox(f"{chan}")
            self.chan_layout.addWidget(self.box)
            self.chan_button_group.addButton(self.box)
            self.chan_button_group.setId(self.box, button_id)
            button_id = button_id + 1
        
        self.source_button_group = QButtonGroup()
        self.source_button_group.setExclusive(True)
        button_id = 0
        for source in self.sources:
            self.box = QRadioButton(f"{source}")
            self.source_layout.addWidget(self.box)
            self.source_button_group.addButton(self.box)
            self.source_button_group.setId(self.box, button_id)
            button_id = button_id + 1
        
        self.sys_button_group = QButtonGroup()
        self.sys_button_group.setExclusive(True)
        button_id = 0
        for sys in self.systems:
            self.box = QRadioButton(f"{sys}")
            self.sys_layout.addWidget(self.box)
            self.sys_button_group.addButton(self.box)
            self.sys_button_group.setId(self.box, button_id)
            button_id = button_id + 1
        
        self.lat_button_group = QButtonGroup()
        self.lat_button_group.setExclusive(True)
        button_id = 0
        for plane in self.planes:
            self.box = QRadioButton(f"{plane}")
            self.lat_layout.addWidget(self.box)
            self.lat_button_group.addButton(self.box)
            self.lat_button_group.setId(self.box, button_id)
            button_id = button_id + 1

        self.confirm_button_group = QButtonGroup()
        self.confirm_button_group.setExclusive(False)
        button_id = 0
        for confirm in self.confirms:
            self.box = QCheckBox(f"{confirm}")
            self.confirm_layout.addWidget(self.box)
            self.confirm_button_group.addButton(self.box)
            self.confirm_button_group.setId(self.box, button_id)
            self.box.toggled.connect(self.confirm_button_clicked)
            button_id = button_id + 1
        
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_sim)
        self.run_button.setEnabled(False)

        self.config_layout = QGridLayout()

        self.config_layout.addLayout(self.geo_layout, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
        self.config_layout.addLayout(self.chan_layout, 0, 1, alignment=Qt.AlignmentFlag.AlignTop)
        self.config_layout.addLayout(self.source_layout, 0, 2, alignment=Qt.AlignmentFlag.AlignTop)
        self.config_layout.addLayout(self.sys_layout, 1, 0, alignment=Qt.AlignmentFlag.AlignTop)
        self.config_layout.addLayout(self.lat_layout, 1, 1, alignment=Qt.AlignmentFlag.AlignTop)
        self.config_layout.addLayout(self.confirm_layout, 1, 2, alignment=Qt.AlignmentFlag.AlignTop)
        self.config_layout.addWidget(self.run_button, 2, 2)
        
        self.import_layout.addLayout(self.data_layout, 0, 0)
        self.import_layout.addLayout(self.config_layout, 0, 1)
        
        self.layout.addLayout(self.import_layout)

        self.setLayout(self.layout)

        self.setFixedSize(self.layout.sizeHint())
    
    def upload_files(self) -> None:
        button = self.sender()
        button_id = self.upload_group.id(button)
        text_box = self.data_layout.itemAt(button_id+2).layout().itemAt(1).widget()
        file = QFileDialog.getOpenFileNames(self, 'Open file')[0]
        text_box.clear()
        try:
            text_box.setText(file[0]) 
            self.data_files[button_id] = file[0]
        except IndexError:
            self.data_files[button_id] = None

    def geo_button_clicked(self) -> None:
        total_itr_buttons = self.data_button_group.buttons() + self.chan_button_group.buttons()
        i = 0
        for button in total_itr_buttons:
            if self.geo_button_group.checkedButton().text() == "Transmission":
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
            else:
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
            i = i+1
            
    def confirm_button_clicked(self) -> None:
        if all(i.isChecked() is True for i in self.confirm_button_group.buttons()):
            self.run_button.setEnabled(True)
            return
        self.run_button.setEnabled(False)

    def run_sim(self) -> None:
        self.run_button.setEnabled(False)
        config = self.get_current_inputs()
        if isinstance(config, SimInputConfig):
            self.win = SimulationResults()
            self.win.show()
            print(config)
        else:
            self.error_win(message=config)
        self.run_button.setEnabled(True)
    
    def valid_data_upload(self, config: SimInputConfig) -> bool:
        return True

    def convert_to_config_str(self, gui_name: str) -> str:
        name_scheme = {'||': 'para', '⊥': 'perp', 'Transmission': 'trans', 'Reflection': 'refl', 
                       'Electric Dipole': 'e_dip', 'Electric Quadrupole': 'e_quad', 'Magnetic Dipole': 'm_dip', 
                       '(0 0 1)': '001','Rotz(90°)': 'rotz90'}
        try:
            return name_scheme[f'{gui_name}']
        except KeyError:
            return gui_name.lower()

    def get_current_inputs(self) -> Union[SimInputConfig, str]:
        config = SimInputConfig()
        if all(i is None for i in self.data_files):
            return "No data files uploaded"
        selected_channels = [i.text() for i in self.chan_button_group.buttons() if i.isChecked()]
        selected_data = [i.text() for i in self.data_button_group.buttons() if i.isChecked()]
        valid_channels = [i for i in selected_data if i in selected_channels]
        if self.geo_button_group.checkedButton().text() == "Transmission":
            combined_list = [(self.convert_to_config_str(self.channels_trans[i]), self.data_files[i]) for i in range(2) 
                if (self.data_files[i] is not None and self.channels_trans[i] in valid_channels)]
        else:
            combined_list = [(self.convert_to_config_str(self.channels_reflec[i]), self.data_files[i+2]) for i in range(4) 
                if (self.data_files[i+2] is not None and self.channels_reflec[i] in valid_channels)]
        if not combined_list:
            return "Missing data and/or channel selection"
        config.channels = combined_list
        try:
            config.geometry = self.convert_to_config_str(self.geo_button_group.checkedButton().text())
        except AttributeError:
            return "Missing geometry selection"
        try:
            config.source = self.convert_to_config_str(self.source_button_group.checkedButton().text())
        except AttributeError:
            return "Missing source selection"
        try:
            config.sys = self.convert_to_config_str(self.sys_button_group.checkedButton().text())
        except AttributeError:
            return "Missing system selection"
        try:
            config.plane = self.convert_to_config_str(self.lat_button_group.checkedButton().text())
        except AttributeError:
            return "Missing lattice plane selection"
        if self.valid_data_upload(config=config) == False:
            return "Unable to read data"
        return config

    def error_win(self, message: str) -> None:
        self.error = QMessageBox()
        self.error.setIcon(QMessageBox.Icon.Critical)
        self.error.setWindowTitle("Unable to Continue")
        self.error.setText(f"Error: {message}.\nPlease try again.")
        self.error.show()

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

    def show_fitting_window(self) -> None:
        self.win = FittingWindow()
        self.win.show()

def startup_mac(): 
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
