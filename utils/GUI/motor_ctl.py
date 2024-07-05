# -*- coding: utf-8 -*-
"""
Created on Monday February 5 2024
@author: Baptiste Bordet 
"""

from pylablib.core.gui.widgets import container, param_table
from PyQt5 import QtWidgets 
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from utils.GUI import calibration_ctl
from utils import constants
import numpy as np 

class Motor_rotation(container.QFrameContainer):
    send_command_rotation=pyqtSignal(float)
    start_calib=pyqtSignal()
    def setup(self):
        
        super().setup()
        self.params=self.add_child("motor rotation params",param_table.ParamTable(self),location=(0,0))

        self.params.setup(add_indicator=False)
        with self.params.using_new_sublayout("pos_calib", "hbox"):
            self.params.add_num_label("position_rotation",label="Position:")
            self.params.add_button("calib_motor", "Calibration Motor")
            self.params.w["calib_motor"].clicked.connect(self.calibration_motor)
            
        self.params.add_num_edit("move_rotation",label="Move:")
        self.params.add_button("apply_rotation",caption="Apply")
        self.params.w["apply_rotation"].clicked.connect(self.send_command_move)
        
    def calibration_motor(self):
        self.calib_window=calibration_ctl.Calibration(self)
        self.calib_window.setup()
        self.calib_window.show()
        self.start_calib.emit()
        
    def update_position(self,dict_motors_positions):
        self.params.wv["position_rotation"]=dict_motors_positions["Rotation motor pos"]
    
    def send_command_move(self):
        self.send_command_rotation.emit(self.params.v["move_rotation"])
    
class Motor_attenuation(container.QFrameContainer):
    send_command_attenation=pyqtSignal(int)
    start_auto_find_att=pyqtSignal()
    send_command_attenuation_auto_find=pyqtSignal(int)
    auto_find_attenuation_finished=pyqtSignal()
    
    def setup(self):
        super().setup()
        self.params=self.add_child("motor attenuation params",param_table.ParamTable(self))
        self.params.setup()
        with self.params.using_new_sublayout("pos_auto_find", "hbox"):
            self.params.add_num_label("position_attenuation",label="Attenuation:")
            self.params.add_button("auto_find_att", "Auto-attenuation")
            self.params.w["auto_find_att"].clicked.connect(self.start_auto_find_attenuation)
        self.params.add_combo_box("attenuation change",options=["0","1","2","3","4","5","6","7"],index_values=[0,1,2,3,4,5,6,7],label="Attenuation change")
            
        self.params.add_button("apply_attenuation",caption="Apply")
        self.params.w["apply_attenuation"].clicked.connect(self.send_command_move)
        
    def update_position(self,dict_motors_positions):
        self.params.wv["position_attenuation"]=dict_motors_positions["Attenuation motor pos"]
    
    def send_command_move(self):
        self.send_command_attenation.emit(self.params.v["attenuation change"])
    
    def start_auto_find_attenuation(self):
        #TODO Verify that this is the right number and format
        self.send_command_attenuation_auto_find.emit(8)
        self.pos=8 
    
    @pyqtSlot(object)
    def one_measurement_find_attenuation(self,worker):
        pd_val=[]
        for i in range(0,10):
           pd_val.append(worker.fpga_serial_ascii.ask_pd_value())
           # probably need to add here a time.sleep 0.1 s
        pd_val_mean=np.mean(pd_val)  
        if pd_val_mean<constants.Arduino_interface.PHOTODIODE_ATTENUATOR_THRESHOLD:
            self.pos=self.pos-1
            if self.pos<0: 
                QtWidgets.QMessageBox.warning(self,
                                              "Auto_find attenuation could not find a suitable value, try manually or restart the program")
                self.auto_find_attenuation_finished.emit()
            else:
                self.send_command_attenuation_auto_find.emit(self.pos)
        else: 
            self.auto_find_attenuation_finished.emit()
        
        
       