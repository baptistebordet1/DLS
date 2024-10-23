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
from utils.GUI import free_running_ctl

from utils import constants

from utils.acquisition import interface_thread

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QThread

from pylablib.core.gui.widgets import container

import sys
import traceback
import logging
import serial


class Window(container.QWidgetContainer):
    def setup(self):
        super().__init__()
        super().setup(layout="hbox",name="window")
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.screensize=QtWidgets.QDesktopWidget().screenGeometry(self)
        self.screen_w=self.screensize.width()
        self.screen_h=self.screensize.height()
        self.dict_status={"current_action":"None", "detection_angle":None, "attenuation_value":None, 
                          "laser_status":"Off","arduino_connected":"Not connected",
                          "acquisition_progress":"No acquisition","error":"None"}
        self.dict_motors_positions={"Rotation motor pos":0,"Attenuation motor pos":0}
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
            self.status_tab.setMaximumWidth(int(0.19*self.screen_w))
            self.status_tab.setMaximumHeight(int(0.5*self.screen_h))
            self.status_tab.setup()
            self.status_control=self.status_tab.add_to_layout(status_ctl.Status(self))
            self.status_control.setup(self.dict_status) 
            
            self.plot_control_auto_corr_tab=self.add_child("control_auto_corr", container.QFrameContainer())
            self.plot_control_auto_corr_tab.setMaximumWidth(int(0.19*self.screen_w))
            self.plot_control_auto_corr_tab.setup()
            self.plot_control_auto_corr=self.plot_control_auto_corr_tab.add_to_layout(plots_ctl.plot_control_auto_corr(self))
            self.plot_control_auto_corr.setup(self.plot_auto_corr.auto_corr)
            
            self.plot_control_I_avg_tab=self.add_child("control_I_avg", container.QFrameContainer())
            self.plot_control_I_avg_tab.setMaximumWidth(int(0.19*self.screen_w))
            self.plot_control_I_avg_tab.setup()
            self.plot_control_I_avg=self.plot_control_I_avg_tab.add_to_layout(plots_ctl.plot_control_I_avg(self))
            self.plot_control_I_avg.setup(self.plot_PD.PD)
            
            self.plot_control_cross_corr_tab=self.add_child("control_cross_corr", container.QFrameContainer())
            self.plot_control_cross_corr_tab.setMaximumWidth(int(0.19*self.screen_w))
            self.plot_control_cross_corr_tab.setup()
            self.plot_control_cross_corr=self.plot_control_cross_corr_tab.add_to_layout(plots_ctl.plot_control_cross_corr(self))
            self.plot_control_cross_corr.setup(self.plot_cross_corr.cross_corr)
            self.add_padding(kind="vertical")
        
        # Motor control, Acquisition and Saving controls 
        
        with self.using_new_sublayout("motor_acquistion_saving_box", "grid"):
            
            # Motor control tabs
            self.motor_tabs=self.add_child("motor_control", container.QTabContainer(self))
            self.motor_tabs.setMaximumWidth(int(0.2*self.screen_w))
            self.motor_tabs.setMaximumHeight(int(0.17*self.screen_h))
            self.motor_rotation_tab=self.motor_tabs.add_tab("Motor rotation tab", "Rotation")
            self.motor_attenuation_tab=self.motor_tabs.add_tab("Motor attenuation tab", "Attenuation")
            self.motor_rotation_control=self.motor_rotation_tab.add_child("motor rotation", motor_ctl.Motor_rotation(self.motor_tabs))
            self.motor_rotation_control.setup()
            self.motor_attenuation_control=self.motor_attenuation_tab.add_child("motor rotation", motor_ctl.Motor_attenuation(self.motor_tabs))
            self.motor_attenuation_control.setup()
            self.add_padding(kind="vertical")
            
            #Free running tab 
            self.free_running_tab=self.add_to_layout(container.QFrameContainer(self),location=(2))
            self.free_running_tab.setup()
            self.free_running_tab.setMaximumWidth(int(0.2*self.screen_w))
            self.free_running_tab.setMaximumHeight(int(0.17*self.screen_h))
            self.free_running_control=self.free_running_tab.add_to_layout(free_running_ctl.Free_running(self))
            # free running is not setup here because it needs the acquisition control widget 
            
            # Saving tab
            self.saving_tab=self.add_to_layout(container.QFrameContainer(self),location=(5))
            self.saving_tab.setup()
            self.saving_tab.setMaximumWidth(int(0.2*self.screen_w))
            self.saving_tab.setMaximumHeight(int(0.17*self.screen_h))
            self.saving_control=self.saving_tab.add_to_layout(saving_ctl.Saving(self))
            self.saving_control.setup()
            
            # Acquistion tab
            self.acquisition_tab=self.add_to_layout(container.QFrameContainer(self),location=(3))
            self.acquisition_tab.setup()
            self.acquisition_tab.setMaximumWidth(int(0.2*self.screen_w))
            self.acquisition_tab.setMaximumHeight(int(0.19*self.screen_h))
            self.acquisition_control=self.acquisition_tab.add_to_layout(acquisition_ctl.Acquisition(self))
            self.acquisition_control.setup(self.saving_control)
            self.free_running_control.setup(self.acquisition_control) # see above for the reason 
            
                       
            # Sequence tab
            self.sequence_tab=self.add_to_layout(container.QFrameContainer(self),location=(4))
            self.sequence_tab.setup()
            self.sequence_tab.setMaximumWidth(int(0.2*self.screen_w))
            self.sequence_tab.setMaximumHeight(int(0.17*self.screen_h))
            self.sequence_control=self.sequence_tab.add_to_layout(sequence_ctl.Sequence(self))
            self.sequence_control.setup(self.saving_control)            
            
            self.initialize_default_values()
            
            self.start_interface_thread()
            
    # load config_dict into the different part of the control 
    
    def initialize_default_values(self):           
        self.acquisition_control.default_values(self.config_dict)
        self.sequence_control.default_values(self.config_dict)
        self.saving_control.default_values(self.config_dict)
    
    # update status and graph on the GUI 
    
    def update_GUI(self,new_dict_status, new_dict_motors):        
        self.dict_status=new_dict_status
        self.dict_motors_positions=new_dict_motors
        
        self.status_control.update_table(self.dict_status)
        self.motor_rotation_control.update_position(self.dict_motors_positions)
        self.motor_attenuation_control.update_position(self.dict_motors_positions)
        
    def start_interface_thread(self):
        # This is way to create a new thread which will have an event loop (other ways provided on documentation 
        # don't create a new thread for most of it or don't have an event loop because the run method is overwritten)
        
        # Step 1 Create a worker class whihc inherits from QObject (done in interface_thread.py)
        # Step 2 : Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker =interface_thread.Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.setup)
        self.worker.thread_finished.connect(self.thread.quit)
        self.worker.thread_finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.update_gui_data.connect(self.update_GUI)
        self.worker.fail_init_attenuator.connect(self.catch_motor_error)
        self.worker.error_attenuation_motor.connect(self.catch_motor_error)
        self.worker.error_rotation_motor.connect(self.catch_motor_error)
        self.free_running_control.free_running_start.connect(self.worker.prepare_free_running)
        self.free_running_control.free_runing_stop.connect(self.worker.stop_acquisition)
        self.acquisition_control.Acquisition_start.connect(self.worker.prepare_acquisition)
        self.acquisition_control.Acquisition_stop.connect(self.worker.stop_acquisition)
        self.motor_rotation_control.send_command_rotation.connect(self.worker.send_rotation_command)
        self.motor_attenuation_control.send_command_attenation.connect(self.worker.send_attenuator_command)
        self.motor_rotation_control.start_calib.connect(self.connect_signals_start_calib)
        self.worker.new_acquisition_data_auto_corr.connect(self.plot_auto_corr.update_plot)
        self.worker.new_acquisition_data_cross_corr.connect(self.plot_cross_corr.update_plot)
        self.worker.new_data_point_photodiode.connect(self.plot_PD.update_plot)
        # Step 6: Start the thread
        self.thread.start()
        
    # This is a work around to wait for a motor movement without blocking the entire code     
    def connect_signals_start_calib(self): 
        self.stop_PD_timer()
        self.motor_rotation_control.calib_window.send_calibration_step.connect(self.worker.send_calibration_turntable)
        self.worker.calibration_step_done.connect(self.motor_rotation_control.calib_window.one_measurement)
    
    def connect_signals_start_auto_find_attenuation(self):
        self.stop_PD_timer()
        self.motor_attenuation_control.send_command_attenuation_auto_find.connect(self.worker.send_auto_find_attenuator_command)
        self.worker.auto_find_att_step_done.connect(self.motor_attenuation_control.one_measurement_find_attenuation)
        self.motor_attenuation_control.auto_find_attenuation_finished.connect(self.start_PD_timer_after_auto_find_att)
        
    def start_PD_timer_after_auto_find_att(self):
        self.worker.PD_timer.start()
        self.worker.dict_status["current_action"]="None"
        
    def stop_PD_timer(self):
        self.worker.PD_timer.stop()

    @pyqtSlot(int,str)
    def catch_motor_error(self,nbr_try,error_code):
        if hasattr(self, 'motor_error_box'):
            self.motor_error_box.close()
        self.motor_error_box=QtWidgets.QMessageBox()
        self.motor_error_box.setWindowFlags(Qt.WindowStaysOnTopHint)
        if error_code=="2":
            self.motor_error_box.setWindowTitle("CRITICAL ERROR")
            self.motor_error_box.setText("LIMIT SWITCHES HAVE BEEN REACHED MOTOR STOPPED, PROGRAMM WILL QUIT NOW")
            log.critical("LIMIT SWITCHES HAVE BEEN REACHED !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.motor_error_box.exec_()
        elif error_code=="-5":
            self.motor_error_box.setWindowTitle("Initilisation error")
            self.motor_error_box.setText("Error while initiating the attenuator position, on Ok the programm will stop, \n Please make sure the attenuator is not blocked")
            self.motor_error_box.exec_()
            log.error("Error while initiating the attenuator position")
        elif error_code=="0":
            self.motor_error_box.setWindowTitle("Rotation error")
            if nbr_try==0:
                self.motor_error_box.setText("Error during the rotation of the turntable, The programm will attemp to restart the motor, \n Please Wait...")
                self.motor_error_box.exec_()
                log.error("Error during the rotation of the turntable")
                if self.worker.previous_command_arduino!="" and self.worker.previous_command_arduino[0:9]=="ROTATION":
                    command_str=self.worker.previous_command_arduino.split(",")
                    position_goal=int(command_str[1])     
                    self.worker.send_rotation_command(position_goal)
            else: 
                self.motor_error_box.setText("Rotation error happended again, The programm will stop the programm please verify the rotation motor under the turntable before restarting.")
                self.motor_error_box.exec_()
                log.error("Rotation error happended again")
        elif error_code=="1":
            self.motor_error_box.setWindowTitle("Attenuator error")
            if nbr_try==0:
                self.motor_error_box.setText("Error during the rotation of the attenuator, The programm will attemp to restart the motor, \n Please Wait...")
                self.motor_error_box.exec_()
                log.error("Error during the rotation of the attenuator")
                if self.worker.previous_command_arduino!="" and self.worker.previous_command_arduino[0:10]=="ATTENUATOR":
                    self.worker.arduino_comm.arduino.write(b"I")
                    command_str=self.worker.previous_command_arduino.split(",")
                    position_goal=int(command_str[1])     
                    self.worker.send_rotation_command(position_goal)
            else: 
                self.motor_error_box.setText("Attenuator error happended again, The programm will stop the programm please verify the attenuator motor before restarting.")
                self.motor_error_box.exec_()
                log.error("Attenuator error happended again")
                
    def closeEvent(self, *args, **kwargs):
        super(container.QWidgetContainer, self).closeEvent(*args, **kwargs)
        self.worker.thread_finished.emit() 
        

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

       
# Pop up window when connection Arduino or FPGA is lost, close the programm after

def catch_connection_lost(error_msg):
    connection_lost_box=QtWidgets.QMessageBox()
    connection_lost_box.setWindowFlags(Qt.WindowStaysOnTopHint)
    connection_lost_box.setWindowTitle("Connection lost")
    #TODO modify the if conditions yo make the differnece between fpag ascii and serial line 
    if "Arduino_not_connected" in error_msg:
        connection_lost_box.setText("Arduino not connected, on OK the programm will stop, \n please make sure Arduino is connected before restarting.")
        log.error("Arduino not connected")
    elif "Arduino" in error_msg:
        connection_lost_box.setText("Connection to Arduino lost, on OK the programm will stop, \n please make sure Arduino is connected before restarting.")
        log.error("Connection to Arduino lost")
    if "FPGA" in error_msg:
        connection_lost_box.setText("Connection to FPGA lost, on OK the programm will stop,\n please make sure FPGA is connected before restarting.")
        log.error("Connection to FPGA lost")
    connection_lost_box.exec_()
    window.close()
   
# get Exceptions and treat it 
    
class UncaughtHook(QObject):
    _exception_caught = pyqtSignal(str)
    connection_lost= pyqtSignal(str)
    
    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)
        # this registers the exception_hook() function as hook with the Python interpreter
        sys.excepthook = self.exception_hook

        # connect signal to execute the message box function always on main thread
        self._exception_caught.connect(show_exception_box)
        self.connection_lost.connect(catch_connection_lost)
    def exception_hook(self, exc_type, exc_value, exc_traceback):
        """Function handling uncaught exceptions.
        It is triggered each time an uncaught exception occurs. 
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # ignore keyboard interrupt to support console applications
            sys.__excepthook__(exc_type, exc_value, exc_traceback) 
        elif issubclass(exc_type, serial.SerialTimeoutException):
            if "Arduino" == serial.SerialTimeoutException.args[0]:
                log_msg = "Arduino"
            if "FPGA_data" == serial.SerialTimeoutException.args[0]:
                log_msg="FPGA_data"
            if "FPGA_ascii" == serial.SerialTimeoutException.args[0]:
                log_msg="FPGA_ascii"
            self.connection_lost.emit(log_msg)
        elif issubclass(exc_type, UnboundLocalError):
            if "Arduino" == UnboundLocalError.args[0]:
                log_msg = "Arduino_not_connected"
            if "FPGA_data" == UnboundLocalError.args[0]:
                log_msg="FPGA_data_not_connected"
            if "FPGA_ascii" == UnboundLocalError.args[0]:
                log_msg="FPGA_ascii_not_connected"
            self.connection_lost.emit(log_msg)
        else:
           
            log_msg = '\n'.join([''.join(traceback.format_tb(exc_traceback)),
                                 '{0}: {1}'.format(exc_type.__name__, exc_value)])
            # trigger message box show
            log.error("Uncaught exception:\n {0}".format(log_msg))
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
