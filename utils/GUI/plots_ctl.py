# -*- coding: utf-8 -*-
"""
Created on Monday May 13 2024

@author: Baptiste Bordet 
"""

from pylablib.core.gui.widgets import container, param_table
import numpy as np

# Control auto correlation plots 

class plot_control_auto_corr(container.QGroupBoxContainer):
    def setup(self, plot_auto_corr):
        super().setup("Control auto-correlation plot")
        self.plot_auto_corr=plot_auto_corr
        self.plot_auto_corr.sigRangeChanged.connect(self.change_indicators)
        self.params=self.add_to_layout(param_table.ParamTable(self))
        self.params.setup(name="control_plot_auto_corr")
        with self.params.using_new_sublayout("auto_resize", "hbox"):
            self.params.add_check_box("auto_range_auto_corr", caption="Auto range").get_value_changed_signal().connect(self.auto_range_change)
            self.params.add_button("resize", caption="Resize plot")
        self.params.w["resize"].clicked.connect(self.resize)
        self.params.add_decoration_label("Manual range : ")
        self.manual_change=1
        with self.params.using_new_sublayout("Yrange", "hbox"):
            self.params.add_num_edit("Ymin", value=None, label="Ymin : ").get_value_changed_signal().connect(self.manual_Y_resize)
            self.params.add_num_edit("Ymax", value=None, label="Ymax : ").get_value_changed_signal().connect(self.manual_Y_resize)
        with self.params.using_new_sublayout("Xrange", "hbox"):
            self.params.add_num_edit("Xmin", value=None, label="Xmin : ",limiter=(0,None,"ignore")).get_value_changed_signal().connect(self.manual_X_resize)
            self.params.add_num_edit("Xmax", value=None, label="Xmax : ",limiter=(0,None,"ignore")).get_value_changed_signal().connect(self.manual_X_resize)
        self.params.add_combo_box("Log-Lin scale", value=1, options=["Logarithmic", "Linear"],index_values=[1,0],label = "Set X-scale : ",location=(5,0)).get_value_changed_signal().connect(self.change_scale)
    def auto_range_change(self):
        if self.manual_change==1:
            self.manual_change=0  
        else:
            self.manual_change=1
        self.params.w["Ymin"].setDisabled(self.params.w["Ymin"].isEnabled())
        self.params.w["Ymax"].setDisabled(self.params.w["Ymax"].isEnabled())
        self.params.w["Xmin"].setDisabled(self.params.w["Xmin"].isEnabled())
        self.params.w["Xmax"].setDisabled(self.params.w["Xmax"].isEnabled())
        self.plot_auto_corr.enableAutoRange(enable=self.params.v["auto_range_auto_corr"])
        
    def resize(self):
        self.manual_change=0
        self.plot_auto_corr.autoRange()  
        self.manual_change=1
    def manual_Y_resize(self):
        if self.manual_change==1:
            self.plot_auto_corr.setYRange(self.params.v["Ymin"], self.params.v["Ymax"],padding=0)
    def manual_X_resize(self):
        if self.manual_change==1:
           if self.params.v["Log-Lin scale"]==1:
               self.plot_auto_corr.setXRange(np.log10(self.params.v["Xmin"]), np.log10(self.params.v["Xmax"]),padding=0)
           else:
               self.plot_auto_corr.setXRange(self.params.v["Xmin"], self.params.v["Xmax"],padding=0)
    def change_indicators(self):
        self.manual_change=0
        if self.params.v["Log-Lin scale"]==1:
            self.params.v["Xmin"]=10**(self.plot_auto_corr.getPlotItem().viewRange()[0][0])
            self.params.v["Xmax"]=10**(self.plot_auto_corr.getPlotItem().viewRange()[0][1])
        else:
            self.params.v["Xmin"]=self.plot_auto_corr.getPlotItem().viewRange()[0][0]
            self.params.v["Xmax"]=self.plot_auto_corr.getPlotItem().viewRange()[0][1]
        self.params.v["Ymin"]=self.plot_auto_corr.getPlotItem().viewRange()[1][0]
        self.params.v["Ymax"]=self.plot_auto_corr.getPlotItem().viewRange()[1][1]
        self.manual_change=1
    def change_scale(self):
        self.manual_change=0
        if self.params.v["Log-Lin scale"]==0:
            self.params.w["Xmin"].set_limiter(limiter=(None,None,"ignore"))
            self.params.w["Xmax"].set_limiter(limiter=(None,None,"ignore"))
        else: 
            self.params.w["Xmin"].set_limiter(limiter=(0,None,"ignore"))
            self.params.w["Xmax"].set_limiter(limiter=(0,None,"ignore"))
        self.plot_auto_corr.getPlotItem().setLogMode( self.params.v["Log-Lin scale"])
        self.manual_change=1
        
