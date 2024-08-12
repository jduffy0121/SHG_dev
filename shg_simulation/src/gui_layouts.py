import pathlib
import pkg_resources
from typing import List
from PyQt6.QtCore import Qt 
from PyQt6.QtWidgets import (
    QGroupBox, QButtonGroup, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QTextEdit, QPushButton, QWidget, QTabWidget, QTableWidget, 
    QStackedLayout, QListWidget, QLineEdit, QLabel
)
from PyQt6.QtGui import QFontMetrics, QTextOption, QPixmap

from .sys_config import OS_CONFIG, PACKAGE_DIR, REPO_DIR
from .data_classes import FitManager, FitConfig
from .custom_widgets import GroupLabel, GroupRadioButton, GroupCheckBox, CustomComboBox
from .gui_html_boxes import (
    create_crystals_tab, create_visuals_tab, create_point_group_tab, create_data_help_tab,
    create_phys_background_tab, create_about_us_tab, create_vers_history,
    create_license_tab, create_sim_desc, create_fit_desc
)
from .utils import test_api_key, check_internet_connection, read_crystal_file

def fit_res_create_layout(config):
    layout = QGridLayout()

    img_label = QLabel()
    img = QPixmap(f'{REPO_DIR}/imgs/logo_mini.png')
    img_scaled = img.scaled(136,68)
    img_label.setPixmap(img_scaled)
    layout.addWidget(img_label, 0, 2, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
    
    tabs_layout = fit_res_create_table()
    layout.addWidget(tabs_layout, 0, 0, 2, 1, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

    expand_layout, swap_button_group, add_button_group = fit_res_create_expand_win(config)
    layout.addLayout(expand_layout, 1, 1, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

    plot_layout = fit_res_create_plot_win()
    layout.addWidget(plot_layout, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight)

    back_button = QPushButton("Back")
    back_button.setFixedSize(70,25)
    layout.addWidget(back_button, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)

    sel_chan_txt = QLabel(f"Selection mode: Single\nSelected channel(s): None")
    layout.addWidget(sel_chan_txt, 2, 2, alignment=Qt.AlignmentFlag.AlignRight)
    
    layout.setHorizontalSpacing(5)

    return layout, swap_button_group, add_button_group

def fit_res_create_table():
    group_box = QGroupBox()
    layout = QVBoxLayout()
    table = QTableWidget()
    table.setColumnCount(5)
    table.setHorizontalHeaderLabels(['Selected', 'Point Group', 'Fit', 'Legend', 'Parameters'])
    layout.addWidget(table)
    group_box.setLayout(layout)
    group_box.setFixedSize(525, 550)
    return group_box

def fit_res_create_expand_win(config):
    layout = QStackedLayout()
    layout_1 = QVBoxLayout()
    layout_2 = QHBoxLayout()

    group_box_1 = QGroupBox()
    visuals_button_1 = QPushButton('✹')
    visuals_button_1.setToolTip('Visualizations')
    download_button_1 = QPushButton('⤓')
    download_button_1.setToolTip('Download fit data as .csv')
    download_button_1.setEnabled(False)
    group_button_1 = QPushButton('፨')
    group_button_1.setToolTip('Point group information')
    redo_button_1 = QPushButton('↻')
    redo_button_1.setToolTip('Reset fits for all channels/point groups')
    redo_button_1.setEnabled(False)
    expand_button = QPushButton('>')
    expand_button.setToolTip('Show plot manager')
    layout_1.addWidget(visuals_button_1, alignment=Qt.AlignmentFlag.AlignBottom)
    layout_1.addWidget(download_button_1, alignment=Qt.AlignmentFlag.AlignBottom)
    layout_1.addWidget(group_button_1, alignment=Qt.AlignmentFlag.AlignBottom)
    layout_1.addWidget(redo_button_1, alignment=Qt.AlignmentFlag.AlignBottom)
    layout_1.addWidget(expand_button, alignment=Qt.AlignmentFlag.AlignBottom)
    group_box_1.setLayout(layout_1)
    group_box_1.setFixedSize(50,200)
    close_widget = QWidget()
    close_layout = QVBoxLayout()
    close_layout.addWidget(group_box_1, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
    close_widget.setLayout(close_layout)
    layout.addWidget(close_widget)

    expand_layout = QVBoxLayout()
    header_label = GroupLabel('Manage plots')
    expand_layout.addWidget(header_label, alignment=Qt.AlignmentFlag.AlignCenter)

    swap_button_group = QButtonGroup()
    add_button_group = QButtonGroup()
    button_id = 0
    for channel in config.channels:
        sub_layout = QHBoxLayout()
        if channel == "Parallel":
            label = GroupLabel('||')
        elif channel == "Perpendicular":
            label = GroupLabel('⊥')
        else:
            label = GroupLabel(f'{channel}')
        sub_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignRight)
        button_layout = QVBoxLayout()
        add_button = QPushButton('+')
        add_button.setToolTip('Add plot')
        add_button_group.addButton(add_button)
        add_button_group.setId(add_button, button_id)
        button_layout.addWidget(add_button)
        swap_button = QPushButton('⇆')
        swap_button.setToolTip('Swap with current selected (only works with single selection)')
        swap_button_group.addButton(swap_button)
        swap_button_group.setId(swap_button, button_id)
        button_layout.addWidget(swap_button)
        button_layout.setSpacing(3)
        sub_layout.addLayout(button_layout)
        expand_layout.addLayout(sub_layout)
        button_id = button_id + 1

    data_color_label = GroupLabel('Choose data points color')
    data_color_box = CustomComboBox()
    data_color_box.addItems(['Blue', 'Red', 'Green', 'Orange', 'Purple', 'Brown'])
    selection_mode_label = GroupLabel('Choose selection mode')
    selection_mode_box = CustomComboBox()
    selection_mode_box.addItems(['Single', 'Multiple'])

    expand_layout.addWidget(data_color_label, alignment=Qt.AlignmentFlag.AlignCenter)
    expand_layout.addWidget(data_color_box)
    expand_layout.addWidget(selection_mode_label, alignment=Qt.AlignmentFlag.AlignCenter)
    expand_layout.addWidget(selection_mode_box)

    close_button_layout = QVBoxLayout()
    visuals_button_2 = QPushButton('✹')
    visuals_button_2.setToolTip('Visualizations')
    download_button_2 = QPushButton('⤓')
    download_button_2.setToolTip('Download fit data as .csv')
    download_button_2.setEnabled(False)
    group_button_2 = QPushButton('፨')
    group_button_2.setToolTip('Point group information')
    redo_button_2 = QPushButton('↻')
    redo_button_2.setToolTip('Reset fits for all channels/point groups')
    redo_button_2.setEnabled(False)
    retract_button = QPushButton('<')
    retract_button.setToolTip('Hide plot manager')
    group_box_2 = QGroupBox()
    group_box_2.setLayout(expand_layout)
    group_box_2.setFixedWidth(200)

    group_box_3 = QGroupBox()
    close_button_layout.addWidget(visuals_button_2, alignment=Qt.AlignmentFlag.AlignBottom )
    close_button_layout.addWidget(download_button_2, alignment=Qt.AlignmentFlag.AlignBottom)
    close_button_layout.addWidget(group_button_2, alignment=Qt.AlignmentFlag.AlignBottom)
    close_button_layout.addWidget(redo_button_2, alignment=Qt.AlignmentFlag.AlignBottom)
    close_button_layout.addWidget(retract_button, alignment=Qt.AlignmentFlag.AlignBottom)
    group_box_3.setLayout(close_button_layout)
    group_box_3.setFixedSize(50,200)

    expand_widget = QWidget()
    layout_2.addWidget(group_box_3, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
    layout_2.addWidget(group_box_2, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
    expand_widget.setLayout(layout_2)

    layout.addWidget(expand_widget)
    
    return layout, swap_button_group, add_button_group

def fit_res_create_plot_win():
    layout = QVBoxLayout()

    label = GroupLabel(f"Select plots to continue")
    layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

    group_box = QGroupBox()
    group_box.setLayout(layout)
    
    group_box.setFixedSize(420,460)
    return group_box

def fit_inp_create_layout(): #Sets the primary layout for FitInput() window
    layout = QGridLayout()
    sub_layout = QHBoxLayout()
    
    #Creates and adds header/img to the layout
    header_label = QLabel("<h1>Import Data for Fit</h1>") 
    img_label = QLabel()
    img = QPixmap(f'{REPO_DIR}/imgs/logo_mini.png')
    img_scaled = img.scaled(136,68)
    img_label.setPixmap(img_scaled)
    layout.addWidget(header_label, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(img_label, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)
    
    #Creates and add file upload to the layout
    file_upload, data_button_group, upload_button_group, full_button_group = fit_inp_create_file_upload()
    layout.addWidget(file_upload, 1, 0, 3, 1)

    #Creates and add the config boxes to the layout
    geo_layout, geo_button_group = fit_inp_create_new_config(list_itr=["Transmission", "Reflection"],
                                                             text_label="Geometry")
    chan_layout, chan_button_group = fit_inp_create_new_config(list_itr=["||", "⊥", "SS", "PP", "SP", "PS"],
                                                               text_label="Channels", exclusive=False)
    source_layout, source_button_group = fit_inp_create_new_config(list_itr=["Electric Dipole", "Electric Quadrupole", "Magnetic Dipole"],
                                                                    text_label="Source")
    system_layout, system_button_group = fit_inp_create_new_config(list_itr=["Triclinic", "Monoclinic", "Orthorhombic", "Tetragonal", "Trigonal", "Hexagonal", "Cubic"],
                                                                    text_label="System")
    planes_layout, planes_button_group = fit_inp_create_new_config(list_itr=["(0 0 1)", "Rotz(90°)"], text_label="Lattice Plane")
    layout.addWidget(geo_layout, 1, 1)
    layout.addWidget(planes_layout, 1, 2)
    layout.addWidget(system_layout, 2, 1)
    layout.addWidget(chan_layout, 2, 2)
    layout.addWidget(source_layout, 3, 1, 1, 2)

    back_button = QPushButton("Back")
    back_button.setFixedSize(70,22)
    run_button = QPushButton("Run")
    run_button.setEnabled(False)
    run_button.setFixedSize(70,22)
    
    layout.addWidget(back_button, 5, 0, alignment=Qt.AlignmentFlag.AlignLeft)
    layout.addWidget(run_button, 5, 2, alignment=Qt.AlignmentFlag.AlignRight)

    return (layout, data_button_group, upload_button_group, full_button_group, 
            geo_button_group, chan_button_group, source_button_group, 
            system_button_group, planes_button_group)

def fit_inp_create_file_upload() -> (QGroupBox, QButtonGroup, QButtonGroup, QButtonGroup): #Creates file input layer for FitInput()
    layout = QGridLayout()
    sub_layout = QVBoxLayout()

    label = GroupLabel("<h3>File Upload</h3>")
    layout.addWidget(label, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

    data_button_group = QButtonGroup()
    upload_button_group = QButtonGroup()
    full_button_group = QButtonGroup()
    data_button_group.setExclusive(False)
    
    button_id = 0
    #Iterates through all chan and creates a file uploader layer (check_box, text_box, upload_file_button, full_plot_button)
    for chan in ["||", "⊥", "SS", "PP", "SP", "PS"]:
        chan_layout = QHBoxLayout()
        if chan == '||':
            box = GroupCheckBox(f"{chan}   ")
        elif chan == '⊥':
            box = GroupCheckBox(f"{chan}  ")
        else:
            box = GroupCheckBox(f"{chan}")
        chan_layout.addWidget(box)
        data_button_group.addButton(box)
        data_button_group.setId(box, button_id)

        text = QTextEdit()
        text.setReadOnly(True)
        font_metrics = QFontMetrics(text.font())
        line_height = font_metrics.lineSpacing()
        text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        text.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        text.setFixedSize(OS_CONFIG.fit_win_upld_box_len, line_height + OS_CONFIG.fit_win_upld_box_ht)
        chan_layout.addWidget(text)

        upload = QPushButton("...")
        upload.setFixedSize(22,22)
        upload.setToolTip("Upload channel data file")
        upload_button_group.addButton(upload)
        upload_button_group.setId(upload, button_id)
        chan_layout.addWidget(upload)
        
        full = QPushButton('⤢')
        full.setFixedSize(22,22)
        full.setEnabled(False)
        full.setToolTip("View data as a polar plot in a new window")
        full_button_group.addButton(full)
        full_button_group.setId(full, button_id)
        chan_layout.addWidget(full)
        
        sub_layout.addLayout(chan_layout)

        button_id = button_id + 1

    layout.addLayout(sub_layout, 1, 0, 1, 2)
    help_button = QPushButton('?')
    help_button.setFixedSize(22,22)
    help_button.setToolTip('How to format data files')
    check_box = GroupCheckBox('Data files contain column headers')
    layout.addWidget(help_button, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
    layout.addWidget(check_box, 2, 1, alignment=Qt.AlignmentFlag.AlignRight)
    
    group_box = QGroupBox()
    group_box.setLayout(layout)

    return group_box, data_button_group, upload_button_group, full_button_group

def fit_inp_create_new_config(list_itr: List[str], 
                              text_label: str, exclusive: bool=True) -> (QGroupBox, QButtonGroup): #Creates new config box
    layout = QVBoxLayout()
    label = GroupLabel(f"<h3>{text_label}</h3>")
    layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

    button_group = QButtonGroup()
    button_group.setExclusive(exclusive)

    button_id = 0
    for button_label in list_itr:
        if exclusive:
            button = GroupRadioButton(f"{button_label}")
        else:
            button = GroupCheckBox(f"{button_label}")
        layout.addWidget(button, Qt.AlignmentFlag.AlignBottom)
        button_group.addButton(button)
        button_group.setId(button, button_id)

        button_id = button_id + 1

    group_box = QGroupBox()
    group_box.setLayout(layout)
    return group_box, button_group

def sim_crystal_remove_layout() -> QVBoxLayout:
    layout = QVBoxLayout()
    sub_layout = QHBoxLayout()

    selection_table = QListWidget()
    selection_table.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
    selection_table.addItems(["Unary", "Binary", "Tertiary"])
    sub_layout.addWidget(selection_table)
    
    selection_layout = sim_create_crystal_table()
    sub_layout.addLayout(selection_layout)

    group_box = QGroupBox()
    group_box.setLayout(sub_layout)
    layout.addWidget(group_box)

    remove_button = QPushButton("Remove selected crystal")
    remove_button.setFixedHeight(22)
    remove_button.setEnabled(False)

    layout.addWidget(remove_button)

    return layout

def sim_key_upload_layout() -> QVBoxLayout:
    layout = QVBoxLayout()
    sub_layout = QVBoxLayout()
    box = QLineEdit()
    button = QPushButton("Upload")
    sub_layout.addWidget(box)
    sub_layout.addWidget(button)
    group_box = QGroupBox()
    group_box.setLayout(sub_layout)
    layout.addWidget(group_box)
    return layout

def sim_crystal_add_layout() -> (QVBoxLayout, QButtonGroup, QButtonGroup):
    layout = QGridLayout()
    types_layout = QVBoxLayout()
    method_layout = QVBoxLayout()
    box_layout = QStackedLayout()
    button_layout = QHBoxLayout()

    crystal_type_button_group = QButtonGroup()
    i = 0
    for label in ['Unary', 'Binary', 'Tertiary']:
        button = GroupRadioButton(f"{label}")
        crystal_type_button_group.addButton(button)
        crystal_type_button_group.setId(button, i)
        types_layout.addWidget(button)
        i = i + 1

    search_type_button_group = QButtonGroup()
    i = 0
    for label in ['Name','Formula']:
        button = GroupRadioButton(f"{label}")
        search_type_button_group.addButton(button)
        search_type_button_group.setId(button, i)
        method_layout.addWidget(button)
        i = i + 1

    crystal_type_button_group.button(0).setChecked(True) 
    search_type_button_group.button(0).setChecked(True)

    group_box_1 = QGroupBox()
    group_box_1.setLayout(types_layout)
    layout.addWidget(group_box_1, 0, 0)

    group_box_2 = QGroupBox()
    group_box_2.setLayout(method_layout)
    layout.addWidget(group_box_2, 1, 0)

    internet_connection = check_internet_connection()

    unary_boxes = sim_add_create_box_layout(num_of_boxes=1)
    binary_boxes = sim_add_create_box_layout(num_of_boxes=2)
    tertiary_boxes = sim_add_create_box_layout(num_of_boxes=3)
    box_layout.addWidget(unary_boxes)
    box_layout.addWidget(binary_boxes)
    box_layout.addWidget(tertiary_boxes)
    layout.addLayout(box_layout, 0, 1, 3, 1)
    
    add_button = QPushButton("Add Crystal Results")
    add_button.setFixedHeight(22)
    search_button = QPushButton("Search Materials Project Database")
    search_button.setFixedHeight(22)
    key_button = QPushButton("⚿")
    key_button.setFixedSize(22,22)
    key_button.setToolTip("Upload Materials Project API Key")
    help_button = QPushButton("?")
    help_button.setToolTip("How to format input")
    help_button.setFixedSize(22,22)
    button_layout.addWidget(help_button)
    button_layout.addWidget(key_button)
    button_layout.addWidget(search_button)
    button_layout.addWidget(add_button)
    layout.addLayout(button_layout, 3, 0, 1, 2)

    internet_connection = check_internet_connection()
    
    group_box_3 = QGroupBox()
    config_layout = QVBoxLayout()
    add_button.setEnabled(False)
    if not internet_connection:
        search_button.setEnabled(False)
        key_button.setEnabled(False)
        internet_label = GroupLabel('Internet: <span style="color: red;">Not Connected</span>')
        key_label = GroupLabel('API Key: <span style="color: red;">None</span>')
    else:
        internet_label = GroupLabel('Internet: <span style="color: green;">Connected</span>')
        if not test_api_key():
            search_button.setEnabled(False)
            key_label = GroupLabel('API Key: <span style="color: red;">None</span>')
        else:
            key_label = GroupLabel('API Key: <span style="color: green;">Valid</span>')

    config_layout.addWidget(internet_label)
    config_layout.addWidget(key_label)
    group_box_3.setLayout(config_layout)
    layout.addWidget(group_box_3, 2, 0)

    return layout, crystal_type_button_group, search_type_button_group

def sim_add_create_box_layout(num_of_boxes: int) -> QGroupBox:
    layout = QVBoxLayout()
    sub_layout = QHBoxLayout()
    search_label = GroupLabel("Crystal:")
    sub_layout.addWidget(search_label)
    for i in range(num_of_boxes):
        box = QLineEdit()
        sub_layout.addWidget(box)
    layout.addLayout(sub_layout)
    table = QTableWidget()
    table.setColumnCount(5)
    table.setHorizontalHeaderLabels(['Material', 'Formula', 'Id', 'Space Group', 'Add'])
    results_label = GroupLabel("Results")
    layout.addWidget(results_label, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(table)
    group_box = QGroupBox()
    group_box.setLayout(layout)

    return group_box

def sim_create_layout() -> QGridLayout:
    layout = QGridLayout()
    sub_layout = QGridLayout()
    button_layout = QVBoxLayout()
    
    header_label = QLabel("<h1>Select crystal</h1>") 
    img_label = QLabel()
    img = QPixmap(f'{PACKAGE_DIR}/imgs/logo_mini.png')
    img_scaled = img.scaled(136,68)
    img_label.setPixmap(img_scaled)

    layout.addWidget(header_label, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(img_label, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)


    selection_table = QListWidget()
    selection_table.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
    selection_table.addItems(["Unary", "Binary", "Tertiary"])
    sub_layout.addWidget(selection_table, 0, 0)

    selection_layout = sim_create_crystal_table()
    sub_layout.addLayout(selection_layout, 0, 1)
    
    add_button = QPushButton("+")
    add_button.setFixedSize(22,22)
    add_button.setToolTip("Add additional crystals")
    remove_button = QPushButton("✕")
    remove_button.setFixedSize(22,22)
    remove_button.setToolTip("Remove crystals")
    reconfig_button = QPushButton('♲')
    reconfig_button.setFixedSize(22,22)
    reconfig_button.setToolTip("Delete custom crystal data")

    button_layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)
    button_layout.addWidget(remove_button, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)
    button_layout.addWidget(reconfig_button, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)
    sub_layout.addLayout(button_layout, 0, 2, alignment=Qt.AlignmentFlag.AlignLeft)
    
    group_box = QGroupBox()
    group_box.setLayout(sub_layout)
    layout.addWidget(group_box, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

    back_button = QPushButton("Back")
    back_button.setFixedSize(70,22)
    run_button = QPushButton("Run")
    run_button.setEnabled(False)
    run_button.setFixedSize(70,22)
    layout.addWidget(back_button, 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
    layout.addWidget(run_button, 2, 1, alignment=Qt.AlignmentFlag.AlignRight)
    
    return layout

def sim_create_crystal_table() -> QStackedLayout:
    layout = QStackedLayout()    

    if pathlib.Path(f'{PACKAGE_DIR}/data/custom_crystals.yaml').exists():
        data = read_crystal_file(file_path = f'{PACKAGE_DIR}/data/custom_crystals.yaml')
    else:
        data = read_crystal_file(file_path = f'{PACKAGE_DIR}/data/default_crystals.yaml')

    unary_list = [f'{crystal["name"]} ({crystal["symbol"]})' for crystal in data if crystal['structure'] == 'Unary']
    binary_list = [f'{crystal["name"]} ({crystal["symbol"]})' for crystal in data if crystal['structure'] == 'Binary']
    tertiary_list = [f'{crystal["name"]} ({crystal["symbol"]})' for crystal in data if crystal['structure'] == 'Tertiary']
    
    unary_table = QListWidget()
    unary_table.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
    unary_table.addItems(unary_list)
    
    binary_table = QListWidget()
    binary_table.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
    binary_table.addItems(binary_list)

    tertiary_table = QListWidget()
    tertiary_table.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
    tertiary_table.addItems(tertiary_list)
        
    layout.addWidget(unary_table)
    layout.addWidget(binary_table)
    layout.addWidget(tertiary_table)

    return layout

def main_create_layout() -> QVBoxLayout:
    layout = QVBoxLayout()
    sub_layout = QGridLayout()
    button_layout = QHBoxLayout()

    img_label = QLabel()
    img = QPixmap(f'{PACKAGE_DIR}/imgs/logo_full.png')
    img_scaled = img.scaled(948,198)
    img_label.setPixmap(img_scaled)
    layout.addWidget(img_label)
    
    package_label = GroupLabel(f'<h1>SHG_Package_Name</h1>')
    vers_label = GroupLabel(f'<i><font size="-1">Version:{pkg_resources.get_distribution("shg_simulation").version}</font></i><br>')
    sub_layout.addWidget(package_label, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
    sub_layout.addWidget(vers_label, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

    fit_desc = create_fit_desc()
    sim_desc = create_sim_desc()
    sub_layout.addWidget(fit_desc, 2, 0)
    sub_layout.addWidget(sim_desc, 2, 1)

    fit_button = QPushButton('Data Fitting')
    sim_button = QPushButton('Simulation')
    more_button = QPushButton('More Information')
    fit_button.setFixedHeight(22)
    sim_button.setFixedHeight(22)
    more_button.setFixedHeight(22)

    button_layout.addWidget(fit_button)
    button_layout.addWidget(sim_button)
    button_layout.addWidget(more_button)
    sub_layout.addLayout(button_layout, 3, 0, 1, 2)
    
    group_box = QGroupBox()
    group_box.setLayout(sub_layout)
    layout.addWidget(group_box)
    return layout

def more_window_layout() -> QVBoxLayout:
    layout = QVBoxLayout()
    tabs = QTabWidget()
    phys_background = create_phys_background_tab(img=f'{PACKAGE_DIR}/imgs/prev.png')
    about_us = create_about_us_tab()
    version_hist = create_vers_history(file=f'{REPO_DIR}/updates.txt')
    license_tab = create_license_tab(file=f'{REPO_DIR}/LICENSE')
    tabs.addTab(phys_background, 'RA-SHG')
    tabs.addTab(about_us, 'About Us')
    tabs.addTab(version_hist, 'Versions History')
    tabs.addTab(license_tab, 'License Agreement')
    layout.addWidget(tabs)
    return layout

def data_help_layout() -> QVBoxLayout:
    layout = QVBoxLayout()
    help_win = create_data_help_tab()
    layout.addWidget(help_win)
    return layout

def point_group_win_layout() -> QVBoxLayout:
    layout = QVBoxLayout()
    group_win = create_point_group_tab()
    layout.addWidget(group_win)
    return layout 

def visuals_win_layout() -> QVBoxLayout:
    layout = QVBoxLayout()
    vis_win = create_visuals_tab()
    layout.addWidget(vis_win)
    return layout

def crystals_win_layout() -> QVBoxLayout:
    layout = QVBoxLayout()
    crystal_win = create_crystals_tab()
    layout.addWidget(crystal_win)
    return layout
