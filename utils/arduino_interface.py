# -*- coding: utf-8 -*-
"""
Created on Friday January 26 2024

@author: Baptiste Bordet

This file is part of the DLS Control code used in LIPhy.
"""

import serial 
import time
import sys 
import os
sys.path.append(os.path.dirname(__file__))
from constants import Arduino_interface
from serial.tools import list_ports

class Arduino_communication():
    def __init__(self,baud_rate=115200, timeout=5):
        """
        Parameters
        ----------
        baud_rate : int, optional
            Baud rate for serial communication with Arduino. 
            The default is 115200.
        timeout : int, optional
            Timeout for reading and writing values if this happens 
        Returns
        -------
        None.

        """
        for port, desc, hwid in sorted(list_ports.comports()): # list all available ports
        #TODO check if this works on other computers with Arduino Mega 2560
            if "USB Serial" in desc:
                arduino_port=port  
        try: 
            self.arduino = serial.Serial(arduino_port, baud_rate,timeout=timeout, write_timeout=timeout)
        except UnboundLocalError:
            raise UnboundLocalError("Arduino")
            
        time.sleep(Arduino_interface.INITIALISATION_TIME) # here to let enough time to Initialise connection with arduino 
         
        # Ping arduino to see if connected 
        
        string_to_send=b"C"
        self.arduino.write(string_to_send)
        is_connected=self.arduino.read_until()
        if b"ALIVE" not in is_connected:
            raise serial.SerialTimeoutException("Arduino")
        self.arduino.write(b"I")


    
    """
    UNIT CONVERSIONS 
    """ 
    
    
    def converter_angle_rotation_turntable_deg_to_dec(self,angle_deg):
        """
        Converts angle in degree of the turntable to angle in decimal (encoder)

        Parameters
        ----------
        angle_deg : float 
           Angle in degree 

        Returns
        -------
        angle_dec : float
            Angle in decimal(encode format)

        """
        angle_dec = (angle_deg - Arduino_interface.TURNTABLE_ANGLE_MIN_DEG) * (Arduino_interface.TURNTABLE_ANGLE_MAX_DEC - Arduino_interface.TURNTABLE_ANGLE_MIN_DEC) / (Arduino_interface.TURNTABLE_ANGLE_MAX_DEG - Arduino_interface.TURNTABLE_ANGLE_MIN_DEG) + Arduino_interface.TURNTABLE_ANGLE_MIN_DEC;
        return angle_dec
    def converter_angle_rotation_turntable_dec_to_deg(self,angle_dec):
        """
        Convert angle from rotary encoder to angle of the turntable. 

        Parameters
        ----------
        angle_dec : float 
            angle from encoder in decimal 

        Returns
        -------
        angle_deg : float
            angle of the turntable in degre

        """
        angle_deg = (angle_dec - Arduino_interface.TURNTABLE_ANGLE_MIN_DEC) * (Arduino_interface.TURNTABLE_ANGLE_MAX_DEG - Arduino_interface.TURNTABLE_ANGLE_MIN_DEG) / (Arduino_interface.TURNTABLE_ANGLE_MAX_DEC - Arduino_interface.TURNTABLE_ANGLE_MIN_DEC) + Arduino_interface.TURNTABLE_ANGLE_MIN_DEG;
        return angle_deg
    
    def hex_to_float(self,hexa_val):
        """
        Convert hexadecimal values send by the serial connection of the arduino 
        to a float type. Used for the reading of position of the absolute encoder

        Parameters
        ----------
        hexa_val : String
            string representing the float value

        Returns
        -------
        float_val : float
            position in the float format

        """
        return float.fromhex(hexa_val[::-1])
    
    def var_to_byte(self,variable):
        """
        Convert the value to byte to be send 

        Parameters
        ----------
        variable : int or string or float
            the variable to send can be int, string, float

        Returns
        -------
        byte_var : bytes
            bytes representation of the variable

        """
        if type(variable)==str:
            return bytes(variable,encoding="utf-8")
        if type(variable)==int:
            return bytes(variable)
        if type(variable)==float:
            return bytes(str(variable),encoding="utf-8")
      
        
    """
    SENDING COMMANDS
    """
    
        
    def send_rotation_turntable(self, angle_rotation): 
        """
        Parameters
        ----------
        angle_rotation : float 
            angle to reach (not how much you move).
            it is in degree and is converted just before being send to the arduino
        Returns
        -------
        None.

        """
        angle_rotation_dec=self.converter_angle_rotation_turntable_deg_to_dec(angle_rotation)
        try:
            string_to_send="MT"+str(angle_rotation_dec) # angle_rotation_dec is float 
            self.arduino.write(self.var_to_byte(string_to_send)) 
        except serial.SerialTimeoutException:
            raise serial.SerialTimeoutException("Arduino")
       
    def send_rotation_calibration_turntable(self):
        try:
            string_to_send="ET"+str(Arduino_interface.CALIBRATION_STEPS)
            self.arduino.write(self.var_to_byte(string_to_send)) 
        except serial.SerialTimeoutException:
            raise serial.SerialTimeoutException("Arduino")
        
    
    def send_rotation_attenuator(self, position_to_reach):
        """
        # position to reach is the number shown on screen 0,1,2,3.. it is converted here in deg 
        Parameters
        ----------
        position_to_reach : int
            attenuator number to reach. 

        Returns
        -------
        None.

        """
        angle_to_reach=Arduino_interface.ATTENUATOR_MOTOR_POSITION[position_to_reach]
        try: 
            string_to_send="MA"+angle_to_reach
            self.arduino.write(self.var_to_byte(string_to_send))
        except serial.SerialTimeoutException:
            raise serial.SerialTimeoutException("Arduino")
            
    def close(self):
         """
         Close communication with Arduino  
         """
         self.arduino.close()
          

# try :
#     Arduino_comm=Arduino_communication()
# except serial.SerialTimeoutException as err:
#     raise
#     print(sys.exc_info()[1].args[0])
   

# Arduino_comm.send_rotation_turntable(80, "P")
# Arduino_comm.close()