# Control I avg plot

class plot_control_I_avg(container.QGroupBoxContainer):
    def setup(self, plot_I_avg):
        super().setup("Control I avg plot")
        self.plot_I_avg=plot_I_avg
        self.plot_I_avg.sigRangeChanged.connect(self.change_indicators)
        self.params=self.add_to_layout(param_table.ParamTable(self))
        self.params.setup(name="control_plot_I_avg")
        with self.params.using_new_sublayout("auto_resize", "hbox"):
            self.params.add_check_box("auto_range_I_avg", caption="Auto range").get_value_changed_signal().connect(self.auto_range_change)
            self.params.add_button("resize", caption="Resize plot")
        self.params.w["resize"].clicked.connect(self.resize)
        self.params.add_decoration_label("Manual range : ")
        self.manual_change=1
        with self.params.using_new_sublayout("Yrange", "hbox",location=(3,0)):
            self.params.add_num_edit("Ymin", value=None, label="Ymin : ").get_value_changed_signal().connect(self.manual_Y_resize)
            self.params.add_num_edit("Ymax", value=None, label="Ymax : ").get_value_changed_signal().connect(self.manual_Y_resize)
        with self.params.using_new_sublayout("Xrange", "hbox",location=(4,0)):
            self.params.add_num_edit("Xmin", value=None, label="Xmin : ").get_value_changed_signal().connect(self.manual_X_resize)
            self.params.add_num_edit("Xmax", value=None, label="Xmax : ").get_value_changed_signal().connect(self.manual_X_resize)
        
    def auto_range_change(self):
        if self.manual_change==1:
            self.manual_change=0  
        else:
            self.manual_change=1
        self.params.w["Ymin"].setDisabled(self.params.w["Ymin"].isEnabled())
        self.params.w["Ymax"].setDisabled(self.params.w["Ymax"].isEnabled())
        self.params.w["Xmin"].setDisabled(self.params.w["Xmin"].isEnabled())
        self.params.w["Xmax"].setDisabled(self.params.w["Xmax"].isEnabled())
        self.plot_I_avg.enableAutoRange(enable=self.params.v["auto_range_auto_corr"])
        
    def resize(self):
        self.manual_change=0
        self.plot_I_avg.autoRange()  
        self.manual_change=1
    def manual_Y_resize(self):
        if self.manual_change==1:
            self.plot_I_avg.setYRange(self.params.v["Ymin"], self.params.v["Ymax"],padding=0)
    def manual_X_resize(self):
        if self.manual_change==1:
            self.plot_I_avg.setXRange(self.params.v["Xmin"], self.params.v["Xmax"],padding=0)
    def change_indicators(self):
        self.manual_change=0
        self.params.v["Xmin"]=self.plot_I_avg.getPlotItem().viewRange()[0][0]
        self.params.v["Xmax"]=self.plot_I_avg.getPlotItem().viewRange()[0][1]
        self.params.v["Ymin"]=self.plot_I_avg.getPlotItem().viewRange()[1][0]
        self.params.v["Ymax"]=self.plot_I_avg.getPlotItem().viewRange()[1][1]
        self.manual_change=1
        
# Control cross correlation plot 

