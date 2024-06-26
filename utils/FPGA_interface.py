# -*- coding: utf-8 -*-
"""
Created on Thursday June 13 2024

@author: Baptiste Bordet

This file is part of the DLS Control code used in LIPhy.
"""


from serial.tools import list_ports
import serial 


class FPGA_serial_ASCII():
    def __init__(self):
        self.baudrate=9600
        self.parity=serial.PARITY_EVEN
        self.bytesize=serial.EIGHTBITS
        
        for port, desc, hwid in sorted(list_ports.comports()):
            #TODO adjust name in desc according to Bruno's setup
            if "FPGA" in desc:
                self.FPGA_ascii_port=port
        try: 
            self.FPGA_ascii = serial.Serial(self.FPGA_ascii_port, baud_rate=self.baudrate,parity=self.parity, bytesize=self.bytesize)
        except UnboundLocalError:
            raise UnboundLocalError("FPGA_ascii")
        
    def ask_pd_value(self):
        self.FPGA_ascii.write("ACQ_PD".encode("ASCII"))
        pd_value=self.FPGA_ascii.read_until()
        return pd_value
    def start_acq(self,acq_type):
        self.FPGA_ascii.write(acq_type.encode("ASCII"))
        self.FPGA_ascii.write("START".encode("ASCII"))
    def stop_acq(self):
        self.FPGA_ascii.write("STOP".encode("ASCII"))
        
    #sequence is just a succession of acquistion process maybe a way to reuse it 

class FPGA_serial_data():
    def __init__(self):
        self.baudrate=115200
    
        for port, desc, hwid in sorted(list_ports.comports()):
            if "FPGA" in desc:
                #TODO adjust name in desc according to Bruno's setup
                self.FPGA_serial_port=port
        try: 
            self.FPGA_ascii = serial.Serial(self.FPGA_serial_port, baud_rate=self.baudrate)
        except UnboundLocalError:
            raise UnboundLocalError("FPGA_serial")
        