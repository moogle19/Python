# -*- coding: utf-8 -*-
"""
Created on Wed Nov 7 10:52:51 2012

@author: Kevin Seidel
@author Valentin Bruder
"""
from BaseRobotClient import *
from time import sleep

import networkx as nx


class TestClient(BaseRobotClient):
    global returnToNode, moveNextStep, sensor, stayNextStep, bomb, Graph, sensorStrings, nodecount, lastnode, nodebeforelast, steps, orientation, orientationset, crossroadlist, commandList, bombsDropped, pos
    #constants
    global CROSSROAD, DEADEND, TURN, HORI, VERT, UP, RIGHT, DOWN, LEFT
    
    def __init__(self):
        super(TestClient , self).__init__()
        #test teleporter  self.commands = [0,0,3, 3,0,3, 4]
        #test sensor_data self.commands = [3,4,0]   
        
        self.sensor = {'right': 0, 'left': 0, 'front':0, 'back': 0, 'battery': 100}     
        self.sensorStrings = ['front', 'right', 'back', 'left']
        self.index = 0
        self.stayNextStep = 0
        self.bomb = 0
        self.steps = 0
        self.bombsDropped = 0
        self.pos = {'x': 0, 'y': 0}
        self.lastnode = 0
        self.returnToNode = False
               
        self.moveNextStep = False
        self.orientationset = False
        
        self.staytime = 1
        self.nodecount = 1
        
        self.crossroadlist = []
        
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
        
        self.orientation = self.UP
        
        #List for moves to do
        self.commandList = []
        
        
    def bombDrop(self):
    
        print "DROPPING BOMB!"
        print self.steps
        print self.Graph.node[self.lastnode]
        commands = ['Right','Forward','DropBomb']
        if (self.steps < 2):
            availablePaths = self.Graph.node[self.lastnode]['openpaths']
            dirToGo = 0
            if(availablePaths[0] == self.orientation):
                dirToGo = availablePaths[1]
            else:
                dirToGo = availablePaths[0]
            if((self.orientation+1)&3 == dirToGo):
                commands.extend(['Left','Forward','Right','Right','Forward','Right','Forward','Sense'])
            else:
                commands.extend(['Right','Forward','Right','Right','Forward','Left','Forward','Sense'])
        #If enough Space available:
        else: 
            commands.extend(['Forward', 'Right', 'Right', 'Forward', 'Forward', 'Sense'])
        commands.reverse()
        self.commandList = commands
        
        return self.turnRight() 
    
    def dropBomb(self):
        self.bombsDropped += 1
        return Command.DropBomb
            
    def turnRight(self):
        self.orientation += 1
        self.sensor['battery'] -= 1
        self.orientation &= 3
        return Command.RightTurn
    
    def turnLeft(self):
        self.orientation -= 1
        self.sensor['battery'] -= 1
        self.orientation &= 3
        return Command.LeftTurn
    
    def moveForward(self):
        self.steps += 1
        self.sensor['battery'] -= 1
        if(self.orientation == 0):
            self.pos['x'] += 1
        elif(self.orientation == 1):
            self.pos['y'] += 1
        elif(self.orientation == 2):
            self.pos['x'] -= 1
        elif(self.orientation == 3):
            self.pos['y'] -= 1
        return Command.MoveForward
    
    def stay(self):
        self.sensor['battery'] += 1
        return Command.Stay
    
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
        if (self.stayNextStep == 1):
            if (self.staytime <= 50) :
                self.staytime += 1
                return Command.Stay           
            else :
                self.stayNextStep = 0
                self.staytime = 0
                self.moveNextStep = True
                return Command.Sense
        elif self.sensor['battery'] <= 10 :
            self.stayNextStep = 1
            return Command.Stay
        else :
            self.moveNextStep = True
            return Command.Sense
    
    
    def returnToLastCrossroad(self):
        if(not(self.commandList)) :
            self.commandList.append('Sense')
            self.commandList.append('Sense')
            self.commandList.extend(self.addMovesToCommandList(self.pathToMoves(self.getBackToLastCrossRoad())))
            self.returnToNode = True
        if self.sensor['battery'] < len(self.commandList) :
            self.commandList.append('Stay')
        ret = self.commandList.pop()
        if(not(self.commandList)) :
            self.returnToNode = False
            #self.moveNextStep = False
        print "lastnode:::::::: ", self.lastnode
        print "Crossroadlist: ", self.crossroadlist
        print "last crossroad::::::: ", self.crossroadlist[-1]
        print "commandList:::::: ", self.commandList
        #a = raw_input()

        return self.doCommand(ret)

    
    def addNode(self, sensor_data, compass):
        #TODO: add paths from nodes A to B and B to A
        #TODO: Avoid adding node twice
        pathcount = 0;
        openpath = [] #list for directions which are open
                
        #count valid/open paths
        for x in self.sensorStrings :
            if(sensor_data[x] == 0) :
                pathcount += 1
                
        # orientation is relative to the start position of the robot but will be consistent in our program
        #        UP
        #        0
        # LEFT 3 ^ 1 RIGHT
        #        2
        #       DOWN
        # because its a relative orientation, UP does not have to be the Up direction in the output, but that doesn't matter, it works!
        
        
        #assumption: the path we are coming from must be free
        # assumption: the path we are coming from must be free
        openpath.append((self.orientation + 2) & 3)
        
        
        '''get open paths from this node with relative orientation''' 
        #the only open path for a Deadend is the pass we are coming from
        if(pathcount <= 1) :
            if(not ((compass == 0.0) and (self.sensor['front'] != 0) and (self.sensor['right'] != 0) and (self.sensor['left'] != 0)) and self.bombsDropped < 3) :
                nodetype = self.DEADEND
            else :
                return self.DEADEND
            #set direction to go back
            
        #get open paths for crossroads        
        elif(pathcount >= 3) :
            nodetype = self.CROSSROAD
            # front is our current orientation
            if(self.sensor['front'] == 0) :
                openpath.append(self.orientation)
            if(self.sensor['left'] == 0) :
                openpath.append((self.orientation - 1) & 3)
            if(self.sensor['right'] == 0) :
                openpath.append((self.orientation + 1) & 3)
        # get open paths for turns
        elif(pathcount == 2) :
            nodetype = self.TURN
            if(self.sensor['left'] == 0 and self.sensor['right'] != 0 and self.sensor['front'] != 0) :
                openpath.append((self.orientation - 1) & 3)
            elif(self.sensor['right'] == 0 and self.sensor['left'] != 0 and self.sensor['front'] != 0) :
                openpath.append((self.orientation + 1) & 3)
            else :
                return None
             
        #if it is not a node return None, return is only there to stop the method. 
        else :
            return None     
        
        #if it is a node add it
        if(self.nodecount <= 1) :
            last = None
        else :
            last = self.lastnode
            
        fromPath = self.orientation - 2
        if(fromPath < 0) :
            fromPath += 4
        
        nodeAlreadyAdded = False
        currentNode = 0
        for n in self.Graph.nodes(data = True) :
            if(n[1]['position'] == self.pos) :
                nodeAlreadyAdded = True
                currentNode = n[0]
                #if((self.orientation + 2) % 4 in n[1]['openpaths'] and self.returnToNode) : 
                    #n[1]['openpaths'].remove((self.orientation + 2) % 4)
                    #if(len(n[1]['openpaths']) <= 1) :
                        #self.crossroadlist.pop()
        if (not(nodeAlreadyAdded)) :
            self.Graph.add_node(self.nodecount, type = nodetype, openpaths = openpath, fromNode = last, fromPath = fromPath, position = dict(self.pos))
            
        if(self.nodecount > 1) :
            #node not known -> add edge from previous node
            if(not(nodeAlreadyAdded)) :
                self.Graph.add_edge(self.lastnode, self.nodecount, length = self.steps, dir = self.orientation, visited = False)
            #node already visited -> new edge from another node (previous)
            else :
                edgeAlreadyAdded = False
                for e in self.Graph.edges() :
                    if (currentNode in e and self.lastnode in e) :
                        edgeAlreadyAdded = True 
                if (not(edgeAlreadyAdded)) :
                    self.Graph.add_edge(self.lastnode, currentNode, length = self.steps, dir = self.orientation, visited = False)
        
        
        if(not(nodeAlreadyAdded)) :
            if(nodetype == self.CROSSROAD) :
                self.crossroadlist.append(self.nodecount)  

            self.lastnode = self.nodecount
            self.nodecount += 1
        else :
            self.lastnode = currentNode
            if(nodetype == self.CROSSROAD) :
                if(not(self.crossroadlist)) :
                    self.crossroadlist.append(currentNode)
                elif(self.crossroadlist[-1] != currentNode) :
                    self.crossroadlist.append(currentNode)
        self.steps = 0
    
        return nodetype
    
    
    #returns nodelist with the shortest path to the targetnode     
    def getWayToNode(self, targetNode):
        return nx.dijkstra_path(self.Graph, self.lastnode, targetNode, 'length')
    
    #returns nodelist with the shortest path to the last crossroad
    def getBackToLastCrossRoad(self) :
        thenode = self.Graph.node[self.lastnode]['fromNode']
        while True :
            if(self.Graph.node[thenode]['type'] == self.CROSSROAD) :
                break
            tmp = self.Graph.node[thenode]['fromNode']
            thenode = tmp
        #list = self.getWayToNode(self.crossroadlist[-1])
        list = self.getWayToNode(thenode)
        print list 
        a = raw_input()
        self.lastnode = list[-1]
        return list
    
    #returns the moves to get back to given node
    #return format [[direction, length], [direction, length] ... ]
    def pathToMoves(self, p) :
        path = list(p)
        moveList = []
        currentNode = path.pop()
        while(len(path) > 0) :
            targetNode = path.pop()
            direction = self.Graph.node[targetNode]['fromPath']
            distance = self.Graph.edge[currentNode][targetNode]['length']
            moveList.append([direction, distance])
            currentNode = targetNode
        return moveList
    
    
    #TODO: method which follows path back to last crossroad and set edge to visited
    #TODO: Method to perform Commands
    '''
        returns list with commands in reverse order to handle it better with List.pop()
    '''
    def addMovesToCommandList(self, moveList):
        cList = []
        relativedirection = self.orientation
        while moveList :
            list = moveList.pop()
            direction = list[0]
            distance = list[1]
            if(direction != relativedirection) :
                #print "Direction: ", direction, " orientation: ", relativedirection
                if(direction == 3 and relativedirection == 0) :
                    cList.append('Left')
                    relativedirection = 3
                elif(direction == 0 and relativedirection == 3) :
                    cList.append('Right')
                    relativedirection = 0
                while(direction < relativedirection):
                    cList.append('Left')
                    relativedirection -= 1
                while(direction > relativedirection):
                    cList.append('Right')
                    relativedirection += 1
                for x in range(0, distance):
                    cList.append('Forward')
        cList.reverse()
        return cList
    
    def doCommand(self, command):
        print command        
        if(command == 'Left'):
            return self.turnLeft()
        elif(command == 'Right'):
            return self.turnRight()
        elif(command == 'Forward'):
            return self.moveForward()
        elif(command == 'DropBomb'):
            return self.dropBomb()
        elif(command == 'Stay'):
            return self.stay()
        elif(command == 'Sense'):
            return Command.Sense
    
    def getNextCommand(self, sensor_data, bumper, compass, teleported):
        
        if(len(self.commandList) > 10) :
            a = raw_input()
        
        currentType = None
        #print sensor_data, bumper
        #self.printSensorData(sensor_data, bumper, compass, teleported)
        #set own sensor data
        if sensor_data != None :
            self.setSensorData(sensor_data)
            currentType = self.addNode(sensor_data, compass)
            if(self.sensor['front'] == 192) :
                print "WON!!!"
                while(1) :
                    1
        

        #handle staying for battery recharging
        if (self.stayNextStep == 1) or (self.sensor['battery'] <= 10) or (self.moveNextStep == False) :
            return self.batteryHandler();
        
        elif self.returnToNode :
            return self.returnToLastCrossroad()
        
        elif self.commandList :
            return self.doCommand(self.commandList.pop())
        
        
        elif(currentType == self.CROSSROAD) :
            self.moveNextStep = False
            open = self.Graph.node[self.lastnode]['openpaths']
            fr = self.Graph.node[self.lastnode]['fromPath']
                        
            if(len(open) > 1) :
                if(compass <= 1.0 or compass == 7.0) :
                    if(self.orientation in open and self.orientation != fr) :
                        self.Graph.node[self.lastnode]['openpaths'].remove(self.orientation)
                        return self.moveForward()
                if(compass <= 7.0 and compass >= 5.0) :
                    if(((self.orientation - 1) & 3) in open and ((self.orientation - 1) & 3) != fr) :
                        #better!!!
                        #return self.commandList = ['Left', 'Forward']
                        return self.turnLeft()
                if(compass >= 1.0 and compass <= 3.0) :
                    if(((self.orientation + 1) & 3) in open and ((self.orientation + 1) & 3) != fr) :
                        return self.turnRight()
                if(self.orientation in open and self.orientation != fr) :
                    self.Graph.node[self.lastnode]['openpaths'].remove(self.orientation)
                    return self.moveForward()
            
            if(len(open) <= 1) :
                print "Crossroad List before: ", self.crossroadlist
                last = self.crossroadlist.pop()
                print "Crossroad List after: ", self.crossroadlist
                #a = raw_input()
                temp = self.returnToLastCrossroad()
                print temp
                #a = raw_input()
                return temp
                #return self.returnToLastCrossroad()
 

            if(((self.orientation - 1) & 3) in open and ((self.orientation - 1) & 3) != fr) :
                return self.turnLeft()
            if(((self.orientation + 1) & 3) in open and ((self.orientation + 1) & 3) != fr) :
                return self.turnRight()
            return self.turnRight()
            
        
        #DEADEND Handling
        elif(currentType == self.DEADEND) :
            if (compass == 0.0) and (self.sensor['front'] != 0) and (self.sensor['right'] != 0) and (self.sensor['left'] != 0) and (self.bombsDropped < 3):
                    return self.bombDrop()
            elif (self.crossroadlist) :
                return self.returnToLastCrossroad()
                #print "CommandList: ", self.commandList
                #print self.doCommand(self.commandList.pop())
                #if self.sensor['battery'] < len(self.commandList) :
                #    self.commandList.append('Stay')
                #return self.doCommand(self.commandList.pop())
            elif (self.sensor['front'] == 0) :
                self.moveNextStep = False
                return self.moveForward()
            else :
                self.moveNextStep = False
                return self.turnRight()
            
        #TURN Handling    
        elif(currentType == self.TURN) :
            self.moveNextStep = False
            dir = None
            for i in self.Graph.node[self.lastnode]['openpaths'] :
                if(i != (self.orientation + 2) & 3) :
                    dir = i
            if((self.orientation + 1) & 3 == dir) :
                return self.turnRight()
            elif((self.orientation - 1) & 3 == dir) :
                return self.turnLeft()
            elif(self.orientation == dir) :
                self.moveNextStep = False
                return self.moveForward()
            else :
                return self.turnRight()
        #STRAIGHT Handling   
        else :
            self.moveNextStep = False
            if(self.sensor['front'] == 0) :
                return self.moveForward()
            else :
                return self.turnRight()
        
        print compass