# -*- coding: utf-8 -*-
"""
Created on Friday February 2 2024

@author: Baptiste Bordet 

"""
from utils.GUI import style_settings
from utils.GUI import motor_ctl
from utils.GUI import saving_ctl
from utils.GUI import status_ctl
from utils.GUI import display_ctl
from utils.GUI import plots_ctl
from utils.GUI import acquisition_ctl
from utils.GUI import sequence_ctl

from utils import constants

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread, QTimer

from pylablib.core.gui.widgets import container

import sys
import traceback
import logging

class interface_thread(QObject):
    pass
      
class Window(container.QWidgetContainer):
    def setup(self):
        super().__init__()
        super().setup(layout="hbox",name="window")
        #self.interface_thread=interface_thread()
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.screensize=QtWidgets.QDesktopWidget().screenGeometry(self)
        self.screen_w=self.screensize.width()
        self.screen_h=self.screensize.height()
        self.dict_status={"current_action":"None", "detection_angle":None, "attenuation_value":None, 
                          "laser_status":"Off","arduino_connected":"Not connected",
                          "acquisition_progress":"No acquisition","error":"None"}
        self.dict_motors_positions={"Rotation motor pos":0,"Attenuation motor pos":0}
        self.dict_acquisition={"corr_length":1000, "acq_time":30}
        self._config=constants.default_configuration(self)
        self.config_dict=self._config.config_dict
        

        # Plots tab
        
        with self.using_new_sublayout("plots", "vbox"):
            self.plot_auto_corr=self.add_child("plot_auto_corr", display_ctl.plot_auto_correlation(self))
            self.plot_auto_corr.setup()
            with self.using_new_sublayout("plots_PD_cross", "hbox"):
                self.plot_PD=self.add_child("plot_PD", display_ctl.plot_PD(self))
                self.plot_PD.setup()
                self.plot_cross_corr=self.add_child("plot_cross", display_ctl.plot_cross_correlation(self))
                self.plot_cross_corr.setup()

        # Status tab and plot controls 
        
        with self.using_new_sublayout("statuss","vbox"):
            self.status_tab=self.add_child("status",container.QFrameContainer())
            self.status_tab.setMaximumWidth(int(0.15*self.screen_w))
            self.status_tab.setMaximumHeight(int(0.5*self.screen_h))
            self.status_tab.setup()
            self.status_control=self.status_tab.add_to_layout(status_ctl.Status(self))
            self.status_control.setup(self.dict_status)
            
            self.plot_control_auto_corr_tab=self.add_child("control_auto_corr", container.QFrameContainer())
            self.plot_control_auto_corr_tab.setMaximumWidth(int(0.15*self.screen_w))
            self.plot_control_auto_corr_tab.setup()
            self.plot_control_auto_corr=self.plot_control_auto_corr_tab.add_to_layout(plots_ctl.plot_control_auto_corr(self))
            self.plot_control_auto_corr.setup(self.plot_auto_corr.auto_corr)
            
            self.plot_control_I_avg_tab=self.add_child("control_I_avg", container.QFrameContainer())
            self.plot_control_I_avg_tab.setMaximumWidth(int(0.15*self.screen_w))
            self.plot_control_I_avg_tab.setup()
            self.plot_control_I_avg=self.plot_control_I_avg_tab.add_to_layout(plots_ctl.plot_control_I_avg(self))
            self.plot_control_I_avg.setup(self.plot_PD.PD)
            
            self.plot_control_cross_corr_tab=self.add_child("control_cross_corr", container.QFrameContainer())
            self.plot_control_cross_corr_tab.setMaximumWidth(int(0.15*self.screen_w))
            self.plot_control_cross_corr_tab.setup()
            self.plot_control_cross_corr=self.plot_control_cross_corr_tab.add_to_layout(plots_ctl.plot_control_cross_corr(self))
            self.plot_control_cross_corr.setup(self.plot_cross_corr.cross_corr)
            self.add_padding(kind="vertical")
        
        # Motor control, Acquisition and Saving controls 
        
        with self.using_new_sublayout("motor_acquistion_saving_box", "grid"):
            
            # Motor control tabs
            self.motor_tabs=self.add_child("motor_control", container.QTabContainer(self))
            self.motor_tabs.setMaximumWidth(int(0.15*self.screen_w))
            self.motor_tabs.setMaximumHeight(int(0.15*self.screen_h))
            self.motor_rotation_tab=self.motor_tabs.add_tab("Motor rotation tab", "Rotation")
            self.motor_attenuation_tab=self.motor_tabs.add_tab("Motor attenuation tab", "Attenuation")
            self.motor_rotation_control=self.motor_rotation_tab.add_child("motor rotation", motor_ctl.Motor_rotation(self.motor_tabs))
            self.motor_rotation_control.setup()
            self.motor_attenuation_control=self.motor_attenuation_tab.add_child("motor rotation", motor_ctl.Motor_attenuation(self.motor_tabs))
            self.motor_attenuation_control.setup()
            self.add_padding(kind="vertical")
            
            # Saving tab
            self.saving_tab=self.add_to_layout(container.QFrameContainer(self),location=(4))
            self.saving_tab.setup()
            self.saving_tab.setMaximumWidth(int(0.15*self.screen_w))
            self.saving_tab.setMaximumHeight(int(0.15*self.screen_h))
            self.saving_control=self.saving_tab.add_to_layout(saving_ctl.Saving(self))
            self.saving_control.setup()
            
            # Acquistion tab
            self.acquisition_tab=self.add_to_layout(container.QFrameContainer(self),location=(2))
            self.acquisition_tab.setup()
            self.acquisition_tab.setMaximumWidth(int(0.15*self.screen_w))
            self.acquisition_tab.setMaximumHeight(int(0.15*self.screen_h))
            self.acquisition_control=self.acquisition_tab.add_to_layout(acquisition_ctl.Acquisition(self))
            self.acquisition_control.setup(self.saving_control)
                       
            # Sequence tab
            self.sequence_tab=self.add_to_layout(container.QFrameContainer(self),location=(3))
            self.sequence_tab.setup()
            self.sequence_tab.setMaximumWidth(int(0.15*self.screen_w))
            self.sequence_tab.setMaximumHeight(int(0.15*self.screen_h))
            self.sequence_control=self.sequence_tab.add_to_layout(sequence_ctl.Sequence(self))
            self.sequence_control.setup(self.saving_control)            
            
            self.initialize_default_values()
            
    # load config_dict into the differnt part of the control 
    
    def initialize_default_values(self):           
        self.acquisition_control.default_values(self.config_dict)
        self.sequence_control.default_values(self.config_dict)
        self.saving_control.default_values(self.config_dict)

    def update_GUI(self,new_dict_status, new_dict_motors):
        #TODO call this function in the Thread to update 
        # Maybe add here the updtae on plots too (if teh new arrays to plot are not too big)
        
        self.dict_status=new_dict_status
        self.dict_motors_positions=new_dict_motors
        
        self.status_control.update_indicators(self.dict_status)
        self.motor_rotation_control.update_position(self.dict_motors_positions)
        self.motor_attenuation_control.update_position(self.dict_motors_positions)
        


