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

class Acquisition(container.QGroupBoxContainer):
    def setup(self):
        super().setup(caption="Acquisition")
        self.params=self.add_to_layout(param_table.ParamTable(self))
        self.params.setup(name="acquisition_table")
        self.params.add_num_edit("corr_length",label="𝜏 max(ms):")
        self.params.add_num_edit("acq_time",label="Acquisition Time(s):")
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