import sys
import os
import pathlib
import pkg_resources
from itertools import chain
import matplotlib.pyplot as plt
from typing import List, Union, Tuple
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar, FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import Qt, QLoggingCategory, pyqtSignal
from PyQt6.QtGui import QPixmap, QFontMetrics, QTextOption, QDesktopServices, QFontDatabase
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout, QLabel, QTableWidgetItem, QTableWidget, QComboBox,
    QHBoxLayout, QVBoxLayout, QCheckBox, QFileDialog, QMessageBox, QRadioButton, QButtonGroup, QTextEdit, 
    QTabWidget, QTextBrowser, QGroupBox, QStackedLayout, QScrollArea
)

from .utils import *
from .gui_classes import *
from .data_fitting import *
from .gui_html_boxes import *
from .gui_layouts import *
from .check_repo_files import *

REPO_DIR = pathlib.Path(__file__).parent.parent.resolve()
OS_CONFIG = OSConfig()

class AdditionalWindow(QWidget):
    def __init__(self, win_type, parent=None) -> None: #Init the window
        super().__init__(parent)

        if win_type == 'more':
            self.setWindowTitle('More Information')
            self.layout = more_window_layout()
            self.width = 565
            self.height = 565
            self.set_button_clicks(widget_type='Tabs')

        elif win_type == 'data help':
            self.setWindowTitle('Data Format')
            self.layout = data_help_layout()
            self.width = 350 
            self.height = 350
            self.set_button_clicks(widget_type='Single')

        elif win_type == 'visual':
            self.setWindowTitle('Visualizations')
            self.layout = visuals_win_layout()
            self.width = 565
            self.height = 565
            self.set_button_clicks(widget_type='Single')

        elif win_type == 'point group':
            self.setWindowTitle('Point Groups')
            self.layout = point_group_win_layout()
            self.width = 565
            self.height = 565
            self.set_button_clicks(widget_type='Single')

        elif win_type == 'add crystals':
            self.setWindowTitle('Searching the Database')
            self.layout = crystals_win_layout()
            self.width = 565
            self.height = 565
            self.set_button_clicks(widget_type='Single')

        self.setLayout(self.layout)
        self.setFixedSize(self.width, self.height)

    def set_button_clicks(self, widget_type) -> None:
        if widget_type == 'Single':
            self.layout.itemAt(0).widget().anchorClicked.connect(self.url_click)
        elif widget_type == 'Tabs':
            for i in range(self.layout.itemAt(0).widget().count()):
                self.layout.itemAt(0).widget().widget(i).anchorClicked.connect(self.url_click)
    
    def url_click(self, url) -> None:
        QDesktopServices.openUrl(url)

class PlotWindow(QWidget):
    def __init__(self, channel: list, config, point_groups=None, data_upload=None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f'{channel}')
        self.config = config
        if not data_upload:
            self.fits = [point_group for point_group in point_groups if point_group.active == True and point_group.channel == channel]
            self.fig, self.ax = polar_plot(title=channel, data=self.config.data[channel], 
                                       width=OS_CONFIG.full_plt_len, height=OS_CONFIG.full_plt_len, 
                                       dpi=OS_CONFIG.full_plt_dpi, fits=self.fits)
        else:
            self.fig, self.ax = polar_plot(title=channel, data=self.config, 
                                       width=OS_CONFIG.full_plt_len, height=OS_CONFIG.full_plt_len, 
                                       dpi=OS_CONFIG.full_plt_dpi)

        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def closeEvent(self, event) -> None:
        plt.close(self.fig) 
        event.accept()
        
