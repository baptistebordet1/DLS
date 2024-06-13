# -*- coding: utf-8 -*-
"""
Created on Friday May 17 2024

@author: Baptiste Bordet
"""

from pylablib.core.gui.widgets import container, param_table
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import re
import os
import pathlib 
from PyQt5 import QtGui,QtWidgets
from utils.GUI import saving_ctl

#TODO add start and stop methods 

class Sequence(container.QGroupBoxContainer):
    def setup(self,saving_control):
        self.saving_control=saving_control
        super().setup(caption="Sequence Loader")
        self.params=self.add_to_layout(param_table.ParamTable(self))
        self.params.setup(name="sequence_table")
        self.measurement_file=""
        with self.params.using_new_sublayout("Sequence_path_browse", "hbox"):
            self.params.add_text_edit("sequence_path",label="Sequence Path : ")
            self.params.add_button("sequence path browser", caption="Browse")
            self.params.w["sequence path browser"].clicked.connect(self.browse_sequence)
        with self.params.using_new_sublayout("Sequence_load", "hbox"):
            self.params.add_button("load_sequence", caption="Load Sequence")
            self.params.w["load_sequence"].clicked.connect(self.load_sequence)
            self.params.add_check_box("sequence_loaded", caption="Sequence Loaded")
            self.params.set_enabled(names="sequence_loaded",enabled=False)
            self.params.w["sequence_loaded"].setStyleSheet("\n QCheckBox:disabled{color: #DFE1E2;}\n QCheckBox:indicator:checked:disabled{ image:url(utils/ressources/round_checkbox_checked_samll.png);}  QCheckBox:indicator:unchecked:disabled{image:url(utils/ressources/round_checkbox_unchecked_samll.png);}")
        self.params.add_spacer(15)
        with self.params.using_new_sublayout("buttons", "hbox"):
            self.params.add_button("start_sequence", caption="Start Sequence")
            self.params.add_button("stop_sequence", caption="Stop Sequence")
            self.utils_directory=pathlib.Path(__file__).parent.parent.resolve()
            self.play_path=os.path.join(self.utils_directory,"ressources/play.png")
            self.stop_path=os.path.join(self.utils_directory,"ressources/stop.png")
            self.play_pic=QtGui.QPixmap(self.play_path)
            self.stop_pic=QtGui.QPixmap(self.stop_path)
            self.params.w["start_sequence"].setIcon(QtGui.QIcon(self.play_pic))
            self.params.w["stop_sequence"].setIcon(QtGui.QIcon(self.stop_pic))
            self.params.w["start_sequence"].setMinimumHeight(int(0.027*QtWidgets.QDesktopWidget().screenGeometry(self).height()))
            self.params.w["stop_sequence"].setMinimumHeight(int(0.027*QtWidgets.QDesktopWidget().screenGeometry(self).height()))
    
    def browse_sequence(self):
        dlg = QFileDialog(self)
        dlg.setDirectory("./")
        if dlg.exec():
            self.measurement_filepath = dlg.selectedFiles()
        self.params.v["sequence_path"]=self.measurement_filepath[0]
            
    def is_number(self, x):
        try:
            float(x)
            return True
        except ValueError:
            return False
        
    def load_sequence(self):
        self.measurement_filepath=self.params.v["sequence_path"]
        if self.measurement_filepath=="":
            QMessageBox.warning(self, "No file selected", "No file has been selected yet")
            return
        try: 
            open(pathlib.Path(self.measurement_filepath))
        except FileNotFoundError:
            QMessageBox.warning(self, "File path error", "Error : the file path doesn't exist, try to browse instead")
            return
        self.measurement_file = open(self.measurement_filepath, "r")
        self.meas_lines = self.measurement_file.readlines()
        self.meas_lines = self.meas_lines[7:]
        for i, line in enumerate(self.meas_lines):
            line = re.sub(r"[\n\t\s]*", "", line)
            line_splitted = line.split(",")
            
            if line_splitted[0] == "MOVE" and len(line_splitted) != 1:
                QMessageBox.warning(
                    self, "Measurement file error", "Invalid number of argument for MOVE argument")
                return
            if line_splitted[0] == "MOVE" and (float(line_splitted[1]) > 180 or float(line_splitted[1]) < 0):
                QMessageBox.warning(
                    self, "Measurement file error", "Impossible to move the motor (destination out of range)")
                return
            if (line_splitted[0] == "MEASURE") and len(line_splitted) != 4:
                QMessageBox.warning(
                    self, "Measurement file error", "Invalid number of argument for MEASURE argument")
                return
            for j in range(len(line_splitted)-1):
                is_digit = self.is_number(line_splitted[j+1])
                if is_digit == False:
                    QMessageBox.warning(
                        self, "Measurement file error", "There is a letter on the arguments on line {line_nbr:.0f}, please review it".format(line_nbr=i))
                    return
        #TODO add here other conditions to check on Tau max and acquisitions time and attenuation value (value between 0,8 with different attenuation) 
        
        self.params.v["sequence_loaded"]=1
        
    def default_values(self, config_dict):
        self.params.v["sequence_path"]=config_dict["sequence_file_path"]
    
    def start_sequence(self):
        folder_path,filename,extension_file,separator=saving_ctl.Saving.grab_saving_file_path(self.saving_control)
        is_folder=pathlib.Path(folder_path).is_dir()
        if is_folder==False:
            QtWidgets.QMessageBox.warning(self,
                                          "Saving Folder doesn't exist", "The saving folder you indicated is unreachable, try browsing instead") 
            return
        #TODO add here sending of signal to start sequence with sequence path, folder path and filename, format and separator
        