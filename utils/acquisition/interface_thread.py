# -*- coding: utf-8 -*-
"""
Created on Wednesday May 29 2024

@author: Baptiste Bordet
"""

from PyQt5.QtCore import QProcess, QProcessEnvironment, QObject, pyqtSignal, QTimer, pyqtSlot
from utils import arduino_interface
 
class Worker(QObject):
    
    #TODO modify the update command according to the data needed for transfer
    update_gui_data=pyqtSignal(dict, dict )
    thread_finished=pyqtSignal()
    new_acquisition_data=pyqtSignal(bytes)
    fail_init_attenuator=pyqtSignal(int,str)
    error_rotation_motor=pyqtSignal(int,str)
    error_attenuation_motor=pyqtSignal(int,str)
    critical_error=pyqtSignal(int,str)
    
    def setup(self):
        self.dict_status={"current_action":"None", "detection_angle":None, "attenuation_value":None, 
                          "laser_status":"Off","arduino_connected":"Not connected",
                          "acquisition_progress":"No acquisition","error":"None"}
        self.dict_motors_positions={"Rotation motor pos":150,"Attenuation motor pos":0}
        self.dict_acquisition={"corr_length":1000, "acq_time":30}
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
        
        #TODO add here the values of the previous command send to arduino (in case motor is stalled to resend the command)
        self.previous_command_arduino=""
        
    def read_arduino(self):
        while self.arduino_comm.arduino.in_waiting()>0:
            self.received_message=self.arduino_comm.arduino.read_until()
            if "CRITICAL_ERROR" in self.received_message:
                self.critical_error.emit(-1000,"2")
            elif self.received_message == "Error_init_attenuator\n":
                self.fail_init_attenuator.emit(2,"-5")
            elif self.received_message == "error_rotation_motor\n":
                self.error_rotation_motor.emit(self.tried_restart_rotation,"0")
                self.tried_restart_rotation=self.tried_restart_rotation+1
            elif self.received_message=="error_attenuation_motor\n":
                self.error_attenuation_motor.emit(self.tried_restart_attenuator,"1")
                self.tried_restart_attenuator=self.tried_restart_attenuator+1
            elif "motor_rotating" in self.received_message:
                position_motor=self.arduino_comm.converter_angle_rotation_turntable_dec_to_deg(self, float(self.received_message[14:-2]))
                self.dict_motors_positions["Rotation motor pos"]=position_motor
            elif "movement_finished" in self.received_message:
                position_motor=self.arduino_comm.converter_angle_rotation_turntable_dec_to_deg(self, float(self.received_message[17:-2]))
                self.dict_motors_positions["Rotation motor pos"]=position_motor
                self.dict_status["current_action"]="None"
            elif "movement_attenuation_finished" in self.received_message:
                #TODO check the value of attenuator position maybe convert it via dict in constants 
                position_attenuator=int(self.received_message[29:-2])
                self.dict_motors_positions["Attenuation motor pos"]=position_attenuator
                self.dict_status["current_action"]="None"

    @pyqtSlot(float)            
    def send_rotation_command(self,position_goal):
        #TODO test that the condition is in the right order
        if self.dict_motors_positions["Rotation motor pos"]-position_goal>position_goal-self.dict_motors_positions["Rotation motor pos"]:
            direction_rotation="P"
        else: 
            direction_rotation="N"
        self.arduino_comm.send_rotation_turntable(position_goal, direction_rotation)
        self.previous_command_arduino="ROTATION,"+str(position_goal)
    
    @pyqtSlot(int) 
    def send_attenuator_command(self,position_goal):
        self.arduino_comm.send_rotation_attenuator(position_goal)
        self.previous_command_arduino="ATTENUATOR"+str(position_goal)
        
    def send_update_gui_command(self):
        self.update_gui_data.emit(self.dict_status, self.dict_motors_positions)
     
    @pyqtSlot(str, str, str, str, int, int)
    def start_acquisition(self,folder_path, filename, extenstion_file, separator, tau_max, acquisition_time):
        print("started_acquisition")
        # and emit signal to send to update plots (probably better to send bytes than array)
        self.sub_process_acquisition=process_Acquisition()
        self.sub_process_acquisition.setup(self)
        
    @pyqtSlot()
    def stop_acquisition(self):
        pass
    #TODO send message to fpga to stop communication 
        
class process_Acquisition():
    def setup(self,worker):
       self.worker=worker
       self.env=QProcessEnvironment.systemEnvironment()
       self.p = QProcess()
       self.p.setProcessEnvironment(self.env)
       self.p.start("python", ["utils/acquisition/acquisition_process.py"])
       self.p.readyReadStandardOutput.connect(self.handle_stdout)
       self.p.readyReadStandardError.connect(self.handle_stderr)
       self.p.finished.connect(self.process_finished)
   
    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        raise Exception(stderr)
        
    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        data=bytes(data)
        self.worker.new_acquisition_data.emit(data)

    def process_finished(self):
        print(self.p.ExitStatus())
        print("finished")
        self.p = None