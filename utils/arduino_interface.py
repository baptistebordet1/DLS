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
            Timeout for reading and writing values if this appends 
        Returns
        -------
        None.

        """
        for port, desc, hwid in sorted(list_ports.comports()): # list all available ports
            if "COM3" in port:
                arduino_port=port  
        try: 
            self.arduino = serial.Serial(arduino_port, baud_rate,timeout=timeout, write_timeout=timeout)
        except UnboundLocalError:
            print("Arduino not connected or not recognized by the computer") # To change send signal to interface graphique 
            raise
            
        time.sleep(Arduino_interface.INITIALISATION_TIME) # here to let enough time to Initialise connection with arduino 
    
    
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
        to afloat type. Used for the reading of position of the absolute encoder

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
        Convert the string value to byte to be send 

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
        
    def send_rotation_turntable(self, angle_rotation, direction_rotation): 
        """
        Parameters
        ----------
        angle_rotation : int 
            angle to reach (not how much you move).
            it is in degree and is converted just before being send to the arduino
        direction_rotation : str
            "P" or "N" indicate the direction for rotation 

        Returns
        -------
        None.

        """
        angle_rotation_dec=self.converter_angle_rotation_turntable_deg_to_dec(angle_rotation)
        try:
            string_to_send="MT"+direction_rotation+str(angle_rotation_dec)
            self.arduino.write(self.var_to_byte(string_to_send)) # angle_rotation_dec is float 
        except serial.SerialTimeoutException:
            print("connection error")
            raise
        movement_finished=False
        while movement_finished==False:
            if self.arduino.inWaiting()==0:
                time.sleep(0.1)
            else:
                try:
                    message_arduino_movement=self.arduino.read_until()
                except serial.SerialException:
                    print("connection error")
                    raise
                if message_arduino_movement in "movement_finished":
                    movement_finished=True
                    try: 
                       self.position_motor_rotation_dec=self.arduino.read_until()
                    except serial.SerialException:
                       print("connection error")
                       raise
        
                       
    def send_read_position_turntable(self):
        """
        Returns
        -------
        position_turntable : float
            position of the turntable (in encoder format maybe changed later)

        """
        # check if there is something in the buffer if yes, remove it
        if self.arduino.inWaiting()>0:
            self.arduino.reset_input_buffer()
        self.arduino.write(self.var_to_byte("RT"))
        while self.arduino.inWaiting()==0:
            time.sleep(0.1)
        try: 
            position_turntable=self.arduino.read_until()
            position_turntable=self.hex_to_float(position_turntable)
        except serial.SerialException:
            print("connection erorr")
            raise
        return position_turntable
    
    def send_rotation_attenuator(self ):
        pass
    #TODO test the attenuator motor with the new microstep driver to know how 
    #TODO to deal with it and same for reading the position
                           
    def close(self):
         """
         Close communication with Arduino  
         """
         self.arduino.close()
         print ('Connection to Arduino closed')
          


Arduino_comm=Arduino_communication()
Arduino_comm.send_rotation_turntable(80, "P")
Arduino_comm.close()
