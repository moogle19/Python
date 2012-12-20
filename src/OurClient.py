# -*- coding: utf-8 -*-
"""
Created on Wed Nov 7 10:52:51 2012

@author: Kevin Seidel
@author Valentin Bruder
"""
from BaseRobotClient import *
import random
import networkx as nx


class TestClient(BaseRobotClient):
    global moveNextStep
    global sensor
    global stay
    global bomb
    global Graph
    global sensorStrings
    global nodecount;
    global lastnode;
    
    def __init__(self):
        super(TestClient , self).__init__()
        #test teleporter  self.commands = [0,0,3, 3,0,3, 4]
        #test sensor_data self.commands = [3,4,0]   
        self.sensor = {'right': 0, 'left': 0, 'front':0, 'back': 0, 'battery': 100}     
        self.sensorStrings = ['right', 'left', 'front', 'back']
        self.index = 0
        self.moveNextStep = False
        self.stay = 0
        self.staytime = 1
        self.bomb = 0
        self.Graph = nx.Graph();
        self.nodecount = 0;
        
    def printSensorData(self, sensor_data, bumper, compass, teleported):
        print "compass: ", compass
        print "bomb stat: ", self.bomb
        if teleported:
            print "ups I was teleported"
        if sensor_data != None:
            print sensor_data
            
        print "Graph: ", self.Graph.nodes()
    
    def setSensorData(self, sensor_data):
        self.sensor['left'] = sensor_data['left']
        self.sensor['right'] = sensor_data['right']
        self.sensor['front'] = sensor_data['front']
        self.sensor['back'] = sensor_data['back']
        self.sensor['battery'] = sensor_data['battery']
        
    def batteryHandler(self):
        if (self.stay == 1):
            if (self.staytime <= 50) :
                self.staytime += 1
                return Command.Stay           
            else :
                self.stay = 0
                self.staytime = 0
                self.moveNextStep = True
                return Command.Sense
        elif self.sensor['battery'] <= 10 :
            self.stay = 1
            return Command.Stay
        else :
            self.moveNextStep = True
            return Command.Sense
           
        
    def getNextCommand(self, sensor_data, bumper, compass, teleported):
        #print sensor_data, bumper
        self.printSensorData(sensor_data, bumper, compass, teleported)
        if sensor_data != None :
            sensorcount = 0;
            self.setSensorData(sensor_data)
            for x in self.sensorStrings :
                if(sensor_data[x] == 0) :
                    sensorcount += 1
            if(sensorcount >= 3) :
                self.Graph.add_node(self.nodecount)
                if(self.nodecount != 0) :
                    print "NODES", self.nodecount, self.lastnode
                    self.Graph.add_edge(lastnode, nodecount)
                self.lastnode = self.nodecount
                self.nodecount += 1;
                    
            
        #battery handling
        #self.moveNextStep = self.count + 1
        
        
        if (self.stay == 1) or (self.sensor['battery'] <= 10) or (self.moveNextStep == False) :
            return self.batteryHandler();
        
        # bomb handling
        elif self.bomb == 1 :
            self.bomb += 1
            return Command.RightTurn
        elif self.bomb == 2 :
            self.bomb += 1
            self.moveNextStep = False
            return Command.MoveForward
        elif self.bomb == 3 :
            self.bomb += 1
            return Command.DropBomb
        elif self.bomb == 4 :
            self.bomb += 1
            return Command.MoveForward
        elif self.bomb == 5 :
            self.bomb += 1
            return Command.RightTurn
        elif self.bomb == 6 :
            self.bomb += 1
            return Command.RightTurn

        elif self.bomb == 7 :
            self.bomb = 0
            self.moveNextStep = False
            return Command.MoveForward
        
        #compass handling
        #
        # 7 0 1
        # 6 x 2
        # 5 4 3
        #
        elif (compass == 0.0) or (compass == 1.0) or (compass == 7.0) :
            if self.sensor['front'] == 0 :
                self.moveNextStep = False
                return Command.MoveForward
            elif (compass == 0.0) and (self.sensor['front'] != 0) and (self.sensor['right'] != 0) and (self.sensor['left'] != 0) :
                self.bomb = 1
                self.moveNextStep = False
                return Command.RightTurn
            elif (compass == 1.0) and (self.sensor['right'] == 0) :
                self.moveNextStep = False
                return Command.RightTurn
            elif (compass == 7.0) and (self.sensor['left'] == 0) :
                self.moveNextStep = False
                return Command.LeftTurn
            elif (compass == 2.0) and (self.sensor['right'] == 0) :
                self.moveNextStep = False
                return Command.RightTurn
            else :
                return Command.RightTurn
            
        elif ((compass == 2.0) or (compass == 6.0)) and (self.sensor['front'] == 0) :
                self.moveNextStep = False
                return Command.MoveForward
            
        elif (compass == 6.0) or (compass == 5.0) :
            self.moveNextStep = False
            return Command.LeftTurn
        elif (self.sensor['front'] == 0) :
            self.moveNextStep = False
            return Command.MoveForward
        else :
            self.moveNextStep = False
            return Command.RightTurn
        
        
        print compass
