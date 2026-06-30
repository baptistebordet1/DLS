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
        self.parity=serial.PARITY_NONE
        self.bytesize=serial.EIGHTBITS
        self.stop_bits=serial.STOPBITS_ONE
        
        for port, desc, hwid in sorted(list_ports.comports()):
            #TODO adjust name in desc according to Bruno's setup
            if "USB Serial Port" in desc:
                self.FPGA_ascii_port=port
        try: 
            self.FPGA_ascii = serial.Serial(port=self.FPGA_ascii_port, baudrate=self.baudrate,parity=self.parity, bytesize=self.bytesize,stopbits=self.stop_bits,timeout=1)
        except UnboundLocalError:
            raise UnboundLocalError("FPGA_ascii")
        
    def ask_pd_value(self):
        self.FPGA_ascii.write("IPD\r".encode("ASCII"))
        pd_value=int.from_bytes(self.FPGA_ascii.read(2), byteorder="big")
        pd_value=pd_value/4095*10.45 # 12 bits adc on fpga with a full scale at 10.45V
        # check if all bits are read 
        # if len(pd_value)!=16:
        #     raise Exception("Comm error with FPGA") 
        # else: 
        
        return pd_value
    def start_acq(self,acq_type):
        self.FPGA_ascii.write(acq_type.encode("ASCII"))
        self.FPGA_ascii.write("START".encode("ASCII"))
    def stop_acq(self):
        self.FPGA_ascii.write("STOP".encode("ASCII"))
        
    def close_comm(self):
        self.FPGA_ascii.close()
        
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
        