class FitResults(QWidget):
    def __init__(self, config, parent=None) -> None: #Init the window
        super().__init__(parent)
        self.setWindowTitle("Fit Results")
        self.manager = FitManager()
        self.config = config
        self.layout, self.swap_button_group, self.add_button_group = fit_res_create_layout(OS_CONFIG, config)
        self.full_button_group = None
        self.close_button_group = None
        self.set_button_clicks()
        self.setLayout(self.layout)
        self.setFixedSize(self.layout.sizeHint())

        self.group_win = None
        self.visuals_win = None
        self.plot_win = None

    def set_button_clicks(self) -> None:
        self.layout.itemAtPosition(2,0).widget().clicked.connect(self.back_to_input)
        for i in range(2):
            self.layout.itemAtPosition(1,1).widget(i).layout().itemAt(0).widget().layout().itemAt(0).widget().clicked.connect(self.visual_button_clicked)
        for i in range(2):
            self.layout.itemAtPosition(1,1).widget(i).layout().itemAt(0).widget().layout().itemAt(1).widget().clicked.connect(self.download_button_clicked)
        for i in range(2):
            self.layout.itemAtPosition(1,1).widget(i).layout().itemAt(0).widget().layout().itemAt(2).widget().clicked.connect(self.point_group_button_clicked)
        for i in range(2):
            self.layout.itemAtPosition(1,1).widget(i).layout().itemAt(0).widget().layout().itemAt(3).widget().clicked.connect(self.reset_button_clicked)
        for i in range(2):
            self.layout.itemAtPosition(1,1).widget(i).layout().itemAt(0).widget().layout().itemAt(4).widget().clicked.connect(self.toggle_expand)
        for button in self.add_button_group.buttons():
            button.clicked.connect(self.add_button_clicked)
        for button in self.swap_button_group.buttons():
            button.clicked.connect(self.swap_button_clicked)

    def toggle_expand(self) -> None:
        current_index = self.layout.itemAtPosition(1,1).currentIndex()
        new_index = 1 - current_index
        self.layout.itemAtPosition(1,1).setCurrentIndex(new_index)

    def point_group_button_clicked(self) -> None:
        self.group_win = AdditionalWindow(win_type = 'point group')
        self.group_win.show()

    def download_button_clicked(self) -> None:
        pass

    def visual_button_clicked(self) -> None:
        self.visuals_win = AdditionalWindow(win_type = 'visual')
        self.visuals_win.show()

    def reset_button_clicked(self) -> None:
        pass

    def add_button_clicked(self) -> None:
        button = self.sender()
        button.setEnabled(False)
        button_id = self.add_button_group.id(button)
        channel = self.config.channels[button_id]
        if self.manager.plots_showing == []:
            self.manager.plots_showing.append(channel)
        self.generate_plots()

    def swap_button_clicked(self) -> None:
        pass

    def close_button_clicked(self) -> None:
        pass

    def full_button_clicked(self) -> None:
        button = self.sender()
        button_id = self.full_button_group.id(button)
        channel = self.manager.plots_showing[button_id]
        self.plot_win = PlotWindow(channel=channel, config=self.config, point_groups=self.manager.point_groups)
        self.plot_win.show()
    
    def generate_plots(self):
        layout = QVBoxLayout()
        self.full_button_group = QButtonGroup()
        self.close_button_group = QButtonGroup()

        plot_id = 0
        self.manager.figures = []
        for channel in self.config.channels:
            fits = [point_group for point_group in self.manager.point_groups if point_group.active == True and point_group.channel == channel]
            channel_layout = QGridLayout()
            sub_layout = QVBoxLayout()
            enlarge_button = QPushButton('⤢')
            enlarge_button.clicked.connect(self.full_button_clicked)
            close_button = QPushButton('✕')
            enlarge_button.setToolTip('Display in a new window')
            close_button.setToolTip('Close plot')
            close_button.setFixedSize(20,20)
            enlarge_button.setFixedSize(20,20)
            sub_layout.addWidget(enlarge_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            sub_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            sub_layout.setSpacing(3)

            self.full_button_group.addButton(enlarge_button)
            self.full_button_group.setId(enlarge_button, plot_id)
            self.close_button_group.addButton(close_button)
            self.close_button_group.setId(close_button, plot_id)
            fig, ax = polar_plot(title=channel, data=self.config.data[channel], 
                         width=(OS_CONFIG.fit_res_mini_plt_r/OS_CONFIG.fit_res_mini_plt_dpi) * 2, 
                         height=(OS_CONFIG.fit_res_mini_plt_r/OS_CONFIG.fit_res_mini_plt_dpi) * 2, 
                         dpi=OS_CONFIG.fit_res_mini_plt_dpi, fits=fits)
            canvas = ClickableFigureCanvas(figure=fig, plot_id=plot_id, radius=OS_CONFIG.fit_res_mini_plt_r)
            self.manager.figures.append((fig, canvas))
            canvas.setFixedSize(OS_CONFIG.fit_res_mini_plt_r * 2, OS_CONFIG.fit_res_mini_plt_r * 2)

            channel_layout.addWidget(canvas, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)
            channel_layout.addLayout(sub_layout, 0, 0, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            group_box = QGroupBox()
            group_box.setFixedSize(350, 325)
            group_box.setLayout(channel_layout)
            layout.addWidget(group_box, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        widget = PlotWidget()
        widget.setLayout(layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(widget)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.layout.itemAtPosition(1,2).widget().layout().itemAt(0).widget().deleteLater()
        self.layout.itemAtPosition(1,2).widget().layout().itemAt(0).widget().setParent(None)
        self.layout.itemAtPosition(1,2).widget().layout().addWidget(scroll_area)
        self.setLayout(self.layout)

    def clear_plots() -> None:
        pass

    def update_selection() -> None:
        pass
        
    def back_to_input(self) -> None:
        self.win = FittingInput(config=self.config)
        self.win.show()
        self.close()

    def closeEvent(self, event) -> None:
        if self.manager.figures:
            for fig, canvas in self.manager.figures:
                plt.close(fig) 
        if self.plot_win is not None and self.plot_win:
            self.plot_win.close()
        if self.group_win is not None and self.group_win:
            self.group_win.close()
        if self.visuals_win is not None and self.visuals_win:
            self.visuals_win.close()
        event.accept()

class FittingInput(QWidget):
    def __init__(self, config=None, parent=None) -> None: #Init the window
        super().__init__(parent)
        self.setWindowTitle("Data Import")
        self.manager = FitInputManager()
        (self.layout, self.data_button_group, self.upload_button_group, self.full_button_group, self.geo_button_group, 
            self.chan_button_group, self.source_button_group, self.system_button_group, 
            self.planes_button_group) = fit_inp_create_layout(OS_CONFIG)
        self.set_button_clicks()
        self.setLayout(self.layout)
        self.setFixedSize(self.layout.sizeHint())
        
        self.additional_win = None
        self.plot_win = None

        self.config = config
        if self.config:
            self.set_config()
 
    def set_button_clicks(self) -> None: #Sets all buttons and button groups to the proper methods
        self.layout.itemAtPosition(5,0).widget().clicked.connect(self.back_to_main)
        self.layout.itemAtPosition(5,2).widget().clicked.connect(self.run_button_clicked)
        self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(2,0).widget().clicked.connect(self.show_help_win)
        self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(2,1).widget().clicked.connect(self.toggle_column_header)
        for button in list(self.chan_button_group.buttons() + self.data_button_group.buttons()):
            if button.text().rstrip() in ["||", "⊥"]:
                button.clicked.connect(self.trans_button_clicked)
            else:
                button.clicked.connect(self.refl_button_clicked)
        for button in self.geo_button_group.buttons():
            if button.text() == "Transmission":
                button.clicked.connect(self.trans_button_clicked)
            else:
                button.clicked.connect(self.refl_button_clicked)
        for button in list(self.source_button_group.buttons() + self.system_button_group.buttons() + self.planes_button_group.buttons()):
            button.clicked.connect(self.config_button_clicked)
        for button in self.upload_button_group.buttons():
            button.clicked.connect(self.upload_file)
        for button in self.full_button_group.buttons():
            button.clicked.connect(self.plot_data)

    def set_config(self) -> None:
        self.manager.data_files = self.config.data_files
        self.manager.column_headers = self.config.column_headers
        for button in self.geo_button_group.buttons():
            if convert_to_config_str(button.text()) == self.config.geometry:
                button.setChecked(True)
        for button in self.chan_button_group.buttons():
            if convert_to_config_str(button.text()) in self.config.channels:
                button.setChecked(True)
        for button in self.data_button_group.buttons():
            if convert_to_config_str(button.text().rstrip()) in self.config.channels:
                button.setChecked(True)
        for button in self.source_button_group.buttons():
            if convert_to_config_str(button.text()) == self.config.source:
                button.setChecked(True)
        for button in self.system_button_group.buttons():
            if convert_to_config_str(button.text()) == self.config.sys:
                button.setChecked(True)
        for button in self.planes_button_group.buttons():
            if convert_to_config_str(button.text()) == self.config.plane:
                button.setChecked(True)        
        if self.config.geometry == 'trans':
            self.trans_button_clicked()
            for i in range(2):
                if self.config.data_files[i]:
                    self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(1,0).itemAt(i).itemAt(1).widget().setText(self.config.data_files[i])
                    self.full_button_group.button(i).setEnabled(True)
        else:
            self.refl_button_clicked()
            for i in range(4):
                if self.config.data_files[i+2]:
                    self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(1,0).itemAt(i+2).itemAt(1).widget().setText(self.config.data_files[i+2])
                    self.full_button_group.button(i+2).setEnabled(True)
        if self.config.column_headers:
            self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(2,1).widget().setChecked(True)

    def trans_button_clicked(self) -> None: #Called when any button in chan/data/geo button group click and the corresponding chan is trans
        button_sender = self.sender()
        #Gets id corresponding to the senders's actual group (-1 will be returned for the incorrect group)
        button_id = max(self.data_button_group.id(button_sender), self.chan_button_group.id(button_sender))
        i = 0
        for button in list(self.chan_button_group.buttons() + self.data_button_group.buttons()):
            if button.text().rstrip() in ["||", "⊥"]: #Enable all buttons corresponding to trans
                button.setEnabled(True)
                if i < 6: #Iterates through all 6 layers of file uploader
                    self.upload_button_group.button(i).setEnabled(True)
            else: #Disable all data upload/buttons corresponding to refl
                button.setChecked(False)
                button.setEnabled(False)
                if i < 6: #Iterates through all 6 layers of file uploader, clearing all refl buttons/data
                    self.upload_button_group.button(i).setEnabled(False)
                    self.full_button_group.button(i).setEnabled(False)
                    self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(1,0).itemAt(i).itemAt(1).widget().clear()
                    self.manager.data_files[i] = None
            #If the sender exist in chan/data button group, then we set both corresponding chan in each group to the same toggle
            if button == button_sender and button.isChecked():
                self.data_button_group.button(button_id).setChecked(True)
                self.chan_button_group.button(button_id).setChecked(True)
            elif button == button_sender:
                self.data_button_group.button(button_id).setChecked(False)
                self.chan_button_group.button(button_id).setChecked(False)
            i = i + 1
        self.geo_button_group.button(0).setChecked(True)
        self.config_button_clicked()

    def refl_button_clicked(self) -> None: #Called when any button in chan/data/geo button groups click and the corresponding chan is refl
        button_sender = self.sender()
        #Gets id corresponding to the senders's actual group (-1 will be returned for the incorrect group)
        button_id = max(self.data_button_group.id(button_sender), self.chan_button_group.id(button_sender))
        i = 0
        for button in list(self.chan_button_group.buttons() + self.data_button_group.buttons()):
            if button.text().rstrip() in ["||", "⊥"]: #Disable all data upload/buttons corresponding to trans
                button.setChecked(False)
                button.setEnabled(False)
                if i < 6: #Iterates through all 6 layers of file uploader, clearing all trans buttons/data
                    self.upload_button_group.button(i).setEnabled(False)
                    self.full_button_group.button(i).setEnabled(False)
                    self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(1,0).itemAt(i).itemAt(1).widget().clear()
                    self.manager.data_files[i] = None
            else: #Enable all buttons corresponding to refl
                button.setEnabled(True)
                if i < 6: #Iterates through all 6 layers of file uploader
                    self.upload_button_group.button(i).setEnabled(True)
             #If the sender exist in chan/data button group, then we set both corresponding chan in each group to the same toggle
            if button == button_sender and button.isChecked():
                self.data_button_group.button(button_id).setChecked(True)
                self.chan_button_group.button(button_id).setChecked(True)
            elif button == button_sender:
                self.data_button_group.button(button_id).setChecked(False)
                self.chan_button_group.button(button_id).setChecked(False)
            i = i + 1
        self.geo_button_group.button(1).setChecked(True)
        self.config_button_clicked()

    def config_button_clicked(self) -> None:
        if all(data is None for data in self.manager.data_files):
            self.layout.itemAtPosition(5,2).widget().setEnabled(False)
            return
        selected_channels = [button.text() for button in self.chan_button_group.buttons() if button.isChecked()]
        if self.geo_button_group.button(0).isChecked():
            channels = ["||", "⊥"]
            self.manager.valid_channels = [
                channels[i] for i in range(2) 
                if (self.manager.data_files[i] is not None and channels[i] in selected_channels)
            ]
            if not self.manager.valid_channels:
                self.layout.itemAtPosition(5,2).widget().setEnabled(False)
                return
        elif self.geo_button_group.button(1).isChecked():
            channels = ["SS", "PP", "SP", "PS"]
            self.manager.valid_channels = [
                channels[i] for i in range(4) 
                if (self.manager.data_files[i+2] is not None and channels[i] in selected_channels)
            ]
            if not self.manager.valid_channels:
                self.layout.itemAtPosition(5,2).widget().setEnabled(False)
                return
        else:
            self.layout.itemAtPosition(5,2).widget().setEnabled(False)
            return
        if (all(button_group.checkedButton() is not None for button_group in [self.data_button_group, self.geo_button_group, self.chan_button_group, 
                                                                             self.source_button_group, self.system_button_group, self.planes_button_group])):
            self.layout.itemAtPosition(5,2).widget().setEnabled(True)
        else:
            self.layout.itemAtPosition(5,2).widget().setEnabled(False)

    def run_button_clicked(self) -> None:
        self.layout.itemAtPosition(5,2).widget().setEnabled(False)
        config = self.generate_config()
        if isinstance(config, FitConfig):
            self.win = FitResults(config)
            self.win.show()
            self.close()
        else:
            self.error_win(message=config)
            self.layout.itemAtPosition(5,2).widget().setEnabled(True)

    def generate_config(self) -> FitConfig:
        config = FitConfig()

        config.geometry = convert_to_config_str(self.geo_button_group.checkedButton().text())
        config.channels = [convert_to_config_str(channel) for channel in self.manager.valid_channels]
        config.source = convert_to_config_str(self.source_button_group.checkedButton().text())
        config.sys = convert_to_config_str(self.system_button_group.checkedButton().text())
        config.plane = convert_to_config_str(self.planes_button_group.checkedButton().text())

        if config.geometry == 'trans':
            channels = ["||", "⊥"]
            data_list = [read_data(data_path=self.manager.data_files[i], header=self.manager.column_headers) 
                for i in range(2) if channels[i] in self.manager.valid_channels]
        else:
            channels = ["SS", "PP", "SP", "PS"]
            data_list = [read_data(data_path=self.manager.data_files[i+2], header=self.manager.column_headers) 
                for i in range(4) if channels[i] in self.manager.valid_channels]

        no_data = [convert_to_config_str(self.manager.valid_channels[i]) 
            for i in range(len(data_list)) if data_list[i] == "No data"]
        too_many_columns = [convert_to_config_str(self.manager.valid_channels[i]) 
            for i in range(len(data_list)) if data_list[i] == "Too many columns"]
        too_few_columns = [convert_to_config_str(self.manager.valid_channels[i]) 
            for i in range(len(data_list)) if data_list[i] == "Too few columns"]
        incorrect_types = [convert_to_config_str(self.manager.valid_channels[i]) 
            for i in range(len(data_list)) if data_list[i] == "Incorrect dtype"]
        missing_types = [convert_to_config_str(self.manager.valid_channels[i]) 
            for i in range(len(data_list)) if data_list[i] == "Missing data elem"]
        
        if len(no_data) > 0:
            return f"No data in uploaded file for channel(s): {', '.join(no_data)}"
        if len(too_many_columns) > 0:
            return f"Too many data columns in uploaded file for channel(s): {', '.join(too_many_columns)}"
        if len(too_few_columns) > 0:
            return f"Missing required data columns in uploaded file for channel(s): {', '.join(no_data)}"
        if len(incorrect_types) > 0:
            return f"Incorrect data types for data in uploaded file for channel(s): {', '.join(incorrect_types)}"
        if len(missing_types) > 0:
            return f"Missing data elements for data in uploaded file for channel(s): {', '.join(missing_types)}"

        config.data = dict({convert_to_config_str(channel): data for channel, data in zip(self.manager.valid_channels, data_list)})
        config.data_files = self.manager.data_files
        config.column_headers = self.manager.column_headers
        return config
        
    def upload_file(self) -> None: #Called whenever any file upload button is clicked
        button = self.sender()
        button_id = self.upload_button_group.id(button)
        #Gets corresponding text box for the sender
        text_box = self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(1,0).itemAt(button_id).itemAt(1).widget() 
        file = QFileDialog.getOpenFileName(self, 'Open file', '','csv files (*.csv)') #Restrict file uploads to .csv documents only
        text_box.clear()
        if not file[0]: #If user did not select a valid file, then clear all entries for that chan
            self.manager.data_files[button_id] = None
            self.full_button_group.button(button_id).setEnabled(False)
        else: #Set manager to store the file and display path to the textbox
            self.manager.data_files[button_id] = file[0]
            text_box.setText(file[0])
            self.full_button_group.button(button_id).setEnabled(True)
        self.config_button_clicked()

    def plot_data(self) -> None:
        button = self.sender()
        button_id = self.full_button_group.id(button)
        data_file = self.manager.data_files[button_id]
        data = read_data(data_path=data_file, header=self.manager.column_headers)
        channels = ["||", "⊥", "SS", "PP", "SP", "PS"]
        channel = channels[button_id]

        if data == 'No data':
            self.error_win(message=f'No data found in the upload file for channel: {channel}')
            return
        elif data == 'Too many columns':
            self.error_win(message=f'Too many data columns in uploaded file for channel: {channel}')
            return
        elif data == 'Too few columns':
            self.error_win(message=f'Missing required data columns in uploaded file for channel: {channel}')
            return
        elif data == 'Incorrect dtype':
            self.error_win(message=f'Incorrect data types for data in uploaded file for channel: {channel}')
            return
        elif data == 'Missing data elem':
            self.error_win(message=f'Missing data elements for data in uploaded file for channel: {channel}')
            return
        self.plot_win = PlotWindow(channel=convert_to_config_str(channel), config=data, data_upload=True)
        self.plot_win.show()

    def show_help_win(self) -> None:
        self.additional_win = AdditionalWindow('data help')
        self.additional_win.show()
    
    def toggle_column_header(self) -> None:
        button = self.sender()
        if button.isChecked():
            self.manager.column_headers = True
        else:
            self.manager.column_headers = False
    
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

    def closeEvent(self, event) -> None:
        if self.additional_win is not None and self.additional_win:
            self.additional_win.close()
        if self.plot_win is not None and self.plot_win:
            self.plot_win.close()
        event.accept()

class SimRemoveCrystal(QWidget):
    signal = pyqtSignal()
    def __init__(self, parent=None) -> None: #Init the window
        super().__init__(parent)
        self.setWindowTitle("Remove Crystals")
        self.layout = sim_crystal_remove_layout()
        self.manager = SimInputManager()
        self.set_button_clicks()
        self.setLayout(self.layout)
        self.setFixedSize(self.layout.sizeHint())

    def set_button_clicks(self):
        self.layout.itemAt(1).widget().clicked.connect(self.remove_button_clicked)
        self.layout.itemAt(0).widget().layout().itemAt(0).widget().itemSelectionChanged.connect(self.crystal_type_change)
        for i in range(3):
            self.layout.itemAt(0).widget().layout().itemAt(1).layout().itemAt(i).widget().itemSelectionChanged.connect(self.crystal_selected)

    def crystal_type_change(self):
        selected_type = self.layout.itemAt(0).widget().layout().itemAt(0).widget().selectedItems()
        if not selected_type:
            return
        self.manager.crystal_type = selected_type[0].text()
        if self.manager.crystal_type  == 'Unary':
            self.layout.itemAt(0).widget().layout().itemAt(1).layout().setCurrentIndex(0)
            if not self.manager.unary_crysal:
                self.layout.itemAt(1).widget().setEnabled(False)
        elif self.manager.crystal_type  == 'Binary':
            self.layout.itemAt(0).widget().layout().itemAt(1).layout().setCurrentIndex(1)
            if not self.manager.binary_crysal:
                self.layout.itemAt(1).widget().setEnabled(False)
        else:
            self.layout.itemAt(0).widget().layout().itemAt(1).layout().setCurrentIndex(2)
            if not self.manager.tertiary_crystal:
                self.layout.itemAt(1).widget().setEnabled(False)

    def crystal_selected(self) -> None:
        if self.manager.crystal_type  == 'Unary':
            selected_crystal = self.layout.itemAt(0).widget().layout().itemAt(1).layout().itemAt(0).widget().selectedItems()
            self.manager.unary_crysal = selected_crystal[0].text()
            self.layout.itemAt(1).widget().setEnabled(True)
        elif self.manager.crystal_type  == 'Binary':
            selected_crystal = self.layout.itemAt(0).widget().layout().itemAt(1).layout().itemAt(1).widget().selectedItems()
            self.manager.binary_crysal = selected_crystal[0].text()
            self.layout.itemAt(1).widget().setEnabled(True)
        else:
            selected_crystal = self.layout.itemAt(0).widget().layout().itemAt(1).layout().itemAt(2).widget().selectedItems()
            self.manager.tertiary_crystal = selected_crystal[0].text()
            self.layout.itemAt(1).widget().setEnabled(True)

    def remove_button_clicked(self) -> None:
        self.layout.itemAt(1).widget().setEnabled(False)
        if self.manager.crystal_type  == 'Unary':
            crystal = self.manager.unary_crysal
        elif self.manager.crystal_type  == 'Binary':
            crystal = self.manager.binary_crysal
        else:
            crystal = self.manager.tertiary_crystal
        if not crystal:
            return
        if pathlib.Path(f'{REPO_DIR}/data/custom_crystals.yaml').exists():
            remove_crystal(crystal_name=crystal, file_path_to_read=f'{REPO_DIR}/data/custom_crystals.yaml', file_path_to_write=f'{REPO_DIR}/data/custom_crystals.yaml')
        else:
            remove_crystal(crystal_name=crystal, file_path_to_read=f'{REPO_DIR}/data/default_crystals.yaml', file_path_to_write=f'{REPO_DIR}/data/custom_crystals.yaml')
        self.regenerate_table()
        self.signal.emit()
        self.layout.itemAt(1).widget().setEnabled(True)

        message = QMessageBox(self)
        message.setWindowTitle('')
        message.setText(f'\"{crystal}\" has been successfully removed.\n\nData has been stored in ~/data/custom_crystals.yaml')
        message.setIcon(QMessageBox.Icon.NoIcon) 
        message.addButton(QMessageBox.StandardButton.Close)
        message.exec()
        
    def regenerate_table(self):
        for i in reversed(range(self.layout.itemAt(0).widget().layout().itemAt(1).count())):
            widget = self.layout.itemAt(0).widget().layout().itemAt(1).itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        new_table = sim_create_crystal_table()
        self.layout.itemAt(0).widget().layout().itemAt(1).setParent(None)
        self.layout.itemAt(0).widget().layout().addLayout(new_table)
        self.manager = SimInputManager()
        self.setLayout(self.layout)
        self.set_button_clicks()
        self.crystal_type_change()

class SimAddCrystal(QWidget):
    signal = pyqtSignal()
    def __init__(self, parent=None) -> None: #Init the window
        super().__init__(parent)
        self.setWindowTitle("Add Crystals")
        self.layout, self.crystal_button_group, self.search_type_button_group = sim_crystal_add_layout()
        self.set_button_clicks()
        self.setLayout(self.layout)
        self.setFixedSize(self.layout.sizeHint())

        self.additional_win = None

    def set_button_clicks(self):
        self.layout.itemAtPosition(3,0).layout().itemAt(0).widget().clicked.connect(self.show_help_win)
        for i in range(3):
            self.layout.itemAtPosition(0,0).widget().layout().itemAt(i).widget().clicked.connect(self.crystal_type_change)

    def crystal_type_change(self):
        button = self.sender()
        button_id = self.crystal_button_group.id(button)
        self.layout.itemAtPosition(0,1).layout().setCurrentIndex(button_id)

    def show_help_win(self):
        self.additional_win = AdditionalWindow(win_type='add crystals')
        self.additional_win.show()

    def closeEvent(self, event) -> None:
        if self.additional_win is not None and self.additional_win:
            self.additional_win.close()
        event.accept()

class SimSelection(QWidget):
    def __init__(self, parent=None) -> None: #Init the window
        super().__init__(parent)
        self.setWindowTitle("Simulation Selection")
        self.layout = sim_create_layout()
        self.manager = SimInputManager()
        self.set_button_clicks()
        self.setLayout(self.layout)
        self.setFixedSize(self.layout.sizeHint())

        self.add_win = None
        self.remove_win = None

    def set_button_clicks(self) -> None:
        self.layout.itemAtPosition(2,0).widget().clicked.connect(self.back_to_main)
        self.layout.itemAtPosition(2,1).widget().clicked.connect(self.run_button_clicked)

        self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,2).layout().itemAt(0).widget().clicked.connect(self.add_button_clicked)
        self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,2).layout().itemAt(1).widget().clicked.connect(self.remove_button_clicked)
        self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,2).layout().itemAt(2).widget().clicked.connect(self.reconfig_button_clicked)
        if pathlib.Path(f'{REPO_DIR}/data/custom_crystals.yaml').exists():
            self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,2).layout().itemAt(2).widget().setEnabled(True)
        else:
            self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,2).layout().itemAt(2).widget().setEnabled(False)

        self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,0).widget().itemSelectionChanged.connect(self.crystal_type_change)
        for i in range(3):
            self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,1).layout().itemAt(i).widget().itemSelectionChanged.connect(self.crystal_selected)
    
    def crystal_type_change(self) -> None:
        selected_type = self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,0).widget().selectedItems()
        if not selected_type:
            return
        self.manager.crystal_type = selected_type[0].text()
        if self.manager.crystal_type  == 'Unary':
            self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,1).layout().setCurrentIndex(0)
            if not self.manager.unary_crysal:
                self.layout.itemAtPosition(2,1).widget().setEnabled(False)
        elif self.manager.crystal_type == 'Binary':
            self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,1).layout().setCurrentIndex(1)
            if not self.manager.binary_crysal:
                self.layout.itemAtPosition(2,1).widget().setEnabled(False)
        else:
            self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,1).layout().setCurrentIndex(2)
            if not self.manager.tertiary_crystal:
                self.layout.itemAtPosition(2,1).widget().setEnabled(False)
    
    def crystal_selected(self) -> None:
        if self.manager.crystal_type  == 'Unary':
            selected_crystal = self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,1).layout().itemAt(0).widget().selectedItems()
            self.manager.unary_crysal = selected_crystal[0].text()
            self.layout.itemAtPosition(2,1).widget().setEnabled(True)
        elif self.manager.crystal_type  == 'Binary':
            selected_crystal = self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,1).layout().itemAt(1).widget().selectedItems()
            self.manager.binary_crysal = selected_crystal[0].text()
            self.layout.itemAtPosition(2,1).widget().setEnabled(True)
        else:
            selected_crystal = self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,1).layout().itemAt(2).widget().selectedItems()
            self.manager.tertiary_crystal = selected_crystal[0].text()
            self.layout.itemAtPosition(2,1).widget().setEnabled(True)
    
    def add_button_clicked(self) -> None:
        self.add_win = SimAddCrystal()
        self.add_win.signal.connect(self.refresh_table)
        self.add_win.show()

    def remove_button_clicked(self) -> None:
        self.remove_win = SimRemoveCrystal()
        self.remove_win.signal.connect(self.refresh_table)
        self.remove_win.show()

    def refresh_table(self) -> None:
        for i in reversed(range(self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,1).count())):
            widget = self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,1).itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        new_table = sim_create_crystal_table()
        self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,1).setParent(None)
        self.layout.itemAtPosition(1,0).widget().layout().addLayout(new_table, 0, 1)
        self.manager = SimInputManager()
        self.setLayout(self.layout)
        self.set_button_clicks()
        self.crystal_type_change()

    def reconfig_button_clicked(self) -> None:
        if not pathlib.Path(f'{REPO_DIR}/data/custom_crystals.yaml').exists():
            return
        self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,2).layout().itemAt(2).widget().setEnabled(False)
        message = QMessageBox(self)
        message.setWindowTitle('Continue')
        message.setText(f'Remove custom crystal data?\n\nThis process cannot be undone.')
        message.setIcon(QMessageBox.Icon.NoIcon)
        message.addButton(QMessageBox.StandardButton.Yes)
        message.addButton(QMessageBox.StandardButton.Cancel)
        reply = message.exec()
        if reply == QMessageBox.StandardButton.Yes:
            os.remove(f'{REPO_DIR}/data/custom_crystals.yaml')
            self.refresh_table()
        else:
            self.layout.itemAtPosition(1,0).widget().layout().itemAtPosition(0,2).layout().itemAt(2).widget().setEnabled(True)
        
    def run_button_clicked(self) -> None:
        print("RUN")

    def back_to_main(self) -> None:
        self.win = MainWindow()
        self.win.show()
        self.close()

    def closeEvent(self, event) -> None:
        if self.add_win is not None and self.add_win:
            self.add_win.close()
        if self.remove_win is not None and self.remove_win:
            self.remove_win.close()
        event.accept()

