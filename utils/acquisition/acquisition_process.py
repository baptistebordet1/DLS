# -*- coding: utf-8 -*-
"""
Created on Tuesday May 28 2024

@author: Baptiste Bordet 
"""
import sys



fpga_serial_data=sys.argv[1]


class data_receive_process():

    def __init__(self,serial_data):
        self.serial_data=serial_data
        
    def receive_data(self):
        sys.stdout.write("ready")
        sys.stdout.flush()
        self.serial_data.reset_input_buffer()
        
        while True: 
            data=self.serial_data.read(16*2*256) 
            sys.stdout.buffer.write(data)
            sys.stdout.flush()
            #TODO chnage the number of bits received
 
data_receiving=data_receive_process(fpga_serial_data)
data_receiving.receive_data()