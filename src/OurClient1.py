# -*- coding: utf-8 -*-
"""
Created on Wed Nov 7 10:52:51 2012

@author: Kevin Seidel
@author Valentin Bruder
"""
from BaseRobotClient import *
import networkx as nx


class TestClient(BaseRobotClient):
    global moveNextStep, sensor, stay, bomb, Graph, sensorStrings, nodecount, lastnode, steps, orientation, orientationset, position, returnToLastNode
    #constants
    global CROSSROAD, DEADEND, TURN, HORI, VERT, UP, RIGHT, DOWN, LEFT
    
    def __init__(self):
        super(TestClient , self).__init__()
        #test teleporter  self.commands = [0,0,3, 3,0,3, 4]
        #test sensor_data self.commands = [3,4,0]   
        
        self.sensor = {'right': 0, 'left': 0, 'front':0, 'back': 0, 'battery': 100}     
        self.sensorStrings = ['front', 'right', 'back', 'left']
        self.index = 0
        self.stay = 0
        self.bomb = 0
        self.steps = 0
        self.position = {'x': 0, 'y': 0}
        self.returnToLastNode = False
        
        self.moveNextStep = False
        self.orientationset = False
        
        self.staytime = 1
        self.nodecount = 1
        
        self.Graph = nx.Graph();
        
        #CONSTANTS
        
        #NODE IDENTIFIER
        self.CROSSROAD = 0
        self.DEADEND = 1
        self.TURN = 2
        
        #EDGE DIRECTION IDENTIFIER 
        self.VERT = 0
        self.HORI = 1
        
        #ORIENTATION IDENTIFIER
        self.UP = 0
        self.RIGHT = 1
        self.DOWN = 2
        self.LEFT = 3
        
        
    def turnRight(self):
        self.orientation += 1
        self.sensor['battery'] -= 1
        if(self.orientation > 3) :
            self.orientation = 0
        return Command.RightTurn
    
    def turnLeft(self):
        self.orientation -= 1
        self.sensor['battery'] -= 1
        if(self.orientation < 0) :
            self.orientation = 3
        return Command.LeftTurn
    
    def moveForward(self):
        self.steps += 1
        self.sensor['battery'] -= 1
        if(self.orientation == self.UP) :
            self.position['y'] += 1
        elif(self.orientation == self.DOWN) :
            self.position['y'] -= 1
        elif(self.orientation == self.RIGHT) :
            self.position['x'] += 1
        elif(self.orientation == self.LEFT) :
            self.position['x'] -= 1
        return Command.MoveForward
    
    def printSensorData(self, sensor_data, bumper, compass, teleported):
        print "compass: ", compass
        print "bomb stat: ", self.bomb
        if teleported:
            print "ups I was teleported"
        if sensor_data != None:
            print sensor_data
            
        print "Graph: ", self.Graph.nodes(data = True)
        print "Edges: ", self.Graph.edges(data = True)
    
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
    
    def addNode(self, sensor_data, compass):
        pathcount = 0;
                
        left = -1
        right = -1
        up = -1
        down = -1
                
        #count valid paths
        for x in self.sensorStrings :
            if(sensor_data[x] == 0) :
                pathcount += 1
        print "PATHCOUNT: ", pathcount
        #set lastnode    
        if(self.nodecount > 1) :        
            if(self.orientation == 0) :
                down = self.lastnode
            elif(self.orientation == 1) :
                left = self.lastnode
            elif(self.orientation == 2) :
                up = self.lastnode
            elif(self.orientation == 3) :
                right = self.lastnode  
        
        '''get open paths from this node with relative orientation''' 
        #get paths for deadends                  
        if(pathcount <= 1 and not ((compass == 0.0) and (self.sensor['front'] != 0) and (self.sensor['right'] != 0) and (self.sensor['left'] != 0))) :
            nodetype = self.DEADEND
            #set direction to go back
            
        #get open paths for crossroads        
        elif(pathcount >= 3) :
            nodetype = self.CROSSROAD
            if(self.orientation == 0) :
                if(self.sensor['front'] == 0) :
                    up = 0
                if(self.sensor['left'] == 0) :
                    left = 0
                if(self.sensor['right'] == 0) :
                    right = 0
            elif(self.orientation == 1) :
                if(self.sensor['front'] == 0) :
                    right = 0
                if(self.sensor['left'] == 0) :
                    up = 0
                if(self.sensor['right'] == 0) :
                    down = 0
            elif(self.orientation == 2) :
                if(self.sensor['front'] == 0) :
                    down = 0
                if(self.sensor['left'] == 0) :
                    right = 0
                if(self.sensor['right'] == 0) :
                    left = 0
            elif(self.orientation == 3) :
                if(self.sensor['front'] == 0) :
                    left = 0
                if(self.sensor['left'] == 0) :
                    down = 0
                if(self.sensor['right'] == 0) :
                    up = 0
        
        #get open paths for turns
        elif(pathcount == 2) :
            nodetype = self.TURN
            if(self.orientation == 0) :
                if(self.sensor['left'] == 0) :
                    left = 0
                elif(self.sensor['right'] == 0) :
                    right = 0
                else :
                    return None
            elif(self.orientation == 1) :
                if(self.sensor['left'] == 0) :
                    up = 0
                elif(self.sensor['right'] == 0) :
                    down = 0
                else :
                    return None
            elif(self.orientation == 2) :
                if(self.sensor['left'] == 0) :
                    right = 0
                elif(self.sensor['right'] == 0) :
                    left = 0
                else :
                   return None
            elif(self.orientation == 3) :
                if(self.sensor['left'] == 0) :
                    down = 0
                elif(self.sensor['right'] == 0) :
                    up = 0
                else :
                    return None         
            else :
               return None 
        #if it is not a node return None
        else :
            return None     
        
        if(self.nodecount <= 1) :
            last = 0
        else :
            last = self.lastnode
            
        openpaths = {'up': up, 'down': down, 'left': left, 'right': right}
        self.Graph.add_node(self.nodecount, type = nodetype, path = openpaths, fromNode = last)
            
        if(self.nodecount > 1) :
            self.Graph.add_edge(self.lastnode, self.nodecount, weight = self.steps, dir = self.orientation, visited = False)
        self.lastnode = self.nodecount
        self.nodecount += 1;
        self.steps = 0
        return 1;
        
       
       
       
    def getNextCommand(self, sensor_data, bumper, compass, teleported):
        #print sensor_data, bumper
        if(not self.orientationset) :
            if(compass <= 1) :
                self.orientation = self.UP
            elif(compass <= 3) :
                self.orientation = self.RIGHT
            elif(compass <= 5) :
                self.orientation = self.DOWN
            elif(compass <= 7) :
                self.orientation = self.LEFT
            self.orientationset = True
        self.printSensorData(sensor_data, bumper, compass, teleported)
        if sensor_data != None :
            self.setSensorData(sensor_data)
            if(self.addNode(sensor_data, compass)) :
                print "Good"
        
        if (self.stay == 1) or (self.sensor['battery'] <= 10) or (self.moveNextStep == False) :
            return self.batteryHandler();
        
        # bomb handling
        elif self.bomb == 1 :
            self.bomb += 1
            return self.turnRight()
        elif self.bomb == 2 :
            self.bomb += 1
            self.steps -= 1 #decrease steps because you go backwards
            #self.moveNextStep = False
            return self.moveForward()
        elif self.bomb == 3 :
            self.bomb += 1
            return Command.DropBomb
        elif self.bomb == 4 :
            self.bomb += 1
            self.steps -= 1 #decrease steps because you go backwards
            return self.moveForward()
        elif self.bomb == 5 :
            self.bomb += 1
            return self.turnRight()
        elif self.bomb == 6 :
            self.bomb += 1
            return self.turnRight()

        elif self.bomb == 7 :
            self.bomb = 0
            self.moveNextStep = False
            return self.moveForward()
        
        #compass handling
        #
        # 7 0 1
        # 6 x 2
        # 5 4 3
        #
        elif (compass == 0.0) or (compass == 1.0) or (compass == 7.0) :
            if self.sensor['front'] == 0 :
                self.moveNextStep = False
                return self.moveForward()
            elif (compass == 0.0) and (self.sensor['front'] != 0) and (self.sensor['right'] != 0) and (self.sensor['left'] != 0) :
                self.bomb = 1
                print "DROPING BOMB!"
                return self.turnRight()
            #if deadend and goal is not in front return to last node
            elif (not(compass == 0.0) and self.sensor['front'] != 0 and self.sensor['right'] != 0 and self.sensor['left'] != 0 ) :
                self.returnToLastNode = True
                return self.turnRight()
            elif (compass == 1.0 or compass == 2.0) and (self.sensor['right'] == 0) :
                self.moveNextStep = False
                return self.turnRight()
            elif (compass == 7.0) and (self.sensor['left'] == 0) :
                self.moveNextStep = False
                return self.turnLeft()
            #elif (compass == 2.0) and (self.sensor['right'] == 0) :
            #   self.moveNextStep = False
            #  return self.turnRight()
            else :
                return self.turnRight()
            
        elif ((compass == 2.0) or (compass == 6.0)) and (self.sensor['front'] == 0) :
                self.moveNextStep = False
                return self.moveForward()
            
        elif (compass == 6.0) or (compass == 5.0) :
            self.moveNextStep = False
            return self.turnLeft()
        elif (self.sensor['front'] == 0) :
            self.moveNextStep = False
            return self.moveForward()
        else :
            self.moveNextStep = False
            return self.turnRight()
        
        
        print compass