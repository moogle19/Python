# -*- coding: utf-8 -*-
"""
Created on Wed Nov 7 10:52:51 2012

@author: Kevin Seidel
"""
from BaseRobotClient import *
import random


class TestClient(BaseRobotClient):
    global count
    global sensor
    global stay
    
    def __init__(self):
        super(TestClient , self).__init__()
        #test teleporter  self.commands = [0,0,3, 3,0,3, 4]
        #test sensor_data self.commands = [3,4,0]   
        self.sensor = {'right': 0, 'left': 0, 'front':0, 'back': 0, 'battery': 100}     
        self.index = 0
        self.count = 0
        self.stay = 0
        self.staytime = 1

    def getNextCommand(self, sensor_data, bumper, compass, teleported):
        #print sensor_data, bumper
        print "compass: ",compass
        if teleported:
            print "ups I was teleported"
        if sensor_data != None:
            print sensor_data
            self.sensor['left'] = sensor_data['left']
            self.sensor['right'] = sensor_data['right']
            self.sensor['front'] = sensor_data['front']
            self.sensor['back'] = sensor_data['back']
            self.sensor['battery'] = sensor_data['battery']
        """
        cmd = self.commands[self.index]
        self.index += 1
        if self.index == len(self.commands):
            self.index = 0
        
        return cmd
        """     
        #return random.randrange(0, 7, 1)
        self.count = self.count + 1
        #print sensor.keys();
        if (self.stay == 1) and (self.staytime <= 50) :
            self.staytime += 1
            return Command.Stay
            
        elif (self.stay == 1) and (self.staytime > 50) :
            self.stay = 0
            self.staytime = 0
            return Command.Sense
        elif self.sensor['battery'] <= 10 :
            self.stay = 1
            return Command.Stay
        elif self.count-2==0 :
            self.count = 0;
            return Command.Sense
        elif self.sensor['front'] == 0 :
            return Command.MoveForward
        else:
            return Command.LeftTurn
        print compass
