# -*- coding: utf-8 -*-
"""
Created on Wednesday May 29 2024

@author: Baptiste Bordet
"""

from PyQt5.QtCore import QProcess, QProcessEnvironment, QObject, pyqtSignal, QTimer, pyqtSlot
from utils import arduino_interface, FPGA_interface, constants
from pathlib import Path 
import os
import struct 
import numpy as np
import time

class Worker(QObject):
    
    update_gui_data=pyqtSignal(dict, dict )
    thread_finished=pyqtSignal()
    new_acquisition_data_auto_corr=pyqtSignal(bytes,int)
    new_acquisition_data_cross_corr=pyqtSignal(bytes,int)
    fail_init_attenuator=pyqtSignal(int,str)
    error_rotation_motor=pyqtSignal(int,str)
    error_attenuation_motor=pyqtSignal(int,str)
    critical_error=pyqtSignal(int,str)
    kill_process=pyqtSignal()
    calibration_step_done=pyqtSignal(float)
    auto_find_att_step_done=pyqtSignal()
    new_data_point_photodiode=pyqtSignal(int)

    def setup(self):
        self.dict_status={"current_action":"None", "detection_angle":None, "attenuation_value":None, 
                          "laser_status":"Off","arduino_connected":"Not connected",
                          "acquisition_progress":"No acquisition","error":"None"}
        self.dict_motors_positions={"Rotation motor pos":0,"Attenuation motor pos":0}
        self.update_timer=QTimer(self)
        self.update_timer.setInterval(100)
        self.update_timer.timeout.connect(self.send_update_gui_command)
        self.update_timer.start()
        self.tried_restart_attenuator=0
        self.tried_restart_rotation=0
        #TODO uncomment this part when arduino is connected 
        self.arduino_comm=arduino_interface.Arduino_communication()
        self.read_arduino_timer=QTimer(self)
        self.read_arduino_timer.setInterval(100)
        self.read_arduino_timer.timeout.connect(self.read_arduino)
        self.read_arduino_timer.start()
        self.previous_command_arduino=""
        

        self.PD_timer=QTimer(self)
        self.PD_timer.setInterval(1000)
        self.PD_timer.timeout.connect(self.ask_photodiode_value)
        #self.fpga_serial_ascii=FPGA_interface.FPGA_serial_ASCII()
        #self.fpga_serial_data=FPGA_interface.FPGA_serial_data() # to be passed in subprocess 
        #self.PD_timer.start()
        
    def ask_photodiode_value(self):
        self.photodiode_val=self.fpga_serial_ascii.ask_pd_value()
        self.new_data_point_photodiode.emit(self.photodiode_val)
        # TODO verify that photodiode_val is of type int 
            
    def read_arduino(self):
        while self.arduino_comm.arduino.in_waiting>0:
            self.received_message=self.arduino_comm.arduino.read_until()
            if b"CRITICAL_ERROR" in self.received_message:
                self.critical_error.emit(-1000,"2")
            elif self.received_message == b"Error_init_attenuator\n":
                self.fail_init_attenuator.emit(2,"-5")
            elif self.received_message == b"error_rotation_motor\n":
                self.error_rotation_motor.emit(self.tried_restart_rotation,"0")
                self.tried_restart_rotation=self.tried_restart_rotation+1
            elif self.received_message==b"error_attenuation_motor\n":
                self.error_attenuation_motor.emit(self.tried_restart_attenuator,"1")
                self.tried_restart_attenuator=self.tried_restart_attenuator+1
            elif b"motor_rotating" in self.received_message:
                position_motor=self.arduino_comm.converter_angle_rotation_turntable_dec_to_deg(float(str(self.received_message[15:-2].decode("utf-8"))))
                self.dict_motors_positions["Rotation motor pos"]=position_motor
            elif b"movement_finished" in self.received_message:
                position_motor=self.arduino_comm.converter_angle_rotation_turntable_dec_to_deg(float(str(self.received_message[18:-2].decode("utf-8"))))
                self.dict_motors_positions["Rotation motor pos"]=position_motor
                self.dict_status["current_action"]="None"
                print("end")
            elif b"finished_movement" in self.received_message:
                self.position_calibration=self.received_message[31:-2]
                self.calibration_step_done.emit(float(str(self.position_calibration.decode("utf-8"))))
            elif b"movement_attenuation_finished" in self.received_message:
                if self.auto_find==1:
                    self.auto_find_att_step_done.emit(self)
                position_attenuator=int(self.received_message[30:])
                self.dict_motors_positions["Attenuation motor pos"]=list(constants.Arduino_interface.ATTENUATOR_MOTOR_POSITION.keys())[list(constants.Arduino_interface.ATTENUATOR_MOTOR_POSITION.values()).index(str(position_attenuator))]
                self.dict_status["current_action"]="None"
        
                
    def send_update_gui_command(self):
        self.update_gui_data.emit(self.dict_status, self.dict_motors_positions)
        
    @pyqtSlot(float)            
    def send_rotation_command(self,position_goal):
        #TODO test that the condition is in the right order

        self.arduino_comm.send_rotation_turntable(position_goal)
        self.previous_command_arduino="ROTATION,"+str(position_goal)
        self.dict_status["current_action"]="Rotation turntable"
        
    @pyqtSlot()
    def send_calibration_turntable(self):
        self.arduino_comm.send_rotation_calibration_turntable()
    
    @pyqtSlot(int)
    def send_auto_find_attenuator_command(self,position_goal):
        self.arduino_comm.send_rotation_attenuator(position_goal)
        self.auto_find=1
        self.dict_status["current_action"]="Search attenuator best position"
        
    @pyqtSlot(int) 
    def send_attenuator_command(self,position_goal):
        self.arduino_comm.send_rotation_attenuator(position_goal)
        self.previous_command_arduino="ATTENUATOR"+str(position_goal)
        self.auto_find=0
        self.dict_status["current_action"]="Move attenuator"
         
    @pyqtSlot(str, str, str, str, str, int, int)
    def prepare_acquisition(self,folder_path, filename, extenstion_file, separator, exp_type,  tau_max, acquisition_time):
        print("started_acquisition")
        self.sub_process_acquisition=process_Acquisition()
        self.sub_process_acquisition.setup(self,folder_path,filename,extenstion_file,separator, exp_type, tau_max, acquisition_time)
   
    @pyqtSlot(str,int)
    def start_acquisition(self,exp_type,acq_time):
        self.acquisition_timer=QTimer()
        self.acquisition_timer.setSingleShot(True)
        self.acquisition_timer.setInterval(acq_time)
        self.acquisition_timer.timeout.connect(self.stop_acquisition)
        self.PD_timer.stop()
        self.fpga_serial_ascii.start_acq(exp_type)
        self.PD_timer.start()
        self.acquisition_timer.start()
        self.dict_status["current_action"]="Acquisition"
    
    @pyqtSlot(str,int)
    def prepare_free_running(self, exp_type, tau_max):
        self.sub_process_acquisition=free_running_Acquisition()
        self.sub_process_acquisition.setup(self,exp_type,tau_max)
        
    @pyqtSlot(str)
    def start_free_running(self,exp_type):
        self.PD_timer.stop()
        self.fpga_serial_ascii.start_acq(exp_type)
        self.PD_timer.start()
        self.dict_status["current_action"]="Free running"
        
    @pyqtSlot()
    def stop_acquisition(self):
        self.PD_timer.stop()
        self.fpga_serial_ascii.stop_acq()
        self.PD_timer.start()
        self.kill_process.emit()
        self.dict_status["current_action"]="None"
        
