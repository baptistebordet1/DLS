# -*- coding: utf-8 -*-
"""
Created on Monday April 22 2024

@author: Baptiste Bordet 
"""

from pylablib.core.gui.widgets import container, param_table
from PyQt5.QtWidgets import QFileDialog
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
            