# -*- coding: utf-8 -*-
"""
Created on Wednesday May 29 2024

@author: Baptiste Bordet
"""

from PyQt5.QtCore import QProcess, QProcessEnvironment
import numpy as np

#TODO here add all the meyhods for teh thread to ahndle as well as variables which will be back propagated 

class process_Acquisition():
   def setup(self):
       env=QProcessEnvironment.systemEnvironment()
       self.p = QProcess()
       self.p.setProcessEnvironment(env)
       self.p.start("python", ["utils/test.py","fsqdjf"])
       self.p.readyReadStandardOutput.connect(self.handle_stdout)
       self.p.readyReadStandardError.connect(self.handle_stderr)
       self.p.stateChanged.connect(self.handle_state)
       self.p.finished.connect(self.process_finished)
   
def handle_stderr(self):
    data = self.p.readAllStandardError()
    stderr = bytes(data).decode("utf8")
    print(stderr)

def handle_stdout(self):
    data = self.p.readAllStandardOutput()
    data=bytes(data)
    array=np.frombuffer(data,dtype=np.int8)
    return array

def handle_state(self, state):
    states = {
        QProcess.NotRunning: 'Not running',
        QProcess.Starting: 'Starting',
        QProcess.Running: 'Running'}
    state_name = states[state]
    print(state_name)

def process_finished(self):
    print(self.p.ExitStatus())
    print("finished")
    self.p = None