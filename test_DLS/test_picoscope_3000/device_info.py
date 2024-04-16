# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 16:23:51 2023

@author: Raphael Girault
"""

from picosdk.ps3000a import ps3000a

device= ps3000a.open_unit()
print('Device info: {}'.format(device.info))

device.close()


with ps3000a.open_unit() as device:
    print('Device info: {}'.format(device.info))