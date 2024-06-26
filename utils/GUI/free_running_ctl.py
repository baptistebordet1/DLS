# -*- coding: utf-8 -*-
"""
Created on Monday June 24 2024

@author: Baptiste Bordet 
"""


from pylablib.core.gui.widgets import container, param_table
from PyQt5.QtCore import pyqtSignal

class Free_running(container.QGroupBoxContainer):
    free_running_start=pyqtSignal(str)
    free_runing_stop=pyqtSignal()
    def setup(self):
        super().setup(caption="Free Running")
        self.params=self.add_to_layout(param_table.ParamTable(self))
        self.params.setup(name="free_running_table")
        self.params.add_combo_box("experience_type",options=["Auto-correlation channel 1","Auto-correlation channel 2", "Auto-correlation channel 1 and 2", "Cross-correlation"],index_values=["AUTO11", "AUTO22", "AUTO12", "CROSS"],label="Experience Type")
        self.params.add_toggle_button("free_running", label="Free Running", caption=["Free Running off", "Free Running on"])
        self.params.w["free_running"].clicked.connect(self.start_stop_free_running)
        
    def start_stop_free_running(self):
        if self.params.v["free_running"]==True:
            self.free_running_start.emit(self.params.v["experience_type"])
        if self.params.v["free_running"]==False:
            self.free_running_stop.emit()
            
        