# -*- coding: utf-8 -*-
"""
Created on Friday May 17 2024

@author: Baptiste Bordet
"""

from pylablib.core.gui.widgets import container, param_table

class Sequence(container.QGroupBoxContainer):
    def setup(self):
        super().setup(caption="Sequence Loader")
        self.params=self.add_to_layout(param_table.ParamTable(self))
        self.params.setup(name="sequence_table")
        with self.params.using_new_sublayout("Sequence_path_browse", "hbox"):
            self.params.add_text_edit("sequence_path",label="Sequence Path : ")
            self.params.add_button("sequence path browser", caption="Browse")
        with self.params.using_new_sublayout("Sequence_load", "hbox"):
            self.params.add_button("load_sequence", caption="Load Sequence")
            self.params.w["load_sequence"].clicked.connect(self.load_sequence)
            self.params.add_check_box("sequence_loaded", caption="Sequence Loaded")
            self.params.set_enabled(names="sequence_loaded",enabled=False)
            self.params.w["sequence_loaded"].setStyleSheet("\n QCheckBox:disabled{color: #DFE1E2;}\n QCheckBox:indicator:checked:disabled{ image:url(utils/ressources/checkbox_checked_samll.png);}  QCheckBox:indicator:unchecked:disabled{image:url(utils/ressources/checkbox_unchecked_samll.png);}")
    
    def load_sequence(self):
        self.params.v["sequence_loaded"]=1
        