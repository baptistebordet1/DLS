# -*- coding: utf-8 -*-
"""
Created on Monday February 5 2024
@author: Baptiste Bordet 
"""

# from PyQt6.QtWidgets import QThreadPool, QThread
from pylablib.core.gui.widgets import container, param_table



class Motor_rotation(container.QFrameContainer):
    def setup(self):
        
        super().setup()
        self.params=self.add_child("motor rotation params",param_table.ParamTable(self),location=(0,0))

        self.params.setup(add_indicator=False)
        self.params.add_num_label("position_rotation",label="Position:")
        self.params.add_num_edit("move_rotation",label="Move:")
        self.params.add_combo_box("direction", options=["Positiv","Negativ"],index_values=["Positiv","Negativ"],label="Direction:")
        self.params.add_button("apply_rotation",caption="Apply")
        self.params.w["apply_rotation"].clicked.connect(self.send_command_move)
        
    def update_position(self,dict_motors_positions):
        self.params.wv["position_rotation"]=dict_motors_positions["Rotation motor pos"]
    
    def send_command_move(self):
        pass

    
        
    
    
class Motor_attenuation(container.QFrameContainer):
    def setup(self):
        super().setup()
        self.params=self.add_child("motor attenuation params",param_table.ParamTable(self),)
        self.params.setup()
        self.params.add_num_label("position_attenuation",label="Attenuation:")
        self.params.add_combo_box("attenutaion change",options=["0","1","2"],index_values=[0,1,2],label="Attenuation change")
        self.params.add_button("apply_attenuation",caption="Apply")
        self.params.w["apply_attenuation"].clicked.connect(self.send_command_move)
        
    def update_position(self,dict_motors_positions):
        self.params.wv["position_attenuation"]=dict_motors_positions["Attenuation motor pos"]
    
    def send_command_move(self):
        pass