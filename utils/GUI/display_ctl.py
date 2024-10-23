# -*- coding: utf-8 -*-
"""
Created on Thursday May 2 2024

@author: Baptiste Bordet
"""

import pyqtgraph
import numpy as np 
from utils import constants
from pylablib.core.gui.widgets import container

class plot_auto_correlation(container.QFrameContainer):
    def setup(self):
        super().setup()
        array=dict(x=np.arange(0,50,1),y=np.random.randint(0,50,50))
        self.auto_corr=self.add_to_layout(pyqtgraph.PlotWidget(self))
        self.auto_corr.showGrid(True,True,0.7)
        self.auto_corr.getPlotItem().addLegend()
        self.auto_corr.getPlotItem().setLogMode(True)
        self.auto_corr.setLabel("left","Auto Correlation")
        self.auto_corr.setMouseMode(pyqtgraph.ViewBox.RectMode)
        self.plot1=self.auto_corr.plot(array["x"],array["y"],name="auto_corr1",symbol="x", pen=None)
        self.tau_list_0th_corr=np.arange(constants.Acquisition_time_limit.TAU_MIN, (constants.Acquisition_parameters.FIRST_CORRELATOR_LENGTH+1)*constants.Acquisition_time_limit.TAU_MIN, constants.Acquisition_time_limit.TAU_MIN)
        self.tau_list=np.zeros((constants.Acquisition_parameters.TOTAL_NUMBER_CORRELATOR))
        self.tau_list[0:constants.Acquisition_parameters.FIRST_CORRELATOR_LENGTH]=self.tau_list_0th_corr
        k=constants.Acquisition_parameters.FIRST_CORRELATOR_LENGTH
        for i in range(1,constants.Acquisition_parameters.DIFFERENT_CORRELATORS_NUMBER):
            for j in range(1,constants.Acquisition_parameters.LINEAR_CORRELATION_NUMBER+1):
                self.tau_list[k]=(self.tau_list_0th_corr[0]*2**i*j)
                k=k+1
                
        #TODO check that it's teh full tau list needed or the list without duplicated values 
    def update_plot(self,new_data_point,exp_type):
        n_max=constants.Acquisition_time_limit.MAX_POINT_PLOT
        if exp_type =="AUTO11" or exp_type=="AUTO22":
            self.auto_corr.plot(self.tau_list[0:n_max],new_data_point[n_max], symbol="x", name=exp_type, pen=None)
        else: 
            self.auto_corr.plot(self.tau_list[0:n_max],new_data_point[0:n_max],name="AUTO11", symbol="x", pen=None)
            self.auto_corr.plot(self.tau_list[int(len(new_data_point)/2):n_max+int(len(new_data_point)/2)],new_data_point[int(len(new_data_point)/2):int(len(new_data_point)/2)+n_max],name="AUTO22", symbol="t",pen=None)
            
        
        
class plot_cross_correlation(container.QFrameContainer):
    def setup(self):
        super().setup()
        self.cross_corr=self.add_to_layout(pyqtgraph.PlotWidget(self))
        self.cross_corr.showGrid(True,True,0.7)
        self.cross_corr.setMouseMode(pyqtgraph.ViewBox.RectMode)
        self.cross_corr.getPlotItem().addLegend()
        self.cross_corr.getPlotItem().setLogMode(True)
        self.cross_corr.setLabel("left","Cross Correlation")  
        self.tau_list=[]
    def update_plot(self,new_data_point,exp_type):
        n_max=constants.Acquisition_time_limit.MAX_POINT_PLOT
        self.cross_corr.plot(self.tau_list[0:n_max], new_data_point[0:n_max], name="Cross Correlation ", symbol="+", pen=None)
        
class plot_PD(container.QFrameContainer):
    def setup(self):
        super().setup()
        self.PD=self.add_to_layout(pyqtgraph.PlotWidget(self))
        self.PD.setMouseMode(pyqtgraph.ViewBox.RectMode)
        self.PD.getPlotItem().addLegend()
        self.PD.showGrid(True,True,0.7)
        self.PD.setLabel("left","I avg")
        self.data_point_list=[]
        self.time_list=[]
    
    def update_plot(self,new_data_point):
            self.time_list.append(len(self.time_list))
            self.data_point_list.append(new_data_point)
            if self.time_list>constants.plots_parameters.MAXIMUM_POINTS_PHOTODIODE:
                del self.data_point_list[0]
                del self.time_list[0]
            self.PD.plot(self.time_list,self.data_point_list,name="Photodiode avg",symbol="o", pen=None)
            
