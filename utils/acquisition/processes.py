# -*- coding: utf-8 -*-
"""
Created on Tuesday May 28 2024

@author: Baptiste Bordet 
"""
import sys
import numpy as np 

a=np.arange(0,20,1,dtype=np.int8)
b=a.tobytes()
sys.stdout.buffer.write(b)
sys.stdout.flush()

