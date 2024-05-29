# -*- coding: utf-8 -*-
"""
Created on Monday April 22 2024

@author: Baptiste Bordet 
"""

from pylablib.core.gui.widgets import container, param_table
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import qdarkstyle
import pathlib

class Saving(container.QGroupBoxContainer):
    def setup(self):
        self.supported_format=[".csv",".txt",".xls",".xlsx"]
        super().setup(caption="Saving")
        self.params=self.add_to_layout(param_table.ParamTable(self))
        self.params.setup(name="save_table")
        
        with self.params.using_new_sublayout("folder_saving_path","hbox",location=("next",0,1,3)):
            self.params.add_text_edit(name="folder_path",label="Folder Path",value="C:\\")
            self.params.add_button("browse_path",caption="Browse Folder",location=("next",0,2,1))
            self.params.w["browse_path"].clicked.connect(self.browse_button_folder)
            
        with self.params.using_new_sublayout("file_saving_path","hbox",location=("next",0,1,3)):
            self.params.add_text_edit(name="file_path",label="Filename",value="")
            self.params.add_button("browse_filename",caption="Browse File",location=("next",0,2,1))
            self.params.w["browse_filename"].clicked.connect(self.browse_button_filename)
            
        self.params.add_combo_box("format", label="Format:", options=[".csv",".txt",".xls",".xlsx"],index_values=[".csv",".txt",".xls",".xlsx"])
        self.params.add_combo_box("separator",label="Separator:", options=[",",";"],index_values=[",",";"])   
          
    def browse_button_folder(self):
        dialog=QFileDialog(self,"Saving Folder Path ")
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        dialog.show()
        if dialog.exec():
            self.folder_path=dialog.selectedFiles()[0]
            self.params.wv["folder_path"]=self.folder_path
            
    def browse_button_filename(self):
        dialog=QFileDialog(self,"Saving Filename ")
        if self.params.v["folder_path"]!="":
            dialog.setDirectory(self.params.v["folder_path"])
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
        dialog.show()
        if dialog.exec():
            self.filename=dialog.selectedFiles()[0]
            self.filename_path_lib=pathlib.Path(dialog.selectedFiles()[0])
            if self.filename_path_lib.suffix in self.supported_format:
                self.params.wv["format"]=self.filename_path_lib.suffix
                self.filename=self.filename_path_lib.stem
            else:
                raise Exception("The format of the supplied file for saving is not supported")
            self.params.wv["file_path"]=self.filename
            
    def default_values(self, config_dict):
        self.params.v["folder_path"]=config_dict["saving_folder_path"]
        self.params.v["file_path"]=config_dict["saving_filename"]
        if config_dict["saving_file_format"] in [".csv",".txt",".xls",".xlsx"]:
            self.params.v["format"]=config_dict["saving_file_format"]
        else: 
            QMessageBox.warning(self, "Wrong file format", "default format of the saving file is incorrect in the configuration file \n the command will be ignored ")
        if config_dict["saving_file_separator"] in [",",";"]:
            self.params.v["separator"]=config_dict["saving_file_separator"]
        else: 
            QMessageBox.warning(self, "Wrong file separator", "default separator of the saving file is incorrect in the configuration file \n the command will be ignored ")
    
    def grab_saving_file_path(self):
        saving_folder_path=self.params.v["folder_path"]
        saving_filename=self.params.v["file_path"]
        extension_file=self.params.v["format"]
        separator=self.params.v["separator"]
        return saving_folder_path, saving_filename, extension_file, separator