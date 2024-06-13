# -*- coding: utf-8 -*-
"""
Created on Monday February 5 2024
@author: Baptiste Bordet 
"""

from pylablib.core.gui.widgets import container, param_table
from PyQt5.QtCore import pyqtSignal
from utils.GUI import calibration_ctl

class Motor_rotation(container.QFrameContainer):
    send_command_rotation=pyqtSignal(float)

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
        calib_window=calibration_ctl.Calibration(self)
        calib_window.setup()
        calib_window.show()
    def update_position(self,dict_motors_positions):
        self.params.wv["position_rotation"]=dict_motors_positions["Rotation motor pos"]
    
    def send_command_move(self):
        self.send_command_rotation.emit(self.params.v["move_rotation"])
    
class Motor_attenuation(container.QFrameContainer):
    send_command_attenation=pyqtSignal(int)
    def setup(self):
        super().setup()
        self.params=self.add_child("motor attenuation params",param_table.ParamTable(self))
        self.params.setup()
        self.params.add_num_label("position_attenuation",label="Attenuation:")
        self.params.add_combo_box("attenuation change",options=["0","1","2"],index_values=[0,1,2],label="Attenuation change")
        self.params.add_button("apply_attenuation",caption="Apply")
        self.params.w["apply_attenuation"].clicked.connect(self.send_command_move)
        
    def update_position(self,dict_motors_positions):
        self.params.wv["position_attenuation"]=dict_motors_positions["Attenuation motor pos"]
    
    def send_command_move(self):
        self.send_command_attenation.emit(self.params.v["attenuation change"])
       