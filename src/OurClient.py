from BaseRobotClient import Command, BaseRobotClient

import networkx as nx


class TestClient(BaseRobotClient):
    global getToPortal, lastPortal, crossroadcount, returnToNode, moveNextStep, sensor, stayNextStep, bomb, Graph, sensorStrings, nodecount, lastnode, nodebeforelast, steps, orientation, commandList, bombsDropped, pos
    #constants
    global CROSSROAD, DEADEND, TURN, HORI, VERT, UP, RIGHT, DOWN, LEFT
    
    def __init__(self):
        super(TestClient , self).__init__()
        
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
        self.lastPortal = None
        self.getToPortal = False
               
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
        
        #ORIENTATION IDENTIFIER
        self.UP = 0
        self.RIGHT = 1
        self.DOWN = 2
        self.LEFT = 3
        
        self.orientation = self.UP
        
        #List for moves to do
        self.commandList = []
        
    ##
    # @brief Method to handle Bomb Drops
    # @param self
    # @return turnRight - initial command to turn
    #
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
    
    ##
    # @brief Encapsulates dropbomb-command
    # @param self
    # @return DropBomb
    #    
    def dropBomb(self):
        self.bombsDropped += 1
        return Command.DropBomb      
    
    ##
    # @brief handles behaviour when encountering an energy spot
    # @param self
    # @return moveForward - initial task: go onto the energy spot
    def energyHandler(self):
        staytime = int((128 - self.sensor['battery']) / 30 )
        for _ in range(0,staytime):
            self.commandList.append('Stay')
        self.commandList.append('Sense')
        self.moveNextStep = True
        return self.moveForward()
        
    ##
    # @brief encapsulates command for turning right
    # @param self
    # @return RightTurn
    #
    # We are saving a relative direction, according to our orientation at start,
    # that's why it's necessary to also update orientation
    def turnRight(self):
        self.orientation += 1
        self.sensor['battery'] -= 1
        self.orientation &= 3
        return Command.RightTurn
    
    ##
    # @brief encapsulates command for turning left
    # @param self
    # @return LeftTurn
    #
    # We are saving a relative direction, according to our orientation at start,
    # that's why it's necessary to also update orientation
    def turnLeft(self):
        self.orientation -= 1
        self.sensor['battery'] -= 1
        self.orientation &= 3
        return Command.LeftTurn
    
    ##
    # @brief encapsulates command for moving forward
    # @param self
    # @return RightTurn
    #
    # We are also saving coordinates. Initial position is [0,0]. With every move, we're
    # updating them, depending on robos direction.
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
    
    ##
    # @brief encapsulates stay command
    # @param self
    # @return Stay
    def stay(self):
        self.sensor['battery'] += 1
        return Command.Stay
    
    ##
    # @brief resets the robot
    # @param self
    # @return Sense
    # 
    # For example when using a portal it becomes necessary to delete the previos graph and set up a new one
    def reset(self):
        self.__init__()
        return Command.Sense
    
    ##
    # @brief prints sensor data in a formatted way
    # @param self
    # @param sensor_data - data to be printed
    # @param bumper - informs whether the robot hits a wall or not
    # @param compass - contains compass data
    # @param teleported - informs whether the robot was teleported or not
    def printSensorData(self, sensor_data, bumper, compass, teleported):
        print "compass: ", compass
        print "bomb stat: ", self.bomb
        if teleported:
            print "ups I was teleported"
        if sensor_data != None:
            print sensor_data
            
        print "Graph: ", self.Graph.nodes(data = True)
        print "Edges: ", self.Graph.edges(data = True)
    
    ##
    # @brief saves the current sensor data in local variable
    # @param self
    # @param sensor_data current data to be saved
    def setSensorData(self, sensor_data):
        self.sensor['left'] = sensor_data['left']
        self.sensor['right'] = sensor_data['right']
        self.sensor['front'] = sensor_data['front']
        self.sensor['back'] = sensor_data['back']
        self.sensor['battery'] = sensor_data['battery']
    
    ##
    # @brief routine to recharge
    # @param self
    # @return command according to battery state
    def batteryHandler(self):
        if (self.stayNextStep == 1):
            if (self.staytime <= 30) :
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
    
    ##
    # @brief returns robot to last valid crossroad
    # @param self
    # @return commandlist
    #
    # According to Tremaux's algorithm we are trying every path available and then return
    # to previous crossroad with unused path.
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

    ##
    # @brief adds a node to graph
    # @param self
    # @param sensor_data - contains current information of local environment
    # @param compass - contains direction towards goal
    #
    # For representation of the maze we are using graph structure, this method adds nodes and 
    # edges to the data structure.
    # A node represents crossroads as well as turns, deadends and portals.
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
        if (not(nodeAlreadyAdded)) :
            if(nodetype == self.CROSSROAD) :
                self.crossroadcount += 1
            self.Graph.add_node(self.nodecount, type = nodetype, openpaths = openpath, visitedpaths = list(), fromNode = last, fromPath = fromPath, position = dict(self.pos))

        if(self.nodecount > 1 and not(self.isPortalNearby()) or self.nodecount > 2 and self.isPortalNearby()) :
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
            if(nodetype == self.DEADEND) :
                crossroadthere = False
                print "Graph: ", self.Graph.nodes(data = True)
                print "NODETYPE: ", nodetype

                for x in self.Graph.node.itervalues() :
                    if(x['type'] == self.CROSSROAD) :
                        crossroadthere = True
            if(not(crossroadthere)) :
                self.getToPortal = True
            if(nodetype == self.CROSSROAD) :
                if(openpath.sort() != self.Graph.node[currentNode]['openpaths'].sort()) :
                    self.Graph.node[currentNode]['openpaths'] = openpath
        self.steps = 0
        return nodetype
    
    ##
    # @brief returns robot to last portal
    # @param self
    # @return commandlist
    #
    # According to Tremaux's algorithm we are trying every path available and then return
    # to previous portal.
    def getBackToLastPortal(self) :
        if(not(self.commandList)) :
            self.commandList.append('Reset')
            self.commandList.extend(self.addMovesToCommandList(self.pathToMoves(self.getWayToNode(self.lastPortal))))
            self.returnToNode = True
        if self.sensor['battery'] < len(self.commandList) :
            self.commandList.append('Stay')
        ret = self.commandList.pop()
        if(not(self.commandList)) :
            self.returnToNode = False
            #self.moveNextStep = False
        return self.doCommand(ret)
    
    ##
    # @brief using dijkstra algorithm to get the fastest path back to specific node
    # @param self
    # @param targetNode
    # @return path to node
    #
    # We're using the implementation of dijkstra algorithm provided by networkx
    def getWayToNode(self, targetNode):
        return nx.dijkstra_path(self.Graph, self.lastnode, targetNode, 'length')
    
    ##
    # @brief returns robot to last valid crossroad
    # @param self
    # @return commandlist
    #
    # According to Tremaux's algorithm we are trying every path available and then return
    # to previous crossroad with unused path.
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
        pathList = self.getWayToNode(thenode)
        self.lastnode = pathList[-1]
        return pathList
    
    ##
    # @brief returns moves to get back to given node
    # @param self
    # @param p - path to node
    # @return pathList containing distance and direction between nodes 
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
    
    
    ##
    # @brief converts direction and distance information into commands for robot movement
    # @param self
    # @param moveList - list containing information about direction and distance between nodes
    # @return cList - list containing commands 
    def addMovesToCommandList(self, moveList):
        cList = []
        relativedirection = self.orientation
        while moveList :
            ddList = moveList.pop()
            direction = ddList[0]
            distance = ddList[1]
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
            for _ in range(0, distance):
                cList.append('Forward')
        cList.reverse()
        return cList
    ##
    # @brief parses string into valid command
    # @param self
    # @param command - command to parse
    # @return command
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
        elif(command == 'Reset'):
            return self.reset()
    
    ##
    # @brief contains logic for robot movement
    # @param self
    # @param sensor_data - contains data of local environment
    # @param bumper - information whether robot hits object or not
    # @param compass - contains compass information
    # @param teleported - information whether robot was previously teleported
    # @return command
    def getNextCommand(self, sensor_data, bumper, compass, teleported):
        currentType = None
        self.printSensorData(sensor_data, bumper, compass, teleported)
        
        #Save current sensor data
        if sensor_data != None :
            self.setSensorData(sensor_data)
            currentType = self.addNode(sensor_data, compass)
            self.addPortal()
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
                self.steps -= 1
                if(self.orientation == 0):
                    self.pos['x'] -= 1
                elif(self.orientation == 1):
                    self.pos['y'] -= 1
                elif(self.orientation == 2):
                    self.pos['x'] += 1
                elif(self.orientation == 3):
                    self.pos['y'] += 1
            return self.returnToLastCrossroad()

        if self.commandList :
            if(bumper) :
                print "BUMPER"
                self.commandList.append('Forward')
                for _ in range(10) :
                    self.commandList.append('Stay')
                self.steps -= 1
                
                
            return self.doCommand(self.commandList.pop())
        
        if(self.getToPortal) :
            return self.getBackToLastPortal()

        print "CROSSROADCOUNT: ", self.crossroadcount 
        if(currentType == self.CROSSROAD) :
            openPath = self.Graph.node[self.lastnode]['openpaths']
            visited = self.Graph.node[self.lastnode]['visitedpaths']
            fr = self.Graph.node[self.lastnode]['fromPath']
            
                        
            if(len(openPath) > len(visited) + 1) :
                if(compass <= 1.0 or compass == 7.0) :
                    if(self.orientation in openPath and not(self.orientation in visited) and self.orientation != fr) :
                        self.Graph.node[self.lastnode]['visitedpaths'].append(self.orientation)
                        self.moveNextStep = False
                        return self.moveForward()
                if(compass <= 7.0 and compass >= 5.0) :
                    if(((self.orientation - 1) & 3) in openPath and not(((self.orientation - 1) & 3) in visited) and ((self.orientation - 1) & 3) != fr) :
                        self.commandList.append('Sense')
                        self.commandList.append('Forward')
                        return self.turnLeft()
                if(compass >= 1.0 and compass <= 3.0) :
                    if(((self.orientation + 1) & 3) in openPath and not(((self.orientation + 1) & 3) in visited) and ((self.orientation + 1) & 3) != fr) :
                        self.Graph.node[self.lastnode]['visitedpaths'].append((self.orientation + 1) & 3)
                        self.commandList.append('Sense')
                        self.commandList.append('Forward')
                        return self.turnRight()
                if(self.orientation in openPath and not(self.orientation in visited) and self.orientation != fr) :
                    #self.Graph.node[self.lastnode]['openpaths'].remove(self.orientation)
                    self.moveNextStep = False
                    self.Graph.node[self.lastnode]['visitedpaths'].append(self.orientation)
                    return self.moveForward()
            
            if(len(openPath) <= len(visited) + 1) :
                self.crossroadcount -= 1
                return self.returnToLastCrossroad()
 

            if(((self.orientation - 1) & 3) in openPath and not(((self.orientation - 1) & 3) in visited) and ((self.orientation - 1) & 3) != fr) :
                self.Graph.node[self.lastnode]['visitedpaths'].append((self.orientation - 1) & 3)
                self.commandList.append('Sense')
                self.commandList.append('Forward')
                return self.turnLeft()
            if(((self.orientation + 1) & 3) in openPath and not(((self.orientation + 1) & 3) in visited) and ((self.orientation + 1) & 3) != fr) :
                self.Graph.node[self.lastnode]['visitedpaths'].append((self.orientation + 1) & 3)
                self.commandList.append('Sense')
                self.commandList.append('Forward')
                return self.turnRight()
            return self.turnRight()
            
        
        #DEADEND Handling
        elif(currentType == self.DEADEND) :
            if(compass == 0.0) and (not(self.isFreeFront()) and not(self.isFreeRight()) and not(self.isFreeLeft())) and (self.bombsDropped < 3) and not(self.isPortal()) :
                    return self.bombDrop()
            if(self.crossroadcount) :
                return self.returnToLastCrossroad()
            if(self.isFreeFront()) :
                self.moveNextStep = False
                if (self.isEnergy()) :
                    return self.energyHandler()
                else :
                    return self.moveForward()
            if(self.isFreeLeft()) :
                self.commandList.append('Sense')
                self.commandList.append('Forward')
                return self.turnLeft()
            if(self.isFreeRight()) :
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
            print "TURN"
            direction = None
            for i in self.Graph.node[self.lastnode]['openpaths'] :
                if(i != (self.orientation + 2) & 3) :
                    direction = i
            if((self.orientation + 1) & 3 == direction) :
                self.commandList.append('Sense')
                self.commandList.append('Forward')
                return self.turnRight()
            elif((self.orientation - 1) & 3 == direction) :
                self.commandList.append('Sense')
                self.commandList.append('Forward')
                return self.turnLeft()
            elif(self.orientation == direction) :
                self.moveNextStep = False
                return self.moveForward()
            else :
                return self.turnRight()
            
        #STRAIGHT Handling at beginning  
        else :
            if(self.steps == 0) :
                if(self.isFreeFront() and compass <= 1.0 or compass == 7.0) :
                    self.moveNextStep = False
                    return self.moveForward()
                if(self.isFreeRight() and compass >= 1.0 and compass <= 3.0) :
                    self.commandList.append('Sense')
                    self.commandList.append('Forward')
                    return self.turnRight()
                if(self.isFreeLeft() and compass <= 7.0 and compass >= 5.0) :
                    self.commandList.append('Sense')
                    self.commandList.append('Forward')
                    return self.turnLeft()   
                if(self.isFreeBack() and compass <= 5.0 or compass >= 3.0) :
                    self.commandList.append('Sense')
                    self.commandList.append('Forward')
                    self.commandList.append('Right')
                    return self.turnRight()  
            if(self.isFreeFront()) :
                self.moveNextStep = False
                if (self.isEnergy()) :
                    return self.energyHandler()
                else :
                    return self.moveForward()          
            else :
                return self.turnRight()
        print compass
        
    ##
    # @return true if the field in front of the robot is passable
    def isFreeFront(self):
        if ((self.sensor['front'] == 0) or (self.sensor['front'] == 128)):
            return True
        return False
        
    ##
    # @return true if the field on the right hand side of the robot is passable
    def isFreeRight(self):
        if ((self.sensor['right'] == 0) or (self.sensor['right'] == 128)):
            return True
        return False
        
    ##
    # @return true if the field on the left hand side of the robot is passable
    def isFreeLeft(self):
        if ((self.sensor['left'] == 0) or (self.sensor['left'] == 128)):
            return True
        return False
        
    ##
    # @return true if the field behind the robot is passable
    def isFreeBack(self):
        if ((self.sensor['back'] == 0) or (self.sensor['back'] == 128)):
            return True
        return False
    
    ##
    # @return true if portal is in front of robot
    def isPortal(self):
        if(self.sensor['front'] == 129) :
            return True
        return False
    
    ##
    # @return true if portal is in von Neumann neighborhood of robot
    def isPortalNearby(self):
        if self.sensor['front'] == 129 :
            return self.orientation
        if self.sensor['left'] == 129 :
            return (self.orientation - 1) & 3
        if self.sensor['right'] == 129 :
            return (self.orientation + 1) & 3
        if self.sensor['back'] == 129 :
            return (self.orientation - 2) & 3
        return -1

    ##
    # @return true if energy station is in front of robot
    def isEnergy(self):
        if(self.sensor['front'] == 128):
            return True
        return False
    
    ##
    # @brief adds portal as a node to existing graph structure
    # @param self
    def addPortal(self):
        portal = self.isPortalNearby()
        x = self.pos['x']
        y = self.pos['y']
        if(portal != -1) :
            if portal == 0  :
                x += 1
            elif portal == 1 :
                y += 1
            elif portal == 2 :
                x -= 1
            elif portal == 3 :
                y -= 1
            if(self.lastnode) :
                last = self.lastnode
            else :
                last = None
            print self.nodecount
            self.Graph.add_node(self.nodecount, type = self.PORTAL, openpaths = portal, visitedpaths = list(), fromNode = last, fromPath = portal, position = dict(self.pos))
            self.lastPortal = self.nodecount
            if(self.nodecount == 1) :
                self.lastnode = self.nodecount
            else :
                self.Graph.add_edge(self.lastnode, self.nodecount, length = self.steps + 1, dir = self.orientation, visited = False)
            self.nodecount += 1