#
# Copyright (C) 2018 Pico Technology Ltd. See LICENSE file for terms.
#
# PS3000A BLOCK MODE EXAMPLE
# This example opens a 3000a driver device, sets up one channels and a trigger then collects a block of data.
# This data is then plotted as mV against time in ns.

import ctypes
import sys 
sys.path.append("test_DLS/picosdk_python_wrappers_master")
from picosdk.ps3000a import ps3000a as ps
import numpy as np
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok
import time 

class pico_block_aquisition():
    def setup(self):
        # Create chandle and status ready for use
        self.status = {}
        self.chandle = ctypes.c_int16()
        
        # Opens the device/s
        self.status["openunit"] = ps.ps3000aOpenUnit(ctypes.byref(self.chandle), None)
        
        try:
            assert_pico_ok(self.status["openunit"])
        except:
        
            # powerstate becomes the status number of openunit
            self.powerstate = self.status["openunit"]
        
            # If powerstate is the same as 282 then it will run this if statement
            if self.powerstate == 282:
                # Changes the power input to "PICO_POWER_SUPPLY_NOT_CONNECTED"
                self.status["ChangePowerSource"] = self.ps.ps3000aChangePowerSource(self.chandle, 282)
                # If the powerstate is the same as 286 then it will run this if statement
            elif self.powerstate == 286:
                # Changes the power input to "PICO_USB3_0_DEVICE_NON_USB3_0_PORT"
                self.status["ChangePowerSource"] = self.ps.ps3000aChangePowerSource(self.chandle, 286)
            else:
                raise
        
            assert_pico_ok(self.status["ChangePowerSource"])
        
        # Set up channel A
        # handle = chandle
        # channel = PS3000A_CHANNEL_A = 0
        # enabled = 1
        # coupling type = PS3000A_DC = 1
        # range = PS3000A_10V = 8
        # analogue offset = 0 V
        self.chARange = 8
        self.status["setChA"] = ps.ps3000aSetChannel(self.chandle, 0, 1, 1, self.chARange, 0)
        assert_pico_ok(self.status["setChA"])
        
        # Sets up single trigger
        # Handle = Chandle
        # Source = ps3000A_channel_B = 0
        # Enable = 0
        # Threshold = 1024 ADC counts
        # Direction = ps3000A_Falling = 3
        # Delay = 0
        # autoTrigger_ms = 1000
        self.status["trigger"] =ps.ps3000aSetSimpleTrigger(self.chandle, 1, 0, 1024, 3, 0, 1000)
        assert_pico_ok(self.status["trigger"])
        
        # Setting the number of sample to be collected
        self.preTriggerSamples = 0
        self.postTriggerSamples = 10
        self.maxsamples =self.preTriggerSamples + self.postTriggerSamples
        
        # Gets timebase innfomation
        # WARNING: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.  
        # To access these Timebases, set any unused analogue channels to off.
        # Handle = chandle
        # Timebase = 2 = timebase
        # Nosample = maxsamples
        # TimeIntervalNanoseconds = ctypes.byref(timeIntervalns)
        # MaxSamples = ctypes.byref(returnedMaxSamples)
        # Segement index = 0
        self.timebase = 2**24
        self.timeIntervalns = ctypes.c_float()
        self.returnedMaxSamples = ctypes.c_int16()
        self.status["GetTimebase"] = ps.ps3000aGetTimebase2(self.chandle, self.timebase, self.maxsamples, ctypes.byref(self.timeIntervalns), 1, ctypes.byref(self.returnedMaxSamples), 0)
        assert_pico_ok(self.status["GetTimebase"])
        
        # Creates a overlow location for data
        self.overflow = ctypes.c_int16()
        # Creates converted types maxsamples
        self.cmaxSamples = ctypes.c_int32(self.maxsamples)
        
        # Starts the block capture
        # Handle = chandle
        # Number of prTriggerSamples
        # Number of postTriggerSamples
        # Timebase = 2 = 4ns (see Programmer's guide for more information on timebases)
        # time indisposed ms = None (This is not needed within the example)
        # Segment index = 0
        # LpRead = None
        # pParameter = None
        self.status["runblock"] = ps.ps3000aRunBlock(self.chandle, self.preTriggerSamples, self.postTriggerSamples, self.timebase, 1, None, 0, None, None)
        assert_pico_ok(self.status["runblock"])
        
        # Create buffers ready for assigning pointers for data collection
        self.bufferAMax = (ctypes.c_int16 * self.maxsamples)()
        self.bufferAMin = (ctypes.c_int16 * self.maxsamples)() # used for downsampling which isn't in the scope of this example
        
        # Setting the data buffer location for data collection from channel A
        # Handle = Chandle
        # source = ps3000A_channel_A = 0
        # Buffer max = ctypes.byref(bufferAMax)
        # Buffer min = ctypes.byref(bufferAMin)
        # Buffer length = maxsamples
        # Segment index = 0
        # Ratio mode = ps3000A_Ratio_Mode_None = 0
        self.status["SetDataBuffers"] = ps.ps3000aSetDataBuffers(self.chandle, 0, ctypes.byref(self.bufferAMax), ctypes.byref(self.bufferAMin), self.maxsamples, 0, 0)
        assert_pico_ok(self.status["SetDataBuffers"])
        
        # Creates a overlow location for data
        self.overflow = (ctypes.c_int16 * 10)()
        # Creates converted types maxsamples
        self.cmaxSamples = ctypes.c_int32(self.maxsamples)
        # Checks data collection to finish the capture
        self.ready = ctypes.c_int16(0)
        self.check = ctypes.c_int16(0)
        
      
        
        # Handle = chandle
        # start index = 0
        # noOfSamples = ctypes.byref(cmaxSamples)
        # DownSampleRatio = 0
        # DownSampleRatioMode = 0
        # SegmentIndex = 0
        # Overflow = ctypes.byref(overflow)
        while self.ready.value == self.check.value:
            self.status["isReady"] = ps.ps3000aIsReady(self.chandle, ctypes.byref(self.ready))
            
    def acquire(self):
        
        
        self.status["GetValues"] = ps.ps3000aGetValues(self.chandle, 0, ctypes.byref(self.cmaxSamples), 0, 0, 0, ctypes.byref(self.overflow))
        assert_pico_ok(self.status["GetValues"])
        
        # Finds the max ADC count
        # Handle = chandle
        # Value = ctype.byref(maxADC)
        self.maxADC = ctypes.c_int16()
        self.status["maximumValue"] =ps.ps3000aMaximumValue(self.chandle, ctypes.byref(self.maxADC))
        assert_pico_ok(self.status["maximumValue"])
        self.time = np.linspace(0, (self.cmaxSamples.value - 1) * self.timeIntervalns.value, self.cmaxSamples.value)
        
        # Converts ADC from channel A to mV
        self.adc2mVChAMax =  adc2mV(self.bufferAMax, self.chARange, self.maxADC)
        return np.mean(self.adc2mVChAMax)
    def close_comm(self):
        


        # Stops the scope
        # Handle = chandle
        self.status["stop"] = ps.ps3000aStop(self.chandle)
        assert_pico_ok(self.status["stop"])
        
        # Closes the unit
        # Handle = chandle
        self.status["close"] = ps.ps3000aCloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])



# clsa=pico_block_aquisition()
# clsa.setup()
# toc=time.time()
# for i in range(0, 10):
#     tic=time.time()
#     print(tic-toc)
#     clsa.acquire()
#     tac=time.time()
    
# #TODO test this code 
# clsa.close_comm()
        

