# -*- coding: utf-8 -*-
"""
Created on Thursday May 2 2024

@author: Baptiste Bordet
"""

import PyQt5
import pyqtgraph
import numpy as np 

from pylablib.core.gui.widgets import container
from pylablib.gui.widgets.plotters import line_plotter

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
        
    def update_plot(self):
        self.plot1.yData
        
        
class plot_cross_correlation(container.QFrameContainer):
    def setup(self):
        super().setup()
        self.cross_corr=self.add_to_layout(pyqtgraph.PlotWidget(self))
        self.cross_corr.showGrid(True,True,0.7)
        self.cross_corr.setMouseMode(pyqtgraph.ViewBox.RectMode)
        self.cross_corr.getPlotItem().addLegend()
        self.cross_corr.getPlotItem().setLogMode(True)
        self.cross_corr.setLabel("left","Cross Correlation")  
        
    def update_plot(self):
        pass
        
class plot_PD(container.QFrameContainer):
    def setup(self):
        super().setup()
        self.PD=self.add_to_layout(pyqtgraph.PlotWidget(self))
        self.PD.setMouseMode(pyqtgraph.ViewBox.RectMode)
        self.PD.getPlotItem().addLegend()
        self.PD.showGrid(True,True,0.7)
        self.PD.setLabel("left","I avg")
    
    def update_plot(self):
        pass
