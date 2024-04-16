# -*- coding: utf-8 -*-
"""
Created on Friday February 2 2024

@author: Baptiste Bordet
"""

import qdarkstyle
import re

def load_style(style):
    """
    Function adapted from : https://github.com/AlexShkarin/pyLabLib-cam-control
    Load color theme style.
    
    Can be ``"standard"`` (default OS style), ``"dark"`` (qdarkstyle dark), or ``"light"`` (qdarkstyle light).
    """
    if style=="standard":
        return ""
    palette=qdarkstyle.DarkPalette if style=="dark" else qdarkstyle.LightPalette
    accent_color="#406482" if style=="dark" else "#94c1e0"
    accent_hover_color="#254f73" if style=="dark" else "#5a96bf"
    checked_style="\n\nQPushButton:checked {{background-color: {};}}\n\nQPushButton:checked:hover {{background-color: {};}}".format(accent_color,accent_hover_color)
    stylesheet=qdarkstyle.load_stylesheet(qt_api="pyqt5",palette=palette)
    m=re.search(r"QPushButton:checked\s*{[^}]*}",stylesheet,flags=re.DOTALL)
    end=m.span()[1]
    stylesheet=stylesheet[:end]+checked_style+stylesheet[end:]
    return stylesheet

def set_style(app,style="dark"):
   """
    Set stylesheet to the app 

    Parameters
    ----------
    app : TYPE
        DESCRIPTION.
    style : TYPE, optional
        DESCRIPTION. The default is "dark".

    Returns
    -------
    app : TYPE
        DESCRIPTION.
    """
   stylesheet=load_style(style)
   app.setStyleSheet(stylesheet)
   return app 
    

"""
Below is an example for file dialogs windows by default are oppenned with OS style 
# from PyQt5.QtWidgets import QFileDialog

# dialog = QFileDialog(window) # works if window has the right stylesheet already
# dialog.show()


"""

import sys
import qdarkstyle
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog

# create the application and the main window
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()

# setup stylesheet
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
# or in new API
app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

dialog=QFileDialog(window)
dialog.show()
# run
window.show()
app.exec_()
