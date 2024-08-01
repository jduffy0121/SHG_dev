import pathlib
from urllib.parse import quote
from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtCore import Qt 

def create_about_us_tab(img: pathlib.Path) -> QTextBrowser: 
    txt_box = QTextBrowser()
    txt_box.setReadOnly(True)
    txt_box.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    txt_box.setOpenLinks(False)

    img_quote = f'file://{quote(img)}'

    html_content = f'''
    <h1>Ultrafast Nonlinear Optics Group</h1>
    <p>It's paragraph time with <b>bold</b>, <i>italic</i>, and <u>underlined</u> text.</p>
    <p>I like list more!</p>
    <ul>
        <li>Ok</li>
        <li>Then</li>
        <li>Bud</li>
    </ul> 
    <p><img src="{img_quote}" alt="Sample Image" width="400"></p>
    <p>Url is <a href=https://auburn.edu>here</a>, super secret tho!</p>
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
    <p>It's paragraph time with <b>bold</b>, <i>italic</i>, and <u>underlined</u> text.</p>
    <p>I like list more!</p>
    <ul>
        <li>Ok</li>
        <li>Then</li>
        <li>Bud</li>
    </ul> 
    <p>Url is <a href=https://auburn.edu>here</a>, super secret tho!</p>
    <p>It's paragraph time with <b>bold</b>, <i>italic</i>, and <u>underlined</u> text.</p>
    <p>I like list more!</p>
    <ul>
        <li>Ok</li>
        <li>Then</li>
        <li>Bud</li>
    </ul> 
    <p>Url is <a href=https://auburn.edu>here</a>, super secret tho!</p>
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
    <p>It's paragraph time with <b>bold</b>, <i>italic</i>, and <u>underlined</u> text.</p>
    <p>I like list more!</p>
    <ul>
        <li>Ok</li>
        <li>Then</li>
        <li>Bud</li>
    </ul> 
    <p>Url is <a href=https://auburn.edu>here</a>, super secret tho!</p>
    <p>It's paragraph time with <b>bold</b>, <i>italic</i>, and <u>underlined</u> text.</p>
    <p>I like list more!</p>
    <ul>
        <li>Ok</li>
        <li>Then</li>
        <li>Bud</li>
    </ul> 
    <p>Url is <a href=https://auburn.edu>here</a>, super secret tho!</p>
    '''
    txt_box.setHtml(html_content)
    return txt_box
