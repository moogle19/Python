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
    global crossroadcount, returnToNode, moveNextStep, sensor, stayNextStep, bomb, Graph, sensorStrings, nodecount, lastnode, nodebeforelast, steps, orientation, commandList, bombsDropped, pos
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
        self.crossroadcount = 0
               
        self.moveNextStep = False
        
        self.staytime = 1
        self.nodecount = 1
                
        self.Graph = nx.Graph();
        
        #CONSTANTS
        
        #NODE IDENTIFIER
        self.CROSSROAD = 0
        self.DEADEND = 1
        self.TURN = 2
        self.PORTAL = 3
        self.STONE = 4
        self.ENERGY = 5
        
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
        commands = ['Right','Forward','DropBomb']
        if (self.steps < 2):
            availablePaths = self.Graph.node[self.lastnode]['openpaths']
            dirToGo = 0
            #if(not(((self.orientation +2) & 3) in availablePaths)) :
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
    
    def energyHandler(self):
        staytime = int((100 - self.sensor['battery']) / 30 )
        for x in range(0,staytime):
            self.commandList.append('Stay')
        self.commandList.append('Sense')
        return self.moveForward()
            
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
                return self.stay()           
            else :
                self.stayNextStep = 0
                self.staytime = 0
                self.moveNextStep = True
                return Command.Sense
        elif self.sensor['battery'] <= 10 :
            self.stayNextStep = 1
            return self.stay()
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
        return self.doCommand(ret)

    
    def addNode(self, sensor_data, compass):
        pathcount = 0;
        openpath = [] #list for directions which are open
                
        #count valid/open paths
        if(self.isFreeFront()) :
            pathcount += 1
        if(self.isFreeLeft()) :
            pathcount += 1
        if(self.isFreeRight()) :
            pathcount += 1
        if(self.isFreeBack()) :
            pathcount += 1
            
                
        # orientation is relative to the start position of the robot but will be consistent in our program
        #        UP
        #        0
        # LEFT 3 ^ 1 RIGHT
        #        2
        #       DOWN
        # because its a relative orientation, UP does not have to be the Up direction in the output, but that doesn't matter, it works!
        
        
        #assumption: the path we are coming from must be free
        openpath.append((self.orientation + 2) & 3)
        
        #get open paths from this node with relative orientation
        #the only open path for a Deadend is the pass we are coming from
        if(pathcount <= 1) :
            if((compass == 0.0) and (not(self.isFreeFront()) and not(self.isFreeRight()) and not(self.isFreeLeft())) and (self.bombsDropped < 3) and not(self.isPortal())) :
                return self.DEADEND
            else :
                nodetype = self.DEADEND
            #set direction to go back
            
        #get open paths for crossroads        
        elif(pathcount >= 3) :
            nodetype = self.CROSSROAD
            # front is our current orientation
            if(self.isFreeFront()) :
                openpath.append(self.orientation)
            if(self.isFreeLeft()) :
                openpath.append((self.orientation - 1) & 3)
            if(self.isFreeRight()) :
                openpath.append((self.orientation + 1) & 3)
        #get open paths for turns
        elif(pathcount == 2) :
            nodetype = self.TURN
            if(self.isFreeLeft() and not(self.isFreeRight()) and not(self.isFreeFront())) :
                openpath.append((self.orientation - 1) & 3)
            elif(self.isFreeRight() and not(self.isFreeLeft()) and not(self.isFreeFront())) :
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
            
        fromPath = (self.orientation + 2) & 3
        #if(fromPath < 0) :
        #    fromPath += 4
        
        nodeAlreadyAdded = False
        currentNode = 0
        for n in self.Graph.nodes(data = True) :
            if(n[1]['position'] == self.pos) :
                nodeAlreadyAdded = True
                currentNode = n[0]
                #if((self.orientation + 2) % 4 in n[1]['openpaths'] and self.returnToNode) : 
                    #n[1]['openpaths'].remove((self.orientation + 2) % 4)
                    #if(len(n[1]['openpaths']) <= 1) :
        if (not(nodeAlreadyAdded)) :
            self.crossroadcount += 1
            self.Graph.add_node(self.nodecount, type = nodetype, openpaths = openpath, visitedpaths = list(), fromNode = last, fromPath = fromPath, position = dict(self.pos))
            
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
            self.lastnode = self.nodecount
            self.nodecount += 1
        else :
            self.lastnode = currentNode
            if(nodetype == self.CROSSROAD) :
                if(openpath.sort() != self.Graph.node[currentNode]['openpaths'].sort()) :
                    self.Graph.node[currentNode]['openpaths'] = openpath
        self.steps = 0
            
        return nodetype
    
    
    #returns nodelist with the shortest path to the targetnode     
    def getWayToNode(self, targetNode):
        return nx.dijkstra_path(self.Graph, self.lastnode, targetNode, 'length')
    
    #returns nodelist with the shortest path to the last crossroad
    def getBackToLastCrossRoad(self) :
        thenode = self.Graph.node[self.lastnode]['fromNode']
        while True :
            if(self.Graph.number_of_nodes() <= 1) :
                print "YOU ARE STUCK! Only 0 or 1 nodes in nodelist. You can not got back to last Crossroad because there is no last Crossroad. Blow the shit up or die!"
                while 1 :
                    1
            if(self.Graph.node[thenode]['fromNode'] == None) :
                print "YOU ARE STUCK! You ran and ran and ran....and there is no way out of this maze."
                while 1 :
                    1
            if(self.Graph.node[thenode]['type'] == self.CROSSROAD) :
                break
            tmp = self.Graph.node[thenode]['fromNode']
            thenode = tmp
        list = self.getWayToNode(thenode)
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
        currentType = None
        #print sensor_data, bumper
        #self.printSensorData(sensor_data, bumper, compass, teleported)
        #set own sensor data
        if sensor_data != None :
            self.setSensorData(sensor_data)
            currentType = self.addNode(sensor_data, compass)
            if(self.sensor['front'] == 192) :
                return self.moveForward()

        #handle staying for battery recharging
        if (self.stayNextStep == 1) or (self.sensor['battery'] <= 15 and (not(self.isFreeFront()) and not(self.isFreeBack()))) or (self.moveNextStep == False)  :
            return self.batteryHandler();
        
        if self.returnToNode :
            if(bumper) :
                self.commandList.append('Forward')
                for _ in range(10) :
                    self.commandList.append('Stay')
                    
            return self.returnToLastCrossroad()

        if self.commandList :
            if(bumper) :
                print "BUMPER"
                for _ in range(10) :
                    self.commandList.append('Stay')
            return self.doCommand(self.commandList.pop())

            
        if(currentType == self.CROSSROAD) :
            self.moveNextStep = False
            open = self.Graph.node[self.lastnode]['openpaths']
            visited = self.Graph.node[self.lastnode]['visitedpaths']
            fr = self.Graph.node[self.lastnode]['fromPath']
            
                        
            if(len(open) > len(visited) + 1) :
                if(compass <= 1.0 or compass == 7.0) :
                    if(self.orientation in open and not(self.orientation in visited) and self.orientation != fr) :
                        self.Graph.node[self.lastnode]['visitedpaths'].append(self.orientation)
                        return self.moveForward()
                if(compass <= 7.0 and compass >= 5.0) :
                    if(((self.orientation - 1) & 3) in open and not(((self.orientation - 1) & 3) in visited) and ((self.orientation - 1) & 3) != fr) :
                        #better!!!
                        #return self.commandList = ['Left', 'Forward']
                        return self.turnLeft()
                if(compass >= 1.0 and compass <= 3.0) :
                    if(((self.orientation + 1) & 3) in open and not(((self.orientation + 1) & 3) in visited) and ((self.orientation + 1) & 3) != fr) :
                        return self.turnRight()
                if(self.orientation in open and not(self.orientation in visited) and self.orientation != fr) :
                    #self.Graph.node[self.lastnode]['openpaths'].remove(self.orientation)
                    self.Graph.node[self.lastnode]['visitedpaths'].append(self.orientation)
                    return self.moveForward()
            
            if(len(open) <= len(visited) + 1) :
                self.crossroadcount -= 1
                return self.returnToLastCrossroad()
 

            if(((self.orientation - 1) & 3) in open and not(((self.orientation - 1) & 3) in visited) and ((self.orientation - 1) & 3) != fr) :
                return self.turnLeft()
            if(((self.orientation + 1) & 3) in open and not(((self.orientation + 1) & 3) in visited) and ((self.orientation + 1) & 3) != fr) :
                return self.turnRight()
            return self.turnRight()
            
        
        #DEADEND Handling
        elif(currentType == self.DEADEND) :
            if (compass == 0.0) and (not(self.isFreeFront()) and not(self.isFreeRight()) and not(self.isFreeLeft())) and (self.bombsDropped < 3) and not(self.isPortal()) :
                    return self.bombDrop()
            elif (self.crossroadcount) :
                return self.returnToLastCrossroad()
                #print "CommandList: ", self.commandList
                #print self.doCommand(self.commandList.pop())
                #if self.sensor['battery'] < len(self.commandList) :
                #    self.commandList.append('Stay')
                #return self.doCommand(self.commandList.pop())
            elif (self.isFreeFront()) :
                self.moveNextStep = False
                return self.moveForward()
            elif(self.isFreeLeft()) :
                self.commandList.append('Sense')
                self.commandList.append('Forward')
                return self.turnLeft()
            elif(self.isFreeRight()) :
                self.commandList.append('Sense')
                self.commandList.append('Forward')
                return self.turnRight()
            else :
                self.commandList.append('Sense')
                self.commandList.append('Forward')
                self.commandList.append('Right')
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
            if(self.isFreeFront()) :
                return self.moveForward()
            else :
                return self.turnRight()
        print compass
        
    #free: if empty space(0) or energy station(128)
    def isFreeFront(self):
        if ((self.sensor['front'] == 0) or (self.sensor['front'] == 128)):
            return True
        return False
        
    def isFreeRight(self):
        if ((self.sensor['right'] == 0) or (self.sensor['right'] == 128)):
            return True
        return False
        
    def isFreeLeft(self):
        if ((self.sensor['left'] == 0) or (self.sensor['left'] == 128)):
            return True
        return False
        
    def isFreeBack(self):
        if ((self.sensor['back'] == 0) or (self.sensor['back'] == 128)):
            return True
        return False
    
    def isPortal(self):
        if(self.sensor['front'] == 129) :
            return True
        return False
    
    def isEnergy(self):
        if(self.sensor['front'] == 128):
            return True
        return False
     