class MainWindow(QWidget):
    def __init__(self, parent=None) -> None: #Init the window
        super().__init__(parent) 
        self.setWindowTitle("SHG_Package_Name")
        self.layout = main_create_layout()
        self.set_button_clicks()
        self.setLayout(self.layout)
        self.setFixedSize(self.layout.sizeHint())
        self.additional_win = None

    def set_button_clicks(self) -> None: #Assigns all the html boxes plus buttons to the proper methods
        self.layout.itemAt(1).widget().layout().itemAtPosition(2,0).widget().anchorClicked.connect(self.url_click)
        self.layout.itemAt(1).widget().layout().itemAtPosition(2,1).widget().anchorClicked.connect(self.url_click)
        self.layout.itemAt(1).widget().layout().itemAtPosition(3,0).itemAt(0).widget().clicked.connect(self.show_fit_win)
        self.layout.itemAt(1).widget().layout().itemAtPosition(3,0).itemAt(1).widget().clicked.connect(self.show_sim_win)
        self.layout.itemAt(1).widget().layout().itemAtPosition(3,0).itemAt(2).widget().clicked.connect(self.show_more_win)

    def show_fit_win(self) -> None:
        self.win = FittingInput()
        self.win.show()
        self.close()

    def show_sim_win(self) -> None:
        self.win = SimSelection()
        self.win.show()
        self.close()

    def show_more_win(self) -> None:
        self.additional_win = AdditionalWindow(win_type='more')
        self.additional_win.show()

    def url_click(self, url) -> None:
        QDesktopServices.openUrl(url)

    def closeEvent(self, event) -> None:
        if self.additional_win is not None and self.additional_win:
            self.additional_win.close()
        event.accept()

def main():
    check_files()
    OS_CONFIG.set_config()
    if OS_CONFIG.invalid_os == True: #Test to see if the os is valid before starting application, kills script if it is invalid
        print(f"Version {pkg_resources.get_distribution('shg_simulation').version} of SHG Simulation Package is not supported on this operating system.")
        print("Supported operating systems: Windows, macOS, and Linux.")
        return
    app = QApplication(sys.argv)
    QLoggingCategory.setFilterRules("qt.qpa.fonts.warning=false")
    QApplication.instance().setStyleSheet(OS_CONFIG.style_sheet)
    window = MainWindow()
    window.show()
    app.exec()