class process_Acquisition(QObject):
    ready_for_acquisition=pyqtSignal(str,int)
    
    def setup(self,worker,folder_path,filename,extenstion_file,separator, exp_type, tau_max, acquisition_time):
       self.worker=worker
       self.folder_path=folder_path
       self.filename=filename
       self.extension_file=extenstion_file
       self.separator=separator
       self.exp_type=exp_type
       self.tau_max=tau_max
       constants.Acquisition_time_limit.set_points_number_plot(constants.Acquisition_time_limit, self.tau_max)
       self.acquisition_time=acquisition_time
       self.message_length=constants.Acquisition_parameters.LENGTH_TYPE_EQ[self.exp_type]
       self.env=QProcessEnvironment.systemEnvironment()
       self.p = QProcess()
       self.p.setProcessEnvironment(self.env)
       self.G="h"
       self.filesave=open(Path(os.path.join(self.folder_path,self.filename,self.extension_file)),"w")
       #TODO modify here the passed arguments to be serial fpga 
       self.p.start("python", ["utils/acquisition/acquisition_process.py",self.G])
       self.p.readyReadStandardOutput.connect(self.handle_process_ready)
       self.p.readyReadStandardError.connect(self.handle_stderr)
       self.p.finished.connect(self.process_finished)
       self.ready_for_acquisition.connect(self.worker.start_acquisition)
       self.worker.kill_process.connect(self.finish_process)
       
    @pyqtSlot()
    def finish_process(self):
        self.p.kill()
        
    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        raise Exception(stderr)
        
    def handle_process_ready(self):
        data=self.p.readAllStandardOutput()
        if data=="ready":
            self.p.readyReadStandardOutput.disconnect(self.handle_process_ready)
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.ready_for_acquisition.emit(self.exp_type,self.acquisition_time)
            
            
    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        data_use=struct.unpack(">H"+"H"*self.message_length,data)
        self.data_array=np.array(data_use,dtype=np.uint16)
        self.data_array=np.interp(self.data_array,[0,65535],[0,1])
        if self.exp_type=="AUTO11" or self.exp_type=="AUTO22" or self.exp_type=="AUTO12":
            self.worker.new_acquisition_data_auto_corr.emit(self.data_array,self.exp_type)
        if self.exp_type=="CROSS":
            self.worker.new_acquisition_data_cross_corr.emit(self.data_array,self.exp_type)
        self.filesave.write(np.array2string(self.data_array,separator=self.separator,max_line_width=np.inf)+"\n")

    def process_finished(self):
        print(self.p.ExitStatus())
        print("finished")
        self.p = None
        self.filesave.close()

