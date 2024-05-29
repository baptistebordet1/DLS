# -*- coding: utf-8 -*-
"""
Created on Thursday May 23 2024

@author: Baptiste Bordet
"""

import pyqtgraph
from PyQt5 import QtWidgets, QtCore
from pylablib import widgets
from pylablib.core.gui.widgets import param_table, container
import time

class Calibration(container.QFrameContainer):
    def setup(self):
        super().setup()
        self.setWindowTitle("Calibration Motor")
        self.setWindowFlag(QtCore.Qt.Dialog)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint,False)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint,False)
       
        self.setWindowModality(QtCore.Qt.ApplicationModal) 
        with self.using_new_sublayout("windows", "hbox"):
            self.calib_plot=self.add_to_layout(pyqtgraph.PlotWidget(self))
            self.calib_plot.showGrid(True,True,0.7)
            self.calib_plot.setLabel("left","Photodiode Voltage (V)")
            self.calib_plot.setLabel("bottom","Motor Position (in motor steps)")
            self.calib_plot.setMinimumHeight(500)
            self.calib_plot.setMinimumWidth(500)
            self.params=self.add_child("window",param_table.ParamTable(self))
            self.params.setup(add_indicator=False)
            self.params.add_button("start_calib",caption="Start Calibration")  
            self.params.w["start_calib"].clicked.connect(self.start_calibration)
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
    def start_calibration(self):
        self.new_win=waiting_window_calibration(self)
        self.new_winsetup()
        self.new_win.show()
        
        #To add methods to run calibrationon thread call waiting window close window at the end 
        
class waiting_window_calibration(container.QFrameContainer):
    def setup(self):
        super().setup()
        self.setWindowTitle("Calibration in progress")
        self.setWindowFlag(QtCore.Qt.Dialog)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint,False)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint,False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint,False)
        self.setWindowModality(QtCore.Qt.WindowModal) 
        self.add_decoration_label("Calibration in progress, please wait...")
        self.show()
    def close_window(self):
        self.close()