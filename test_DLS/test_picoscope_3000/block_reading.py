# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 16:33:19 2023

@author: Raphael Girault
"""

from picosdk.ps3000a import ps3000a
from picosdk.PicoDeviceEnums import picoEnum
from picosdk.functions import assert_pico_ok
from ctypes import byref, c_int16, c_uint32, sizeof

SAMPLES = 2000
OVERSAMPLING = 1


def get_timebase(device, wanted_time_interval):
    current_timebase = 1
    old_time_interval = None
    time_interval = 0
    time_units = c_int16()
    max_samples = c_uint32()
    while ps3000a.ps3000aGetTimebase2(
        device.handle,
        current_timebase,
        SAMPLES,
        time_interval,
        time_units,
        OVERSAMPLING,
        max_samples) == 0 \
        or time_interval.value < wanted_time_interval:
        current_timebase += 1
        old_time_interval = time_interval.value
    if current_timebase.bit_length() > sizeof(c_int16) * 8:
        raise Exception('No appropriate timebase was identifiable')
    return current_timebase - 1, old_time_interval

with ps3000a.open_unit() as device:
    print('Device info: {}'.format(device.info))
    
    res = ps3000a.ps3000aSetChannel(
        device.handle, # handle of device (int16)
        picoEnum.PICO_CHANNEL['PICO_CHANNEL_A'], # channel ot set 
        True,  # activate channel 
        picoEnum.PICO_COUPLING['PICO_DC'], # DC or AC 
        ps3000a.PS3000A_RANGE['PS3000A_50MV'], # Voltage range 
        0 #analog offset
        )
    
    assert_pico_ok(res)
    timebase_a, interval = get_timebase(device, 25_000)