class plot_control_cross_corr(container.QGroupBoxContainer):
    def setup(self, plot_cross_corr):
        super().setup("Control cross-correlation plot")
        self.plot_cross_corr=plot_cross_corr
        self.plot_cross_corr.sigRangeChanged.connect(self.change_indicators)
        self.params=self.add_to_layout(param_table.ParamTable(self))
        self.params.setup(name="control_plot_cross_corr")
        with self.params.using_new_sublayout("auto_resize", "hbox"):
            self.params.add_check_box("auto_range_cross_corr", caption="Auto range").get_value_changed_signal().connect(self.auto_range_change)
            self.params.add_button("resize", caption="Resize plot")
        self.params.w["resize"].clicked.connect(self.resize)
        self.params.add_decoration_label("Manual range : ")
        self.manual_change=1
        with self.params.using_new_sublayout("Yrange", "hbox"):
            self.params.add_num_edit("Ymin", value=None, label="Ymin : ").get_value_changed_signal().connect(self.manual_Y_resize)
            self.params.add_num_edit("Ymax", value=None, label="Ymax : ").get_value_changed_signal().connect(self.manual_Y_resize)
        with self.params.using_new_sublayout("Xrange", "hbox"):
            self.params.add_num_edit("Xmin", value=None, label="Xmin : ",limiter=(0,None,"ignore")).get_value_changed_signal().connect(self.manual_X_resize)
            self.params.add_num_edit("Xmax", value=None, label="Xmax : ",limiter=(0,None,"ignore")).get_value_changed_signal().connect(self.manual_X_resize)
        self.params.add_combo_box("Log-Lin scale", value=1, options=["Logarithmic", "Linear"],index_values=[1,0],label = "Set X-scale : ").get_value_changed_signal().connect(self.change_scale)
    
    def auto_range_change(self):
        if self.manual_change==1:
            self.manual_change=0  
        else:
            self.manual_change=1
        self.params.w["Ymin"].setDisabled(self.params.w["Ymin"].isEnabled())
        self.params.w["Ymax"].setDisabled(self.params.w["Ymax"].isEnabled())
        self.params.w["Xmin"].setDisabled(self.params.w["Xmin"].isEnabled())
        self.params.w["Xmax"].setDisabled(self.params.w["Xmax"].isEnabled())
        self.plot_cross_corr.enableAutoRange(enable=self.params.v["auto_range_auto_corr"])
        
    def resize(self):
        self.manual_change=0
        self.plot_cross_corr.autoRange()  
        self.manual_change=1
    def manual_Y_resize(self):
        if self.manual_change==1:
            self.plot_cross_corr.setYRange(self.params.v["Ymin"], self.params.v["Ymax"],padding=0)
    def manual_X_resize(self):
        if self.manual_change==1:
            if self.params.v["Log-Lin scale"]==1:
                self.plot_cross_corr.setXRange(np.log10(self.params.v["Xmin"]), np.log10(self.params.v["Xmax"]),padding=0)
            else:
                self.plot_cross_corr.setXRange(self.params.v["Xmin"], self.params.v["Xmax"],padding=0)
    def change_indicators(self):
        self.manual_change=0
        if self.params.v["Log-Lin scale"]==1:
            self.params.v["Xmin"]=10**(self.plot_cross_corr.getPlotItem().viewRange()[0][0])
            self.params.v["Xmax"]=10**(self.plot_cross_corr.getPlotItem().viewRange()[0][1])
        else:
            self.params.v["Xmin"]=self.plot_cross_corr.getPlotItem().viewRange()[0][0]
            self.params.v["Xmax"]=self.plot_cross_corr.getPlotItem().viewRange()[0][1]
        self.params.v["Ymin"]=self.plot_cross_corr.getPlotItem().viewRange()[1][0]
        self.params.v["Ymax"]=self.plot_cross_corr.getPlotItem().viewRange()[1][1]
        self.manual_change=1
    def change_scale(self):
        self.manual_change=0
        if self.params.v["Log-Lin scale"]==0:
            self.params.w["Xmin"].set_limiter(limiter=(None,None,"ignore"))
            self.params.w["Xmax"].set_limiter(limiter=(None,None,"ignore"))
        else: 
            self.params.w["Xmin"].set_limiter(limiter=(0,None,"ignore"))
            self.params.w["Xmax"].set_limiter(limiter=(0,None,"ignore"))
        self.plot_cross_corr.getPlotItem().setLogMode( self.params.v["Log-Lin scale"])
        self.manual_change=1