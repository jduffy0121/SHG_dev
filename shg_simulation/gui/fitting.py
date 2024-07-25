from .gui_classes import *
from PyQt6.QtWidgets import (
    QWidget, QCheckBox, QVBoxLayout, QButtonGroup, QTabWidget, 
    QComboBox, QTableWidget, QTableWidgetItem, QLabel
)

def win_create_fit_tabs_layer(config: SimInputConfig) -> (QVBoxLayout(), QButtonGroup(), ComboBoxGroup()):
    layout = QVBoxLayout()
    tabs = QTabWidget()
    tabs.setTabPosition(QTabWidget.TabPosition.North)
    tabs.setMovable(False)

    tab1 = QWidget()
    tab1_layout = QVBoxLayout()
    txt1 = QLabel("Best Fits", alignment=Qt.AlignmentFlag.AlignCenter)

    fit_table = QTableWidget()
    fit_table.setRowCount(10)
    fit_table.setColumnCount(4)
    fit_table.setHorizontalHeaderLabels(['Selected', 'Point Group', 'Fit', 'Legend'])
    fit_check_group = QButtonGroup()
    legend_group = ComboBoxGroup()
    fit_check_group.setExclusive(False)

    point_group, fit_results = get_fit_results(config=config)

    for i in range(10):
        check_box = QCheckBox()
        fit_table.setCellWidget(i, 0, check_box)
        point_group = QTableWidgetItem("D3")
        fit_results = QTableWidgetItem("0.99")
        point_group.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        fit_results.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        fit_table.setItem(i, 1, point_group)
        fit_table.setItem(i, 2, fit_results)
        box = QComboBox()
        box.addItems(['Blue', 'Red', 'Green', 'Black', 'Yellow',
                      'Orange', 'Purple', 'Brown', 'Pink', 'Navy'])
        box.setCurrentIndex(i)
        legend_group.addComboBox(box)
        fit_check_group.addButton(check_box)

        fit_table.setCellWidget(i, 3, box)
    fit_table.horizontalHeader().setStretchLastSection(True)
    tab1_layout.addWidget(txt1)
    tab1_layout.addWidget(fit_table)
    tab1.setLayout(tab1_layout)

    tab2 = QWidget()
    tab2_layout = QVBoxLayout()
    txt2 = QLabel("Fit Manipulations", alignment=Qt.AlignmentFlag.AlignCenter)
    tab2_layout.addWidget(txt2)
    tab2.setLayout(tab2_layout)

    tab3 = QWidget()
    tab3_layout = QVBoxLayout()
    txt3 = QLabel("Plot Visualization", alignment=Qt.AlignmentFlag.AlignCenter)
    tab3_layout.addWidget(txt3)
    tab3.setLayout(tab3_layout)

    tabs.addTab(tab1, "Best Fits")
    tabs.addTab(tab2, "Fit Manipulations")
    tabs.addTab(tab3, "Plot Visualization")

    layout.addWidget(tabs)

    return layout, fit_check_group, legend_group

def func_dict():
    pass

def get_fit_results(config: SimInputConfig):
    return None, None
