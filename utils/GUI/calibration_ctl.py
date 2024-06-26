# -*- coding: utf-8 -*-
"""
Created on Thursday May 23 2024

@author: Baptiste Bordet
"""

import pyqtgraph
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from pylablib.core.gui.widgets import param_table, container
from test_DLS.picosdk_python_wrappers_master.ps3000aExamples import ps3000aBlockExample # change here 
from utils import constants

class Calibration(container.QFrameContainer):
    send_calibration_step=pyqtSignal()
    def setup(self):#here add the interace thread to be able to sned command via the fpga
        super().setup()
        self.setWindowTitle("Calibration Motor")
        self.setWindowFlag(QtCore.Qt.Dialog)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint,False)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint,False)
       
        self.setWindowModality(QtCore.Qt.ApplicationModal) 
        self.peaks_pos=[]
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
        self.new_win.setup()
        self.new_win.show()
        self.calib_data=[]
        self.i=0
        self.one_step_move()
        
    @pyqtSlot()    
    def one_measurement(self):
        calib_measure=ps3000aBlockExample.pico_block_aquisition()
        self.calib_data.append(calib_measure.acquire())
        self.i=self.i+1
        if self.i<=constants.Arduino_interface.MAX_ROTATION_FULL_TURN:
             self.one_step_move()
        else:  #calibration finished
            self.calib_plot.plot(self.calib_data)
            self.new_win.close()
            self.i=0
            self.calibration_treatment()
        
    def one_step_move(self):
        self.send_calibration_step.emit()
        
    def calibration_treatment(self):
        if self.i<2:
            self.peaks_pos.append(pyqtgraph.SignalProxy(self.calib_plot.scene().sigMouseClicked).scenePos())
            #TODO continue here the treatment of the claibration find peaks with half the data near peaks and find their true position 
            #TODO add also the vbar of each peak found and ask user if iot seems correct if yes print values for the calibration 
             
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