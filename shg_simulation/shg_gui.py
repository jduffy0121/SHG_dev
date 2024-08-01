import sys
import pathlib
import pkg_resources
import matplotlib.pyplot as plt
from typing import List, Union, Tuple
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar, FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFontMetrics, QTextOption, QDesktopServices
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout, QLabel, QTableWidgetItem, QTableWidget, QComboBox,
    QHBoxLayout, QVBoxLayout, QCheckBox, QFileDialog, QMessageBox, QRadioButton, QButtonGroup, QTextEdit, 
    QTabWidget, QTextBrowser, QGroupBox, QStackedLayout, QScrollArea
)

from .utils import *
from .gui_classes import *
from .data_fitting import *
from .gui_html_boxes import *

REPO_DIR = pathlib.Path(__file__).parent.parent.resolve()
OS_CONFIG = OSConfig()

class HelpWindow(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Infromation")
        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(False)

        self.about_txt = create_about_us_tab(img=f'{REPO_DIR}/imgs/prev.png')
        self.about_txt.anchorClicked.connect(self.url_click)

        self.tabs.addTab(self.about_txt, "About Us")
        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)
    
    def url_click(self, url):
        QDesktopServices.openUrl(url)

class PlotWindow(QWidget):
    def __init__(self, channel: list, config, point_groups, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f'{channel}')
        self.config = config
        self.fits = [point_group for point_group in point_groups if point_group.active == True and point_group.channel == channel]
        self.fig, self.ax = polar_plot(title=channel, data=self.config.data[channel], 
                                       width=OS_CONFIG.full_plt_len, height=OS_CONFIG.full_plt_len, 
                                       dpi=OS_CONFIG.full_plt_dpi, fits=self.fits)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

    def closeEvent(self, event) -> None:
        plt.close(self.fig)
        event.accept()

class ParameterAdjust(QWidget):
    def __init__(self, channel: str, point_group, parent=None) -> None:
        super().__init__(parent)
        if '_' in point_group.name:
            self.point_group_formatted = point_group.name.replace('_', '<sub>') + '</sub>'
        else:
            self.point_group_formatted = point_group.name
        self.point_group = point_group
        self.setWindowTitle('Parameters')
        self.txt = QLabel(f'Fitting function: r = {get_readable_fit_func(point_group.name)}')
        self.txt2 = QLabel(f'Channel: {channel}')
        self.txt3 = QLabel(f'Point Group: {self.point_group_formatted}')

        self.table = QTableWidget()
        self.table.setRowCount(len(point_group.weights))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Parameter', 'Value'])

        i = 0
        for constant in point_group.weights:
            self.const = QTableWidgetItem(constant[0])
            self.const.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(i, 0, self.const)
            self.value = QTableWidgetItem(str(round(constant[1], 3)))
            self.table.setItem(i, 1, self.value)
            i = i + 1
        
        self.table.horizontalHeader().setStretchLastSection(True)
        
        self.sublayot = QHBoxLayout()
        
        self.e1 = QPushButton('✎')
        self.b1 = QPushButton('Apply Changes')
        self.b1.setEnabled(False)
        self.r1 = QPushButton('↺')
        self.r2 = QPushButton('⏮')
        self.b2 = QPushButton('⏴')
        self.b3 = QPushButton('⏵')
        self.b4 = QPushButton('⏭')
        
        self.sublayot.addWidget(self.r1)
        self.sublayot.addWidget(self.r2)
        self.sublayot.addWidget(self.b2)
        self.sublayot.addWidget(self.b3)
        self.sublayot.addWidget(self.b4)
        
        self.sublayout2 = QHBoxLayout()
        self.sublayout2.addWidget(self.txt2)
        self.sublayout2.addWidget(self.txt3)

        self.sublayout3 = QHBoxLayout()
        self.sublayout3.addWidget(self.txt)
        self.sublayout3.addWidget(self.e1)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.sublayout3)
        self.layout.addLayout(self.sublayout2)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.b1)
        self.layout.addLayout(self.sublayot)
        self.setLayout(self.layout)

        self.setFixedSize(self.layout.sizeHint())

