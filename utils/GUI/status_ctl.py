# -*- coding: utf-8 -*-
"""
Created on Friday April 19 2024

@author: Baptiste Bordet 
"""

from pylablib.core.gui.widgets import container, param_table

class Status(container.QGroupBoxContainer):
    def setup(self,dict_status):
        super().setup(caption="Status")
        self.params=self.add_to_layout(param_table.ParamTable(self))
        self.params.setup(name="status_table")
        self.params.add_text_label("current_action",label="Current Action:",)
        self.params.add_text_label("detection_angle", label="Detection angle:")
        self.params.add_text_label("attenuation_value",label="Attenuation:")
        self.params.add_text_label("laser_status", label="Laser On/Off:")
        self.params.add_text_label("arduino_connected", label="Arduino controlled:")
        self.params.add_text_label("acquisition_progress",label="Acquisition progress:")
        self.params.add_text_label("error", label="Error:")
        self.params.set_all_values(dict_status)
    def update_table(self,new_dict):
        self.params.set_all_values(new_dict)