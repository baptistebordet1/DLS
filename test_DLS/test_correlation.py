# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 15:55:49 2023

@author: Raphael Girault
"""

# test auto correlation sur 31 Mo 

"""
Conclusion de ca convoltion sur une array flipped est le plus rapide (4.5 s pour 31 M de points)
"""
import time
import numpy as np 
from scipy.signal import fftconvolve, correlate, correlation_lags
import matplotlib.pyplot as plt
from timeit import timeit
import pandas as pd
import numpy as np

rng = np.random.default_rng()
dataset1=np.random.rand(31000)
dataset2=np.random.rand(31000)
dataset2= dataset2[::-1]
start = time.time()

corrfft=fftconvolve(dataset1, dataset2,mode="full")
stop = time.time()
print("excecution time is ", stop-start)


