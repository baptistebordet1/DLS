# -*- coding: utf-8 -*-
"""
Created on Thursday May 23 2024

@author: Baptiste Bordet
"""

import pyqtgraph
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from pylablib.core.gui.widgets import param_table, container
from utils.FPGA_interface import FPGA_serial_ASCII
from utils import constants


import numpy as np 

class Calibration(container.QFrameContainer):
    send_calibration_step=pyqtSignal()
    def setup(self,i_thread):#here add the interace thread to be able to sned command via the fpga
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
            self.params.add_num_edit("first_peak",label="1st peak estimation :")
            self.params.add_num_edit("second_peak",label="2nd peak estimation :")
            self.params.add_button("validate_estimations", "validate estimations")
            self.params.add_button("start_calib",caption="Start Calibration")  
            self.params.w["start_calib"].clicked.connect(self.start_calibration)
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.i_thread=i_thread

    def start_calibration(self):
        self.calib_data=[]
        self.peaks_pos=[]
        self.motor_positions=[]
        self.new_win=waiting_window_calibration(self)
        self.new_win.setup()
        self.new_win.show()
        self.i=0
        self.calib_measure=self.i_thread.fpga_serial_ascii
        print(self.calib_measure)
        self.one_step_move()
        
    @pyqtSlot(float)    
    def one_measurement(self,motor_pos):

        self.motor_positions.append(motor_pos)
        self.calib_data.append(self.calib_measure.ask_pd_value())
        self.i=self.i+1
        if self.i<constants.Arduino_interface.MAX_ROTATION_FULL_TURN:
             self.one_step_move()
        else:  #calibration finished
            self.calib_measure.close_comm()
            self.calib_plot.plot(self.motor_positions,self.calib_data)
            self.new_win.close()
            self.params.w["validate_estimations"].clicked.connect(self.calibration_treatment)
            

    def one_step_move(self):
        self.send_calibration_step.emit()
        
        
    def calibration_treatment(self):
        if self.params.v["first_peak"]!="":
            self.peaks_pos.append(self.params.v["first_peak"])
        else:
            raise ValueError("no value entered in estimation of first peak")
            return
        if self.params.v["second_peak"]!="":
            self.peaks_pos.append(self.params.v["second_peak"])
        else:
            raise ValueError("no value entered in estimation of second peak")  
            return
        peaks=[]
        for j in range(0,1):
            idx = np.where(self.motor_positions-self.peaks_pos[j]<0.01)[0][0] # à ajuster en fonction du pas du moteur
            for i in range(int(idx-0.1*len(self.motor_positions)),int(idx+0.1*len(self.motor_positions))):
                diff_gauche=self.motor_positions[i]-self.motor_positions[i-1]
                diff_droite=self.motor_positions[i+1]-self.motor_positions[i]
                ratio_diff=np.abs(diff_gauche/diff_droite)
                if ratio_diff>0.1:
                    peaks.append(self.motor_positions[i])      
        self.reduction_ratio=360/(peaks[1]-peaks[0])
        pen=pyqtgraph.mkPen(c="r")
        self.calib_plot.addItem(pyqtgraph.InfiniteLine(peaks[0],angle=90,pen=pen))
        self.calib_plot.addItem(pyqtgraph.InfiniteLine(peaks[1],angle=90,pen=pen))
        self.params.add_text_label("red_ratio", value=self.reduction_ratio, label="Reduction ratio")
        self.params.add_text_label("frist_peak", value=peaks[0], label="first peak")
        self.params.add_text_label("second_peak", value=peaks[1], label="second peak")
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