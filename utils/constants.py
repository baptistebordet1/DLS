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
    TURNTABLE_ANGLE_MAX_DEC=TURNTABLE_ANGLE_MIN_DEC+REDUCTION_RATIO*180 # calculated angle from the 0 position thanks to reduction ration 