class free_running_Acquisition(QObject):
    ready_for_acquisition=pyqtSignal(str)
    def setup(self,worker, exp_type,tau_max):
       self.worker=worker
       self.exp_type=exp_type
       self.tau_max=tau_max
       self.message_length=constants.Acquisition_parameters.LENGTH_TYPE_EQ[self.exp_type]
       constants.Acquisition_time_limit.set_points_number_plot(constants.Acquisition_time_limit, self.tau_max)
       self.env=QProcessEnvironment.systemEnvironment()
       self.p = QProcess()
       self.p.setProcessEnvironment(self.env)
       self.G="h"
       #TODO modify here the passed arguments to be serial fpga 
       self.p.start("python", ["utils/acquisition/acquisition_process.py",self.G])
       self.p.readyReadStandardOutput.connect(self.handle_process_ready)
       self.p.readyReadStandardError.connect(self.handle_stderr)
       self.p.finished.connect(self.process_finished)
       self.ready_for_acquisition.connect(self.worker.start_free_running)
       self.worker.kill_process.connect(self.finish_process)
       
    @pyqtSlot()
    def finish_process(self):
        self.p.kill()
        
    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        raise Exception(stderr)
        
    def handle_process_ready(self):
        data=self.p.readAllStandardOutput()
        if data=="ready":
            self.p.readyReadStandardOutput.disconnect(self.handle_process_ready)
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.ready_for_acquisition.emit(self.exp_type)
                        
    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        data_use=struct.unpack(">H"+"H"*self.message_length,data)
        self.data_array=np.array(data_use,dtype=np.uint16)
        self.data_array=np.interp(self.data_array,[0,65535],[0,1])
        self.worker.new_acquisition_data.emit(self.data_array)

    def process_finished(self):
        print(self.p.ExitStatus())
        print("finished")
        self.p = None
        
        
