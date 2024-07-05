# -*- coding: utf-8 -*-
"""
Created on Monday April 15 2024

@author: Baptiste Bordet
"""

class Arduino_interface():
    REDUCTION_RATIO=100
    INITIALISATION_TIME=3 #time to be sure serial connection is initialised 
    TURNTABLE_ANGLE_MIN_DEG=0 # 0° angle 
    TURNTABLE_ANGLE_MIN_DEC=367.2 # To calibrate angle corresponding to the O° angle 
    TURNTABLE_ANGLE_MAX_DEG=180 # 180° angle 
    TURNTABLE_ANGLE_MAX_DEC=TURNTABLE_ANGLE_MIN_DEC+REDUCTION_RATIO*180 # calculated angle from the 0 position thanks to reduction ratio
    ATTENUATOR_MOTOR_POSITION={0:"40", 1:"80", 2:"120",3:"160",4:"200",5:"240",6:"280",7:"320",8:"360"}
    CALIBRATION_STEPS= 200 # (must be an int) number of steps done before a new measurement is made for the turntable calibration
    MAX_ROTATION_FULL_TURN=5600 # max number of rotation of the rotation motor (one full trun is 200 steps)
    PHOTODIODE_ATTENUATOR_THRESHOLD=45 # threshold for the photiode for autofind of attenuation 
    
class Acquisition_time_limit():
    TAU_MIN=0 # ms
    TAU_MAX=1000 # ms
    ACQ_TIME_MIN=1 #s 
    ACQ_TIME_MAX=100 #s
    
class Acquisition_parameters():
    LENGTH_TYPE_EQ={"AUTO11":160, "AUTO22":160, "AUTO12":320, "CROSS":320} #TODO modify accordingly the message lengths 

class plots_parameters():
    MAXIMUM_POINTS_PHOTODIODE=300 # 5 min at 1 point/s 
    
class default_configuration():
    def __init__(self,window):
        from PyQt5.QtWidgets import  QMessageBox
        import sys 
        import re
        self.config_dict={}
        self.config_file=open("utils/configuration.txt","r") # change to utils folder when moving to main file 
        self.config_file_lines=self.config_file.readlines()
        for i, line in enumerate(self.config_file_lines):
            self.config_file_lines[i]=line.split("#")[0]
        for i, line in enumerate(self.config_file_lines):
            line = re.sub(r"[\n\t\s]*", "", line)
            line_splitted=line.split(":")
            if "int" in line_splitted[0]:
                if line_splitted[1]=="":
                    line_splitted[1]=-1000 # default values to be ignored 
                key_dict=line_splitted[0].replace("_int","")
                try:
                    self.config_dict[key_dict]=int(line_splitted[1])
                except ValueError:
                    QMessageBox.warning(window,
                        "default config error ", f"Invalid argument of parameter : {key_dict}\n  Quitting the program... ")
                    sys.exit()
            elif "float" in line_splitted[0]:
                if line_splitted[1]=="":
                    line_splitted[1]=-1000 # default values to be ignored 
                key_dict=line_splitted[0].replace("_float","")
                try:
                    self.config_dict[key_dict]=float(line_splitted[1])
                except ValueError:
                    QMessageBox.warning(
                        window, "default config error ", f"Invalid argument of parameter : {key_dict}\n  Quitting the program... ")
                    sys.exit()
            else: 
                key_dict=line_splitted[0]
                self.config_dict[key_dict]=line_splitted[1]
        