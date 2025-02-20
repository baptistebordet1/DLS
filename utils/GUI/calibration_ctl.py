# -*- coding: utf-8 -*-
"""
Created on Thursday May 23 2024

@author: Baptiste Bordet
"""

import pyqtgraph
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer
from pylablib.core.gui.widgets import param_table, container
from test_DLS.picosdk_python_wrappers_master.ps3000aExamples import ps3000aBlockExample # change here 
from utils import constants
import time

import numpy as np

class Calibration(container.QFrameContainer):
    send_calibration_step=pyqtSignal()
    def setup(self):#here add the interace thread to be able to sned command via the fpga
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
        self.new_win.setup()
        self.new_win.show()
        self.calib_data=[]
        self.peaks_pos=[]
        self.motor_positions=[]
        self.i=0
        self.calib_measure=ps3000aBlockExample.pico_block_aquisition()
        self.calib_measure.setup()# TODO add here the measurements from FPGA photodiode when available 
        self.one_step_move()
        
    @pyqtSlot(float)    
    def one_measurement(self,motor_pos):

        self.motor_positions.append(motor_pos)
        self.calib_data.append(self.calib_measure.acquire())
        self.i=self.i+1
        if self.i<constants.Arduino_interface.MAX_ROTATION_FULL_TURN:
             self.one_step_move()
        else:  #calibration finished
            print("here")
            self.calib_measure.close_comm()
            self.calib_plot.scene().sigMouseClicked.connect(self.add_mouse_position_click)
            self.calib_plot.plot(self.calib_data)
            self.new_win.close()
            self.clicked_timer=QTimer(self)
            self.clicked_timer.setInterval(100)
            self.clicked_timer.timeout.connect(self.ready_treatment_check)
            self.clicked_timer.start()
            
    @pyqtSlot()
    def ready_treatment_check(self):
        if len(self.peaks_pos)==2:
            self.clicked_timer.stop()
            self.calibration_treatment()
            
    
    def one_step_move(self):
        self.send_calibration_step.emit()
        
    @pyqtSlot(object)    
    def add_mouse_position_click(self,pos):
        self.pos=pos.pos()[0]
        self.peaks_pos.append(pos.pos()[0])
    def calibration_treatment(self):
       
        idx_first_peak=np.where(np.min(self.peaks_pos[0][0]-self.motor_positions))[0]
        slice_first_peak=(0,idx_first_peak+len(self.motor_positions)/4)
        idx_first_peak=np.where(np.max(self.calib_data[slice_first_peak]))[0]
        idx_second_peak=np.where(np.min(self.peaks_pos[1][0]-self.motor_positions))[0]
        slice_second_peak=(idx_second_peak-len(self.motor_positions)/4,len(self.motor_positions)-1)
        idx_second_peak=np.where(np.max(self.calib_data[slice_second_peak]))[0]
        self.reduction_ratio=360/(self.motor_positions[idx_second_peak]-self.motor_positions[idx_first_peak])
        self.zero_position=self.motor_positions[idx_first_peak]
        pen=pyqtgraph.mkPen(c="r")
        self.calib_plot.addItem(pyqtgraph.InfiniteLine(self.zero_position,angle=90,pen=pen))
        self.calib_plot.addItem(pyqtgraph.InfiniteLine(self.motor_positions[idx_second_peak],angle=90,pen=pen))
        self.params.add_text_label("zero_pos", value=self.zero_position, label="0° position in motor steps : ")
        self.params.add_text_label("red_ratio", value=self.reduction_ratio, label="Reduction ratio")
        self.params.add_text_label("instructions", "Please Copy the values above in the constants.py file \n 0° position should be in TURNTABLE_ANGLE_MIN_DEC \n Reduction ratio should be in REDUCTION_RATIO \n Then restart python (spyder if you're using it) to activate the change")
        
             
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