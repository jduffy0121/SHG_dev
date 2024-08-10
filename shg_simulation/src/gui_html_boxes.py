import pathlib
import markdown
from urllib.parse import quote
from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtCore import Qt 

def create_crystals_tab() -> QTextBrowser:
    txt_box = QTextBrowser()
    txt_box.setReadOnly(True)
    txt_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    txt_box.setOpenLinks(False)

    html_content = f'''
    <h1>Materials Project Database</h1>
    '''
    txt_box.setHtml(html_content)
    
    return txt_box
   

def create_visuals_tab() -> QTextBrowser:
    txt_box = QTextBrowser()
    txt_box.setReadOnly(True)
    txt_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    txt_box.setOpenLinks(False)

    html_content = f'''
    <h1>Visualizations</h1>
    '''
    txt_box.setHtml(html_content)
    
    return txt_box

def create_point_group_tab() -> QTextBrowser:
    txt_box = QTextBrowser()
    txt_box.setReadOnly(True)
    txt_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    txt_box.setOpenLinks(False)

    html_content = f'''
    <h1>Point Groups</h1>
    '''
    txt_box.setHtml(html_content)
    
    return txt_box

def create_data_help_tab() -> QTextBrowser:
    txt_box = QTextBrowser()
    txt_box.setReadOnly(True)
    txt_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    txt_box.setOpenLinks(False)

    html_content = f'''
    <h1>How to Format Data Files</h1>
    <p>
    Data files needs to be formatted in a <b>two column .csv file</b> where column one represents theta (or phi) and column two 
    represents the measured intensity.
    </p>
    <p>
    <table style="width:100%">
        <tr>
            <th>Theta</th>
            <th>Intensity</td>
        </tr>
        <tr>
            <td>θ<sub>1</sub></td>
            <td>I<sub>1</sub></td>
        </tr>
        <tr>
            <td>θ<sub>2</sub></td>
            <td>I<sub>2</sub></td>
        </tr>
        <tr>
            <td>.</td>
            <td>.</td>
        </tr>
        <tr>
            <td>.</td>
            <td>.</td>
        </tr>
        <tr>
            <td>.</td>
            <td>.</td>
        </tr>
        <tr>
            <td>θ<sub>n</sub></td>
            <td>I<sub>n</sub></td>
        </tr>
    </table>
    </p>
    <p>
    All other columns in the file <b>must be empty</b>. Also, if any row that is <b>missing an element</b> or an 
    element has a <b>text value instead of a float</b>, this will cause an error and the program will not be able to continue.
    </p>
    <p>
    Files can have column headers as long as the option is selected. What these data headers are irreverent and will not be referenced by
    the program.
    </p>
    '''
    txt_box.setHtml(html_content)
    
    return txt_box

def create_license_tab(file: pathlib.Path) -> QTextBrowser:
    txt_box = QTextBrowser()
    txt_box.setReadOnly(True)
    txt_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    txt_box.setOpenLinks(False)

    with open(file, 'r', encoding='utf-8') as file:
        txt = file.read()
        txt_box.setText(txt)
    file.close()
    
    return txt_box

def create_phys_background_tab(img: pathlib.Path) -> QTextBrowser:
    txt_box = QTextBrowser()
    txt_box.setReadOnly(True)
    txt_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    txt_box.setOpenLinks(False)

    img_quote = f'file://{quote(img)}'

    html_content = f'''
    <h1>Rotational-Anisotropic Second-Harmonic Generation (RA-SHG)</h1>
    <p><img src="{img_quote}" alt="Sample Image" width="400"></p>
    '''
    txt_box.setHtml(html_content)
    
    return txt_box

def create_about_us_tab() -> QTextBrowser: 
    txt_box = QTextBrowser()
    txt_box.setReadOnly(True)
    txt_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    txt_box.setOpenLinks(False)

    html_content = f'''
    <h1>Ultrafast Nonlinear Optics Group</h1>
    <p>This program was created by the <a href= https://jinlab.auburn.edu> Ultrafast Nonlinear Optics (UNO) Research Group</a> at Auburn University's Physics Department.</p>
    <p>
    Our group focuses on studying novel phases of matter in low-dimensional 
    quantum systems. We exploit a variety of experimental techniques such as 
    femtosecond laser-based nonlinear optical spectroscopy and synchrotron-based photoemission 
    spectroscopy/microscopy to investigate the electronic and magnetic structures at 
    surfaces and interfaces.
    </p>
    <h1>Creators</h1>
    <p>This program was created by:</p>
    <ul>
        <li>Jacob Duffy (Auburn University – Physics and Computer Science Departments: <a href=mailto:jod0007@auburn.edu)> jod0007@auburn.edu</a>)</li>
        <li>Hussam Mustafa (Auburn University – Physics Department: <a href=mailto: hnm0037@auburn.edu> hnm0037@auburn.edu</a>)</li>
        <li>Chunli Tang (Auburn University – Electrical and Computer Engineering Department: <a href=mailto: chunli.tang@auburn.edu> chunli.tang@auburn.edu</a>)</li>
    </ul> 
    <h1>Acknowledgements</h1>
    <p>
    We would like to give special acknowledgement to <b>Brian Opatosky (Auburn University – Physics Department: <a href=mailto: bbo0007@auburn.edu> bbo0007@auburn.edu</a>)</b> 
    for his assistance with deriving the fitting functions for each point group used in this program.
    </p>
    <p>
    Finally, we would like to give special apperication to our advisor <b><a href= https://www.auburn.edu/cosam/departments/physics/physics-faculty/jin/index.htm> 
    Dr. Wencan Jin</a> (Auburn University – Physics Department: <a href=mailto:wjin@auburn.edu> wjin@auburn.edu</a>)</b> for all the support and 
    assistance in creating this program.
    </p>
    '''
    txt_box.setHtml(html_content)
    
    return txt_box

def create_fit_desc() -> QTextBrowser:
    txt_box = QTextBrowser()
    txt_box.setReadOnly(True)
    txt_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    txt_box.setOpenLinks(False)

    html_content = f'''
    <h2>Data Fitting</h2>
    '''
    txt_box.setHtml(html_content)
    return txt_box

def create_sim_desc() -> QTextBrowser:
    txt_box = QTextBrowser()
    txt_box.setReadOnly(True)
    txt_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    txt_box.setOpenLinks(False)

    html_content = f'''
    <h2>Simulation</h2>
    '''
    txt_box.setHtml(html_content)

    return txt_box

def create_vers_history(file: pathlib.Path) -> QTextBrowser:
    txt_box = QTextBrowser()
    txt_box.setReadOnly(True)
    txt_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    txt_box.setOpenLinks(False)

    with open(f"{file}", "r") as file:
        markdown_content = file.read()

    file.close()

    html_content = markdown.markdown(markdown_content)
    txt_box.setHtml(html_content)

    return txt_box