# logging file to trace exceptions

log = logging.getLogger(__name__)
handler = logging.FileHandler("logout.txt",mode="w")
log.addHandler(handler)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s\n  --------------------- ")
handler.setFormatter(formatter)
    
    
# Pop up window when an exeption is raised 
def show_exception_box(log_msg):
    """Checks if a QApplication instance is available and shows a messagebox with the exception message. 
    If unavailable (non-console application), log an additional notice.
    """
    if QtWidgets.QApplication.instance() is not None:
            errorbox = QtWidgets.QMessageBox()
            errorbox.setWindowFlags(Qt.WindowStaysOnTopHint)
            errorbox.setWindowTitle("Error Message")
            errorbox.setText("log of the error (last line will probably indicate what it is about):\n{0}".format(log_msg))
            errorbox.exec_()
            
    else:
        log.debug("No QApplication instance available.")
# get Exceptions and treat it 
class UncaughtHook(QObject):
    _exception_caught = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)
        # this registers the exception_hook() function as hook with the Python interpreter
        sys.excepthook = self.exception_hook

        # connect signal to execute the message box function always on main thread
        self._exception_caught.connect(show_exception_box)

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        """Function handling uncaught exceptions.
        It is triggered each time an uncaught exception occurs. 
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # ignore keyboard interrupt to support console applications
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            log_msg = '\n'.join([''.join(traceback.format_tb(exc_traceback)),
                                 '{0}: {1}'.format(exc_type.__name__, exc_value)])
            # trigger message box show
            log.critical("Uncaught exception:\n {0}".format(log_msg))
            self._exception_caught.emit(log_msg)
            

           


# Main 

app=0         
app = QtWidgets.QApplication([]) 
app,stylesheet=style_settings.set_style(app)
qt_exception_hook = UncaughtHook()
window = Window()
window.setup()
window.show()
app.exec_()
