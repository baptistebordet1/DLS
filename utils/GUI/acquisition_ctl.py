# -*- coding: utf-8 -*-
"""
Created on Thursday May 16 2024

@author: Baptiste Bordet
"""


from pylablib.core.gui.widgets import container, param_table
from PyQt5 import QtGui
import pathlib
import os
from PyQt5 import QtWidgets 
from PyQt5.QtCore import pyqtSignal

from utils.constants import Acquisition_time_limit
from utils.GUI import saving_ctl

class Acquisition(container.QGroupBoxContainer):
    Acquisition_start=pyqtSignal(str, str, str, str,str,  int, int)
    Acquisition_stop=pyqtSignal()
    def setup(self,saving_control):
        self.saving_control=saving_control
        super().setup(caption="Acquisition")
        self.params=self.add_to_layout(param_table.ParamTable(self))
        self.params.setup(name="acquisition_table")
        self.params.add_combo_box("experience_type",options=["Auto-corr chan. 1","Auto-corr chan. 2", "Auto-corr cha. 1 and 2", "Cross-corr"],index_values=["AUTO11", "AUTO22", "AUTO12", "CROSS"],label="Experience Type")
        self.params.add_num_edit("corr_length",label="𝜏 max(ms):",limiter=(Acquisition_time_limit.TAU_MIN, Acquisition_time_limit.TAU_MAX))
        self.params.add_num_edit("acq_time",label="Acquisition Time(s):", limiter=(Acquisition_time_limit.ACQ_TIME_MIN,Acquisition_time_limit.ACQ_TIME_MAX ))
        with self.params.using_new_sublayout("buttons","hbox"):
            self.params.add_button("start_acquisition", caption="Start Acquisition")
            self.params.add_button("stop_acquisition", caption="Stop Acquisition")
            self.utils_directory=pathlib.Path(__file__).parent.parent.resolve()
            self.play_path=os.path.join(self.utils_directory,"ressources/play.png")
            self.stop_path=os.path.join(self.utils_directory,"ressources/stop.png")
            self.play_pic=QtGui.QPixmap(self.play_path)
            self.stop_pic=QtGui.QPixmap(self.stop_path)
            self.params.w["start_acquisition"].setIcon(QtGui.QIcon(self.play_pic))
            self.params.w["stop_acquisition"].setIcon(QtGui.QIcon(self.stop_pic))
            self.params.w["start_acquisition"].setMinimumHeight(int(0.027*QtWidgets.QDesktopWidget().screenGeometry(self).height()))
            self.params.w["stop_acquisition"].setMinimumHeight(int(0.027*QtWidgets.QDesktopWidget().screenGeometry(self).height()))
            self.params.w["start_acquisition"].clicked.connect(self.start_acquisition)
            
    def default_values(self, config_dict):
        if float(config_dict["corr_length"])<=Acquisition_time_limit.TAU_MAX: 
            self.params.v["corr_length"]=float(config_dict["corr_length"])
        else: 
            QtWidgets.QMessageBox.warning(self,
            "𝜏 max too big", f"𝜏 max can't be higher than {Acquisition_time_limit.TAU_MAX} ms \n default 𝜏 max will be ignored")
        self.params.v["acq_time"]=float(config_dict["acq_time"])
        
    def start_acquisition(self):
        folder_path,filename,extension_file,separator=saving_ctl.Saving.grab_saving_file_path(self.saving_control)
        is_folder=pathlib.Path(folder_path).is_dir()
        if is_folder==False:
            QtWidgets.QMessageBox.warning(self,
                                          "Saving Folder doesn't exist", "The saving folder you indicated is unreachable, try browsing instead") 
            return
        self.Acquisition_start.emit(folder_path, filename,extension_file,separator,self.params.v["experience_type"],self.params.v["corr_length"],self.params.v["acq_time"])
    
    def stop_acquisition(self):
        self.Acquisition_stop.emit()
    
    def grab_tau_max(self):
        return self.params.v["corr_length"]