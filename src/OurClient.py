# -*- coding: utf-8 -*-
"""
Created on Wed Nov 7 10:52:51 2012

@author: Kevin Seidel
"""
from BaseRobotClient import *
import random

class TestClient(BaseRobotClient):
    global count
    def __init__(self):
        super(TestClient , self).__init__()
        #test teleporter  self.commands = [0,0,3, 3,0,3, 4]
        #test sensor_data self.commands = [3,4,0]        
        self.index = 0
        self.count = 0

    def getNextCommand(self, sensor_data, bumper, compass, teleported):
        #print sensor_data, bumper
        print "compass: ",compass
        if teleported:
            print "ups I was teleported"
        if sensor_data != None:
            print sensor_data
        """
        cmd = self.commands[self.index]
        self.index += 1
        if self.index == len(self.commands):
            self.index = 0
        
        return cmd
        """     
        #return random.randrange(0, 7, 1)
        self.count = self.count + 1
        if self.count-5==0 :
            self.count = 0;
            return 4
        else:
            return 1