class FitResults(QWidget):
    def __init__(self, config: FitConfig, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Fit Results")
        self.layout = QGridLayout()
        self.img_label = QLabel()
        self.img = QPixmap(f'{REPO_DIR}/imgs/logo_mini.png')
        self.img_scaled = self.img.scaled(136,68)
        self.img_label.setPixmap(self.img_scaled) 

        self.config = config
        self.manager = FitManager()
        self.manager.selection_mode == 'Single'
        init_fit_classes(config=self.config, manager=self.manager)
       
        self.tabs_layout, self.fit_button_group, self.legend_button_group, self.param_button_group = self.win_create_fit_tabs_layer(init_tabs=True)

        self.no_plots = TableLabel(f"Select plots to continue")

        self.sel_chan_txt = QLabel(f"Selection mode: {self.manager.selection_mode}\nSelected channel(s): None")
        self.sel_chan_txt.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.add_button_layout, self.add_button_group, self.swap_button_group = self.win_create_add_plot_layer()
        self.plot_layout, self.full_button_group, self.close_button_group = self.win_create_plot_layer(channels=self.config.channels)
        
        self.no_layout = QGridLayout()
        self.no_layout.addWidget(self.no_plots, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        #self.no_layout.addWidget(self.sel_chan_txt, 0, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.expand_layout = self.win_create_expand_layer()
        self.expand_layout.setCurrentIndex(0)
        self.group_box_1 = QGroupBox()
        self.area = QScrollArea()
        self.area.setFixedSize(500,550)
        self.area.setLayout(self.no_layout)
        self.layout_new = QGridLayout()
        self.layout_new.addWidget(self.area, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        #self.layout_new.addWidget(self.sel_chan_txt, 0, 0, alignment=Qt.AlignmentFlag.AlignBottom)
        self.group_box_1.setLayout(self.layout_new)
        self.group_box_1.setFixedSize(550,600)
        self.area = QScrollArea()
        self.area.setFixedSize(500,575)
        self.widget = QWidget()
        self.widget.setLayout(self.tabs_layout)
        self.tabs = QTabWidget()
        self.tabs.addTab(self.widget, 'INIT')
        self.label2 = QLabel("HI")
        self.tabs.addTab(self.label2, 'INIT2')
        self.tabs.setFixedWidth(525)
        self.group_box_2 = QGroupBox()
        self.tabs_layout = QVBoxLayout()
        self.tabs_layout.addWidget(self.tabs)
        self.group_box_2.setLayout(self.tabs_layout)
        
        self.back_button = QPushButton("Back")
        self.back_button.setFixedSize(70,25)

        self.layout.addWidget(self.group_box_2, 0, 0, 2, 1)
        self.layout.addLayout(self.expand_layout, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.group_box_1, 1, 2, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.back_button, 3, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.img_label, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.sel_chan_txt, 3, 2, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        self.help_win = None

        self.setLayout(self.layout)
        self.setFixedSize(self.layout.sizeHint())   
        
        self.clear_plots()
        self.manager.plots_showing = []
    
    def win_create_fit_tabs_layer(self, init_tabs=False) -> (QVBoxLayout(), List[QButtonGroup()], List[ComboBoxGroup()], List[QButtonGroup()]):
        layout = QVBoxLayout()

        fit_check_groups = []
        legend_groups = []
        params_groups = []

        if self.manager.selection_mode == 'Multiple' and self.manager.selected_channels:
            channel_tabs = QTabWidget()
            channel_tabs.setTabPosition(QTabWidget.TabPosition.North)
            for channel in self.manager.selected_channels:
                channel_widget = QWidget()
                tab_layout = QVBoxLayout() 
                fit_table, fit_check_group, legend_group, param_group = self.create_single_fit_table(channel=channel, init_tabs=init_tabs)
                fit_check_groups.append((channel, fit_check_group))
                legend_groups.append((channel, legend_group))
                params_groups.append((channel, param_group))
                tab_layout.addWidget(fit_table)
                channel_widget.setLayout(tab_layout)
                channel_tabs.addTab(channel_widget, f'{channel}')
            layout.addWidget(channel_tabs)
        else:
            if not self.manager.selected_channels:
                init_tabs = True
                channel = None
            else:
                channel = self.manager.selected_channels[0]

            fit_table, fit_check_group, legend_group, param_group = self.create_single_fit_table(channel=channel, init_tabs=init_tabs)
            fit_check_groups.append((channel, fit_check_group))
            legend_groups.append((channel, legend_group))
            params_groups.append((channel, param_group))
            layout.addWidget(fit_table)
        return layout, fit_check_groups, legend_groups, params_groups

    def win_create_expand_layer(self) -> QStackedLayout:
        layout = QStackedLayout()
        group_box_1 = QGroupBox()
        layout_1 = QVBoxLayout()
        visuals_button_1 = QPushButton('✹')
        visuals_button_1.setToolTip('Visualizations')
        visuals_button_2 = QPushButton('✹')
        visuals_button_2.setToolTip('Visualizations')
        download_button_1 = QPushButton('⤓')
        download_button_1.setToolTip('Download fit data as .csv')
        download_button_2 = QPushButton('⤓')
        download_button_2.setToolTip('Download fit data as .csv')
        group_button_1 = QPushButton('፨')
        group_button_1.setToolTip('Point group information no cap')
        group_button_2 = QPushButton('፨')
        group_button_2.setToolTip('Point group information lol')
        redo_button_1 = QPushButton('↻')
        redo_button_1.setToolTip('Reset all fits for all channels/point groups')
        redo_button_2 = QPushButton('↻')
        redo_button_2.setToolTip('Reset all fits for all channels/point groups')
        expand_button = QPushButton('>')
        expand_button.setToolTip('Show plot manager')
        expand_button.clicked.connect(self.toggle_stack)
        retract_button = QPushButton('<')
        retract_button.setToolTip('Hide plot manager')
        retract_button.clicked.connect(self.toggle_stack)
        
        layout_1.addWidget(visuals_button_1, alignment=Qt.AlignmentFlag.AlignBottom)
        layout_1.addWidget(download_button_1, alignment=Qt.AlignmentFlag.AlignBottom)
        layout_1.addWidget(group_button_1, alignment=Qt.AlignmentFlag.AlignBottom)
        layout_1.addWidget(redo_button_1, alignment=Qt.AlignmentFlag.AlignBottom)
        layout_1.addWidget(expand_button, alignment=Qt.AlignmentFlag.AlignBottom)
        group_box_1.setLayout(layout_1)
        group_box_1.setFixedSize(75,200)
        
        retract_widget = QWidget()
        retract_layout = QVBoxLayout()
        retract_layout.addWidget(group_box_1, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        retract_widget.setLayout(retract_layout)

        expand_layout = QVBoxLayout()
        add_button_group = QButtonGroup()
        swap_button_group = QButtonGroup()
        button_id = 0
        header_label = GroupLabel('Manage plots')
        expand_layout.addWidget(header_label, alignment=Qt.AlignmentFlag.AlignCenter)
        for channel in self.config.channels:
            if channel == "Parallel":
                label = GroupLabel('||')
            elif channel == "Perpendicular":
                label = GroupLabel('⊥')
            else:
                label = GroupLabel(f'{channel}')
            sub_layout = QHBoxLayout()
            sub_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignRight)
            button_layout = QVBoxLayout()
            add_button = QPushButton('+')
            add_button.clicked.connect(self.add_button_clicked) 
            add_button.setToolTip('Add plot')
            add_button_group.setId(add_button, button_id)
            swap_button = QPushButton('⇆')
            swap_button.clicked.connect(self.swap_button_clicked)
            swap_button.setToolTip('Swap with current selected (only works with single selection)')
            swap_button_group.setId(swap_button, button_id)
            button_layout.addWidget(add_button)
            button_layout.addWidget(swap_button)
            sub_layout.addLayout(button_layout)
            button_id = button_id + 1
            if self.manager.plots_showing is not None:
                if channel in self.manager.plots_showing:
                    add_button.setEnabled(False)
            expand_layout.addLayout(sub_layout)
        data_color_label = GroupLabel('Choose data points color')
        data_color_box = CustomComboBox()
        data_color_box.addItems(['Blue', 'Red', 'Green', 'Orange', 'Purple', 'Brown'])
        selection_mode_label = GroupLabel('Choose selection mode')
        selection_mode_box = CustomComboBox()
        selection_mode_box.addItems(['Single', 'Multiple'])
        if self.manager.selection_mode == 'Multiple':
            selection_mode_box.setCurrentIndex(1)
        selection_mode_box.box_signal.connect(self.selection_mode_changed)
        expand_layout.addWidget(data_color_label, alignment=Qt.AlignmentFlag.AlignCenter)
        expand_layout.addWidget(data_color_box)
        expand_layout.addWidget(selection_mode_label, alignment=Qt.AlignmentFlag.AlignCenter)
        expand_layout.addWidget(selection_mode_box)

        group_box_2 = QGroupBox()
        layout_2 = QVBoxLayout()
        layout_2.addWidget(visuals_button_2, alignment=Qt.AlignmentFlag.AlignBottom)
        layout_2.addWidget(download_button_2, alignment=Qt.AlignmentFlag.AlignBottom)
        layout_2.addWidget(group_button_2, alignment=Qt.AlignmentFlag.AlignBottom)
        layout_2.addWidget(redo_button_2, alignment=Qt.AlignmentFlag.AlignBottom)
        layout_2.addWidget(retract_button, alignment=Qt.AlignmentFlag.AlignBottom)
        group_box_2.setLayout(layout_2)
        group_box_2.setFixedSize(75,200)

        group_box_3 = QGroupBox()
        group_box_3.setLayout(expand_layout)
        group_box_3.setFixedWidth(200)
        
        expand_widget_2 = QWidget()
        expand_layout_2 = QHBoxLayout()
        expand_layout_2.addWidget(group_box_2, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        expand_layout_2.addWidget(group_box_3, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        expand_widget_2.setLayout(expand_layout_2)

        layout.addWidget(retract_widget)
        layout.addWidget(expand_widget_2)

        return layout

    def win_create_plot_layer(self, channels: list) -> (QGridLayout(), QButtonGroup(), QButtonGroup()):
        layout = QGridLayout()
        full_button_group = QButtonGroup()
        close_button_group = QButtonGroup()
        plot_id = 0
        self.manager.plots_showing = []
        self.manager.figures = []
        for channel in channels:
            fits = [point_group for point_group in self.manager.point_groups if point_group.active == True and point_group.channel == channel]
            sub_layout = QGridLayout()
            button_layout = QVBoxLayout()

            enlarge_button = QPushButton('⤢')
            close_button = QPushButton('✕')
            enlarge_button.setToolTip('Display in a new window')
            close_button.setToolTip('Close plot')
            
            full_button_group.addButton(enlarge_button)
            full_button_group.setId(enlarge_button, plot_id)
            close_button_group.addButton(close_button)
            close_button_group.setId(close_button, plot_id)

            enlarge_button.clicked.connect(self.full_button_clicked)
            close_button.clicked.connect(self.close_button_clicked) 
            
            fig, ax = polar_plot(title=channel, data=self.config.data[channel], 
                                 width=(OS_CONFIG.fit_res_mini_plt_r/OS_CONFIG.fit_res_mini_plt_dpi) * 2, 
                                 height=(OS_CONFIG.fit_res_mini_plt_r/OS_CONFIG.fit_res_mini_plt_dpi) * 2, 
                                 dpi=OS_CONFIG.fit_res_mini_plt_dpi, fits=fits)
            canvas = ClickableFigureCanvas(figure=fig, plot_id=plot_id, radius=OS_CONFIG.fit_res_mini_plt_r)
            canvas.canvas_signal.connect(self.canvas_clicked)
            self.manager.figures.append((fig, canvas))
            canvas.setFixedSize(OS_CONFIG.fit_res_mini_plt_r * 2, OS_CONFIG.fit_res_mini_plt_r * 2)

            sub_layout.addWidget(canvas, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
            button_layout.addWidget(enlarge_button)
            button_layout.addWidget(close_button)
            sub_layout.addLayout(button_layout, 0, 1, alignment=Qt.AlignmentFlag.AlignTop)
            
            self.manager.plots_showing.append(channel)

            if plot_id == 0:
                layout.addLayout(sub_layout, 0, 0)
            elif plot_id == 1:
                layout.addLayout(sub_layout, 0, 1)
            elif plot_id == 2:
                layout.addLayout(sub_layout, 1, 0)
            else:
                layout.addLayout(sub_layout, 1, 1)
            plot_id = plot_id + 1
    
        return layout, full_button_group, close_button_group
    
    def win_create_add_plot_layer(self) -> (QVBoxLayout(), QButtonGroup(), QButtonGroup()):
        layout = QVBoxLayout()
        add_button_group = QButtonGroup()
        swap_button_group = QButtonGroup()
        button_id = 0
        header_label = QLabel('Manage plots')
        layout.addWidget(header_label, alignment=Qt.AlignmentFlag.AlignCenter)
        for channel in self.config.channels:
            if channel == "Parallel":
                label = QLabel('||')
            elif channel == "Perpendicular":
                label = QLabel('⊥')
            else:
                label = QLabel(f'{channel}')
            sub_layout = QHBoxLayout()
            sub_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignRight)
            button_layout = QVBoxLayout()
            add_button = QPushButton('+')
            add_button.clicked.connect(self.add_button_clicked) 
            add_button.setToolTip('Add plot')
            add_button_group.setId(add_button, button_id)
            swap_button = QPushButton('⇆')
            swap_button.clicked.connect(self.swap_button_clicked)
            swap_button.setToolTip('Swap with current selected (only works with single selection)')
            swap_button_group.setId(swap_button, button_id)
            button_layout.addWidget(add_button)
            button_layout.addWidget(swap_button)
            sub_layout.addLayout(button_layout)
            button_id = button_id + 1
            if self.manager.plots_showing is not None:
                if channel in self.manager.plots_showing:
                    add_button.setEnabled(False)
            layout.addLayout(sub_layout)
        data_color_label = QLabel('Choose data points color')
        data_color_box = CustomComboBox()
        data_color_box.addItems(['Blue', 'Red', 'Green', 'Orange', 'Purple', 'Brown'])
        selection_mode_label = QLabel('Choose selection mode')
        selection_mode_box = CustomComboBox()
        selection_mode_box.addItems(['Single', 'Multiple'])
        if self.manager.selection_mode == 'Multiple':
            selection_mode_box.setCurrentIndex(1)
        selection_mode_box.box_signal.connect(self.selection_mode_changed)
        layout.addWidget(data_color_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(data_color_box)
        layout.addWidget(selection_mode_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(selection_mode_box)
        return layout, add_button_group, swap_button_group

    def toggle_stack(self) -> None:
        current_index = self.expand_layout.currentIndex()
        new_index = 1 - current_index
        self.expand_layout.setCurrentIndex(new_index)

    def full_button_clicked(self) -> None:
        button = self.sender()
        button_id = self.full_button_group.id(button)
        channel = self.manager.plots_showing[button_id]
        self.manager.prev_selected = self.manager.selected_channels
        if self.manager.selection_mode == 'Single':
            self.manager.selected_channels = []
        if not channel in self.manager.selected_channels:
            self.manager.selected_channels.append(channel)
        self.update_selections()
        self.plot_window = PlotWindow(channel=channel, config=self.config, point_groups=self.manager.point_groups)
        self.plot_window.show()

    def expand_plots_button_clicked(self) -> None:
        self.more_layout.removeWidget(self.help_button)
        self.help_button.deleteLater()
        self.help_button.setParent(None)
        self.expand_layout.removeWidget(self.expand_plots_button)
        self.expand_plots_button.deleteLater()
        self.expand_plots_button.setParent(None)
        self.more_layout.removeWidget(self.download_button)
        self.download_button.deleteLater()
        self.download_button.setParent(None)
        self.more_layout.removeWidget(self.fitting_button)
        self.fitting_button.deleteLater()
        self.fitting_button.setParent(None)
        self.more_layout.removeWidget(self.redo_button)
        self.redo_button.deleteLater()
        self.redo_button.setParent(None)

        if not self.manager.expanded_window:
            self.manager.expanded_window = True
            self.add_button_layout, self.add_button_group, self.swap_button_group = self.win_create_add_plot_layer()
            self.expand_plots_button = QPushButton('<')

        else:
            self.manager.expanded_window = False
            for i in range(self.expand_layout.count()):
                item_1 = self.expand_layout.itemAt(i)
                if item_1 is None:
                    break
                if isinstance(item_1.layout(), QVBoxLayout):
                    for j in reversed(range(item_1.count())):
                        item_2 = item_1.itemAt(j)
                        if isinstance(item_2.layout(), QHBoxLayout):
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
                        else:
                            widget = item_2.widget()
                            widget.deleteLater()
                            widget.setParent(None)
            self.expand_plots_button = QPushButton('>')
        self.expand_plots_button.setToolTip('Manage plots and selection')
        self.expand_plots_button.clicked.connect(self.expand_plots_button_clicked)
        
        self.help_button = QPushButton("✹")
        #self.help_button.clicked.connect(self.open_help_win)
        self.help_button.setToolTip('Visualizations')

        self.download_button = QPushButton("⤓")
        self.download_button.setToolTip('Download fit data as .csv')

        if not self.manager.selected_channels:
            self.download_button.setEnabled(False)

        self.fitting_button = QPushButton('፨')
        self.fitting_button.setToolTip('Point group information')

        self.redo_button = QPushButton('↻')
        self.redo_button.setToolTip('Reset all fits for all channels/point groups')

        self.more_layout = QVBoxLayout()
        self.more_layout.addWidget(self.help_button, alignment=Qt.AlignmentFlag.AlignBottom)
        self.more_layout.addWidget(self.fitting_button, alignment=Qt.AlignmentFlag.AlignBottom)
        self.more_layout.addWidget(self.download_button, alignment=Qt.AlignmentFlag.AlignBottom)
        self.more_layout.addWidget(self.redo_button, alignment=Qt.AlignmentFlag.AlignBottom)
        self.more_layout.addWidget(self.expand_plots_button, alignment=Qt.AlignmentFlag.AlignBottom)
        
        self.expand_layout = QHBoxLayout()
        self.expand_layout.addLayout(self.more_layout)
        
        if self.manager.expanded_window:
            self.expand_layout.addLayout(self.add_button_layout)

        self.layout.addLayout(self.expand_layout, 0, 1, 2, 1, alignment=Qt.AlignmentFlag.AlignBottom)
        self.setLayout(self.layout)

    def close_button_clicked(self) -> None:
        button = self.sender()
        button_id = self.close_button_group.id(button)
        channel = self.manager.plots_showing[button_id]
        channel_id = self.config.channels.index(channel)
        if self.manager.expanded_window:
            self.add_button_group.button(channel_id).setEnabled(True)
        num_of_plts = len(self.manager.plots_showing)
        if num_of_plts == 1:
            no_plots = QLabel("\t\tSelect plots to continue\t\t")
            self.clear_plots()
            self.manager.plots_showing = []
            self.no_layout.addWidget(no_plots, alignment=Qt.AlignmentFlag.AlignBottom)
            self.setLayout(self.layout)
            self.manager.prev_selected = self.manager.selected_channels
            self.manager.selected_channels = []
            self.update_selections()
            return
        plot_list = self.manager.plots_showing[:button_id] + self.manager.plots_showing[button_id+1:]
        self.clear_plots()
        self.manager.plots_showing = []
        self.plot_layout, self.full_button_group, self.close_button_group = self.win_create_plot_layer(channels=plot_list)
        self.layout.addLayout(self.plot_layout, 0, 2)
        self.setLayout(self.layout)
        self.manager.prev_selected = self.manager.selected_channels
        if channel in self.manager.selected_channels:
            self.manager.selected_channels.remove(channel)
            if self.manager.selection_mode == 'Single':
                self.manager.selected_channels = []
        self.update_selections()

    def add_button_clicked(self) -> None:
        button = self.sender()
        button.setEnabled(False)
        button_id = self.add_button_group.id(button)
        channel = self.config.channels[button_id]
        if self.manager.plots_showing == []:
            total_channels = [channel]
            text = self.no_layout.itemAt(0).widget()
            self.no_layout.removeWidget(text)
            text.deleteLater()
            text.setParent(None)
        else:
            total_channels = self.manager.plots_showing + [channel]
            self.clear_plots()
            self.manager.plots_showing = []
        self.plot_layout, self.full_button_group, self.close_button_group = self.win_create_plot_layer(channels = total_channels)
        self.layout.addLayout(self.plot_layout, 0, 2)
        self.manager.prev_selected = self.manager.selected_channels
        if self.manager.selection_mode == 'Single':
            self.manager.selected_channels = []
        self.manager.selected_channels.append(channel)
        self.update_selections()

    def swap_button_clicked(self) -> None:
        return
        if not self.manager.plots_showing:
            return
        button = self.sender()
        button_id = self.swap_button_group.id(button)
        channel = self.config.channels[button_id]
        selected_id = self.plots_showing.index(self.manager)
        plot_list = self.plots_showing
        if (self.sel_chan[0] in self.plots_showing) and (self.config.channels[button_id] in self.plots_showing):
            plot_id = self.plots_showing.index(channel)
            plot_list[selected_id], plot_list[plot_id] = plot_list[plot_id], plot_list[selected_id]
            self.clear_plots()
            self.plots_showing = None
            self.plot_layout, self.full_button_group, self.close_button_group = self.win_create_plot_layer(channels = plot_list)
            self.layout.addLayout(self.plot_layout, 0, 2)
            if self.sel_mode == 'Single':
                self.sel_chan = []
            self.sel_chan.append(channel)
            self.update_selections()

        else:
            plot_list[selected_id] = channel
            self.clear_plots()
            self.plots_showing = None
            self.plot_layout, self.full_button_group, self.close_button_group = self.win_create_plot_layer(channels = plot_list)
            self.layout.addLayout(self.plot_layout, 0, 2)
            if self.sel_mode == 'Single':
                self.sel_chan = []
            self.sel_chan.append(channel)
            self.update_selections()
    
    def create_single_fit_table(self, channel:str, init_tabs=False):
        fit_table = QTableWidget()
        groups = [group for group in self.manager.point_groups if group.channel==channel]
        group_indexes = [index for index, group in enumerate(self.manager.point_groups) if group.channel==channel]
        num_of_rows = len(groups)
        fit_table.setRowCount(num_of_rows)
        fit_table.setColumnCount(5)
        fit_table.setHorizontalHeaderLabels(['Selected', 'Point Group', 'Fit', 'Legend', 'Parameters'])

        fit_check_group = QButtonGroup()
        params_group = QButtonGroup()
        legend_group = ComboBoxGroup()
        fit_check_group.setExclusive(False)
        if not init_tabs:
            for i in range(num_of_rows):
                check_box = TableCheckBox()
                check_box.clicked.connect(self.fit_button_clicked)
                fit_check_group.addButton(check_box, group_indexes[i])
                check_box_item = QTableWidgetItem()
                fit_table.setItem(i, 0, check_box_item)
                fit_table.setCellWidget(i, 0, check_box)
                point_group = self.manager.point_groups[group_indexes[i]]
                if point_group.active:
                    check_box.setChecked(True)
                else:
                    check_box.setChecked(False)
                if '_' in point_group.name:
                    point_group_formatted = point_group.name.replace('_', '<sub>') + '</sub>'
                else:
                    point_group_formatted = point_group.name
                label = TableLabel(point_group_formatted)
                label_item = QTableWidgetItem()
                fit_table.setItem(i, 1, label_item)
                fit_result = QTableWidgetItem(str(round(point_group.r2, 3)))
                fit_result.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                fit_table.setCellWidget(i, 1, label)
                fit_table.setItem(i, 2, fit_result)
                box = QComboBox()
                box.addItems(['Red', 'Green', 'Orange', 'Purple', 'Brown', 'Blue'])
                box.setCurrentText(point_group.legend)
                legend_group.addComboBox(box)
                fit_check_group.addButton(check_box, i)
                fit_table.setCellWidget(i, 3, box)

                button = QPushButton('Set')
                button.clicked.connect(self.param_button_clicked)
                fit_table.setCellWidget(i, 4, button)
                params_group.addButton(button, group_indexes[i])
        #fit_table.setFixedWidth(500) 
        fit_table.horizontalHeader().setStretchLastSection(True)
        fit_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        fit_table.itemSelectionChanged.connect(lambda: self.update_table(fit_table))
        return fit_table, fit_check_group, legend_group, params_group

    def update_table(self, table_widget):
        for row in range(table_widget.rowCount()):
            for col in range(table_widget.columnCount()):
                table_item = table_widget.cellWidget(row, col)
                if isinstance(table_item, TableCheckBox) or isinstance(table_item, TableLabel):
                    item = table_widget.item(row, col)
                    table_item.setSelected(item.isSelected())
    
    def fit_button_clicked(self) -> None:
        button = self.sender()
        button_group = None
        channel = None
        for (chan, group) in self.fit_button_group:
            if button in group.buttons():
                button_group = group
                channel = chan
                break
        button_id = button_group.id(button)
        point_group = self.manager.point_groups[button_id]
        if point_group.active:
            point_group.active = False
            button.setChecked(False)
        else:
            point_group.active = True
            button.setChecked(True)
        old_plots = self.manager.plots_showing
        self.clear_plots()
        self.plot_layout, self.full_button_group, self.close_button_group = self.win_create_plot_layer(channels = old_plots)
        self.layout.addLayout(self.plot_layout, 0, 2)
        self.update_selections()

    def param_button_clicked(self) -> None:
        button = self.sender()
        button_group = None
        channel = None
        for (chan, group) in self.param_button_group:
            if button in group.buttons():
                button_group = group
                channel = chan
                break
        button_id = button_group.id(button)
        point_group = self.manager.point_groups[button_id]
        self.param_win = ParameterAdjust(channel=channel, point_group=point_group)
        self.param_win.show()

    def selection_mode_changed(self, mode) -> None:
        self.manager.selection_mode = mode
        index = len(self.manager.selected_channels)
        self.manager.prev_selected = self.manager.selected_channels
        if self.manager.selection_mode == 'Single' and index > 1:
            self.manager.selected_channels = []
            self.manager.selected_channels.append(self.manager.prev_selected[0])
        self.update_selections()

    def canvas_clicked(self, plot_id) -> None:
        channel = self.manager.plots_showing[plot_id]
        self.manager.prev_selected = self.manager.selected_channels
        if self.manager.selection_mode == 'Single':
            if channel in self.manager.selected_channels:
                self.manager.selected_channels = []
            else:
                self.manager.selected_channels = []
                self.manager.selected_channels.append(channel)
        else:
            if channel in self.manager.selected_channels:
                self.manager.selected_channels.remove(channel)
            else:
                self.manager.selected_channels.append(channel)
        self.update_selections()

    def update_selections(self, disable_swap = False) -> None:
        text = self.layout.itemAtPosition(1,3).widget()
        self.layout.removeWidget(text)
        text.deleteLater()
        text.setParent(None)
        if self.manager.plots_showing is not None:
            for fig, canvas in self.manager.figures:
                canvas.remove_glow_effect()
        if self.manager.selected_channels:
            for channel in self.manager.selected_channels:
                selected_id = self.manager.plots_showing.index(channel)
                self.manager.figures[selected_id][1].apply_glow_effect()
        self.clear_fit_tables()
        self.tabs_layout, self.fit_button_group, self.legend_button_group, self.param_button_group = self.win_create_fit_tabs_layer(init_tabs=False)
        self.layout.addLayout(self.tabs_layout, 0, 0, 2, 1)
        if len(self.manager.selected_channels) == 0:
            label = None
            self.download_button.setEnabled(False)
        else:
            label = f"{', '.join(self.manager.selected_channels)}"
            self.download_button.setEnabled(True)
        self.sel_chan_txt = QLabel(f"Selection mode: {self.manager.selection_mode}\nSelected channel(s): {label}", alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.sel_chan_txt, 1, 3, alignment=Qt.AlignmentFlag.AlignBottom)
        self.setLayout(self.layout)
        if self.manager.expanded_window:
            for channel in self.config.channels:
                if self.manager.selection_mode == 'Single' and self.manager.selected_channels:
                    channel_id = self.config.channels.index(channel)
                    if channel in self.manager.selected_channels:
                        self.swap_button_group.button(channel_id).setEnabled(False)
                    else:
                        self.swap_button_group.button(channel_id).setEnabled(True)
                else:
                    channel_id = self.config.channels.index(channel)
                    self.swap_button_group.button(channel_id).setEnabled(False)

    def clear_fit_tables(self):
        item_1 = self.tabs_layout.itemAt(0)
        widget = item_1.widget()
        if isinstance(widget, QTableWidget) and isinstance(widget.cellWidget(0,3), QComboBox):
            j = 0
            if self.manager.selection_mode == 'Single' and len(self.manager.prev_selected) > 1:
                prev = self.manager.prev_selected[0]
            else:
                prev = self.manager.prev_selected
            for i in range(len(prev)):
                point_group = self.manager.point_groups[i]
                if point_group.channel in self.manager.prev_selected:
                    point_group.legend = widget.cellWidget(j,3).currentText()
                    j = j + 1
        elif isinstance(widget, QTabWidget) and isinstance(widget.widget(0), QWidget):
            i = 0
            for i in range(widget.count()):
                table = widget.widget(i).findChild(QTableWidget)
                channel = widget.tabText(i)
                k = 0
                for j in range(len(self.manager.point_groups)):
                    point_group = self.manager.point_groups[j]
                    if point_group.channel == channel:
                        point_group.legend = table.cellWidget(k,3).currentText()
                        k = k + 1
                i = i + 1
        widget.deleteLater()
        widget.setParent(None)

    def clear_plots(self):
        for fig, canvas in self.manager.figures:
            plt.close(fig)
        for k in range(self.plot_layout.count()):
            item_1 = self.plot_layout.itemAt(k)
            if item_1 is None:
                self.plot_layout = None
                break
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
        self.manager.plots_showing = []
        
    def open_help_win(self) -> None:
        self.help_win = HelpWindow()
        self.help_win.show()

    def closeEvent(self, event) -> None:
        for fig, canvas in self.manager.figures:
            plt.close(fig)
        if self.help_win is not None and self.help_win.isVisible():
            self.help_win.close()
        event.accept()

class FitWindow(QWidget): 
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Data Import")
        
        self.layout = QGridLayout()
        self.import_layout = QGridLayout()
        
        self.header_label = QLabel("<h1>Import Data for Fit</h1>") 
        self.img_label = QLabel()
        self.img = QPixmap(f'{REPO_DIR}/imgs/logo_mini.png')
        self.img_scaled = self.img.scaled(136,68)
        self.img_label.setPixmap(self.img_scaled)
        self.layout.addWidget(self.header_label, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.img_label, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)

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
        self.run_button.setFixedSize(70,25)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.back_to_main)
        self.back_button.setFixedSize(70,25)

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
        self.import_layout.addWidget(self.data_layout, 0, 0)
        self.import_layout.addLayout(self.config_layout, 0, 1)
         
        self.layout.addLayout(self.import_layout, 1, 0)

        self.layout.addWidget(self.run_button, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.back_button, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.layout)
        
        self.valid_channels = None

        self.setFixedSize(self.layout.sizeHint())

    def win_create_data_layer_group(self) -> (QGroupBox, QButtonGroup(), QButtonGroup()):
        layout = QVBoxLayout()
        label = GroupLabel("<h3>File Upload</h3>")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
    
        data_button_group = QButtonGroup()
        upload_group = QButtonGroup()
        data_button_group.setExclusive(False)

        button_id = 0
        for chan in self.channels: 
            d_chan_layout = QHBoxLayout()
            if chan == '||':
                box = GroupCheckBox(f"{chan}   ")
            elif chan == '⊥':
                box = GroupCheckBox(f"{chan}  ")
            else:
                box = GroupCheckBox(f"{chan}")
            box.clicked.connect(self.chan_button_clicked)

            text = QTextEdit(self)
            text.setReadOnly(True)
            font_metrics = QFontMetrics(text.font())
            line_height = font_metrics.lineSpacing()
            text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            text.setWordWrapMode(QTextOption.WrapMode.NoWrap)
            text.setFixedSize(OS_CONFIG.fit_win_upld_box_len, line_height + OS_CONFIG.fit_win_upld_box_ht)

            upload = QPushButton("...")
            upload.clicked.connect(self.upload_files)
            upload_group.addButton(upload)
            upload_group.setId(upload, button_id)

            view = QPushButton('⤢')
            view.setEnabled(False)

            d_chan_layout.addWidget(box)
            d_chan_layout.addWidget(text)
            d_chan_layout.addWidget(upload)
            d_chan_layout.addWidget(view)

            data_button_group.addButton(box) 
            data_button_group.setId(box, button_id)

            layout.addLayout(d_chan_layout)
            button_id = button_id+1
        
        help_button = QPushButton('?')
        layout.addWidget(help_button, alignment=Qt.AlignmentFlag.AlignLeft)

        group_box = QGroupBox()
        group_box.setLayout(layout)

        return group_box, data_button_group, upload_group

    def win_create_new_layer(self, list_itr: List[str], 
                             text_label: str, exclusive: bool=True) -> (QGroupBox, QButtonGroup()):
        layout = QVBoxLayout()
        label = GroupLabel(f"<h3>{text_label}</h3>")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        button_group = QButtonGroup()
        button_group.setExclusive(exclusive)
        button_id = 0
        for button_label in list_itr:
            if exclusive:
                button = GroupRadioButton(f"{button_label}")
            else:
                button = GroupCheckBox(f"{button_label}")
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
        group_box = QGroupBox()
        group_box.setLayout(layout)
        return group_box, button_group

    def win_create_config_layer_group(self) -> QGridLayout():
        layout = QGridLayout()
        layout.addWidget(self.geo_layout, 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.source_layout, 2, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.sys_layout, 1, 0, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.chan_layout, 1, 1, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.lat_layout, 0, 1, alignment=Qt.AlignmentFlag.AlignTop)
        return layout

    def upload_files(self) -> None:
        button = self.sender()
        button_id = self.upload_group.id(button)
        text_box = self.data_layout.layout().itemAt(button_id+1).layout().itemAt(1).widget()
        file = QFileDialog.getOpenFileName(self, 'Open file', '','csv files (*.csv)')
        text_box.clear()
        if not file[0]:
            self.data_files[button_id] = None
        else:
            text_box.setText(file[0]) 
            self.data_files[button_id] = file[0]
        self.test_button_groups()

    def data_help_button_clicked(self) -> None:
        return

    def trans_button_clicked(self) -> None:
        i = 0
        for button in self.data_button_group.buttons() + self.chan_button_group.buttons():
            if button.text() in self.channels_reflec:
                button.setChecked(False)
                button.setEnabled(False)
                if i < 6:
                    text_box = self.data_layout.layout().itemAt(i+1).layout().itemAt(1).widget()
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
                    text_box = self.data_layout.layout().itemAt(i+1).layout().itemAt(1).widget()
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
        if isinstance(config, FitConfig):
            print(config)
            self.config_win = FitResults(config=config)
            self.config_win.show()
        else:
            self.error_win(message=config)
        self.run_button.setEnabled(True)  

    def get_current_inputs(self) -> Union[FitConfig, str]:
        config = FitConfig()

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
 
        config.channels = [channel for channel, data in combined_list]
        config.data = {channel: [] for channel, _ in combined_list}
        for channel, data in combined_list:
            config.data[channel] = data
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

class SimulationWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fitting")

class MainWindow(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent) 
        self.setWindowTitle("SHG_Package_Name")     

        self.layout = QVBoxLayout()
        self.img_label = QLabel()
        self.img = QPixmap(f'{REPO_DIR}/imgs/logo_full.png')
        self.img_scaled = self.img.scaled(948,198)
        self.img_label.setPixmap(self.img_scaled)

        self.fit_desc = create_fit_desc()
        self.sim_desc = create_sim_desc()
        self.sim_desc.anchorClicked.connect(self.url_click)
        self.fit_desc.anchorClicked.connect(self.url_click)
        self.package_label = GroupLabel(f'<h1>SHG_Package_Name</h1>')
        self.vers_label = GroupLabel(f"<i><font size='-1'>Version: {pkg_resources.get_distribution('shg_simulation').version}</font></i>")
        self.desc_layout = QHBoxLayout()
        self.desc_layout.addWidget(self.fit_desc)
        self.desc_layout.addWidget(self.sim_desc)
        self.package_layout = QVBoxLayout()
        self.package_layout.addWidget(self.package_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.package_layout.addWidget(self.vers_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.package_layout.addWidget(GroupLabel())

        self.help_button = QPushButton('More Information')
        self.sim_button = QPushButton('Simulation')
        self.fit_button = QPushButton('Data Fitting')
        self.sim_button.clicked.connect(self.show_simulation_win)
        self.sim_button.setEnabled(False)
        self.fit_button.clicked.connect(self.show_fitting_win)
        self.help_button.clicked.connect(self.show_help_win)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.fit_button)
        self.button_layout.addWidget(self.sim_button)
        self.button_layout.addWidget(self.help_button)
        
        self.sub_desc_layout = QHBoxLayout()
        self.sub_desc_layout.addWidget(self.fit_desc)
        self.sub_desc_layout.addWidget(self.sim_desc)

        self.desc_layout = QVBoxLayout()
        self.desc_layout.addLayout(self.package_layout)
        self.desc_layout.addLayout(self.sub_desc_layout)
        self.desc_layout.addLayout(self.button_layout)

        self.group_box = QGroupBox()
        self.group_box.setLayout(self.desc_layout)

        self.layout.addWidget(self.img_label)
        self.layout.addWidget(self.group_box)

        self.setLayout(self.layout)

        self.setFixedSize(self.layout.sizeHint())

    def show_help_win(self) -> None:
        self.win = HelpWindow()
        self.win.show()

    def show_simulation_win(self) -> None:
        return

    def show_fitting_win(self) -> None:
        self.win = FitWindow()
        self.win.show()
        self.close()

    def url_click(self, url):
        QDesktopServices.openUrl(url)

def main():
    if OS_CONFIG.invalid_os == True:
        print(f"Version {pkg_resources.get_distribution('shg_simulation').version} of SHG Simulation Package is not supported on this operating system.")
        print("Supported operating systems: Windows, macOS, and Linux.")
        return
    app = QApplication(sys.argv)
    QApplication.instance().setStyleSheet(OS_CONFIG.style_sheet)
    window = MainWindow()
    window.show()
    app.exec()
