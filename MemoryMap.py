#Faith Meyer, Lucius Latham, Nicholas True, and Thomas Dolan
#MemoryMap.py
#2/17/21
#Project 1
#This file holds the memory map and related classes, these store the information needed for the ai to function and handle calculation of risks and exploration
from enum import Enum
from typing import Union, Any, List, Optional, cast, Dict
import random

#Memory map class, holds all tiles and has functions to make them work.
class MemoryMap:
    def __init__(self):#setup initial vars
        self.map = dict()#holds all tiles
        self.messagedTiles: List['Tile'] = []#tiles that have recieved a message
        self.moving = False#true if wumpi moving
        self.minX = 0#
        self.minY = 0#min and max x/y to handle wall and allow for a 'mid point'
        self.maxX = 0#
        self.maxY = 0#
        self.wallsFound = ''#NESW
        self.wumTiles=[]#holds tiles for wumpus propagation
        self.justPlacedTiles=[]#wumpus risks that were just placed and should be ignored for a round

    def dist(self,fromTile,toTile):#heuristic for a* just city block distance
        x=fromTile.coords[0]
        y=fromTile.coords[1]
        j=toTile.coords[0]
        k=toTile.coords[1]
        dx = abs(x-j)
        dy = abs(y-k)
        return ((dx)+(dy))

    def pathToString(self,path):#converts a path to a string for print out
        re = "["
        for tile in path:
            re+=str(tile)+","
        re = re[0:len(re)-1]
        re+="]"
        return re

    def pathToMoves(self,path):#converts a path to moves, used for agent. NOTE:probably belongs as static function
        mvs = []
        while len(path)>1:
            mvs.append(self.getRelativeDirTiles(path[0],path[1]))
            path=path[1:]
        mvs.reverse()
        return mvs

    def reconstructPath(self,camefrom,current):#A* reconstruction see getPathTo for citation
        total_path = [current]
        while current in camefrom:
            current = camefrom[current]
            total_path= [current]+total_path
        p = "["
        for tile in total_path:
            p+=str(tile)+","
        return total_path

    def wumpusPropagationTick(self):#propagates the wumpus risk, allows for a guess of where a wumpus may have made it to after a period of time
        #NOTE could have been more useful with some tuning of the decay speed and the change in percept order in driver
        if self.moving:
            for tile in self.wumTiles:
                tile.propagateWumpus()
            for tile in self.justPlacedTiles:
                if not tile in self.wumTiles:
                    self.wumTiles.append(tile)
            self.justPlacedTiles.clear()

    def getPathTo(self,fromTile,toTile):#a* strongly based on pseudo code from https://en.wikipedia.org/wiki/A*_search_algorithm
        #comments in this function are left as an exercise to the reader
        toWas = toTile.wasExplored
        toTile.wasExplored=True
        fromWas = fromTile.wasExplored
        fromTile.wasExplored=True
        opn = set()
        opn.add(fromTile)
        cameFrom = dict()
        gScore = dict()
        gScore[fromTile]=0
        fScore = dict()
        fScore[fromTile]=self.dist(fromTile,toTile)
        while len(opn)>0:
            l=list(opn)
            lowest:'Tile'
            lowest = l[0]
            opstr="open:["
            for tile in l:
                opstr+=str(tile)
                if fScore[tile]<fScore[lowest]:
                    lowest=tile
            current = lowest
            if current==toTile:
                toTile.wasExplored=toWas
                fromTile.wasExplored=fromWas
                return self.reconstructPath(cameFrom,current)
            opn.remove(current)
            for neighbor in current.getExploredNeighbors():
                tempGScore = gScore[current]+(neighbor.getRisk()*50)#multiply risk by a relatively large number to make it matter a bit. in considerations
                if not neighbor in gScore:
                    gScore[neighbor] = 999999999
                if tempGScore<gScore[neighbor]:
                    cameFrom[neighbor]=current
                    gScore[neighbor]=tempGScore
                    fScore[neighbor]=gScore[neighbor]+self.dist(neighbor,toTile)
                    if not neighbor in opn:
                        opn.add(neighbor)
        return 0
    
    def getNearestUnexploredEdges(self,tile,count:int=1,riskTolerance:float=0,maxChecks:int=25):#Find an unexplored tile with a path to the current tile
        #risk count and max checks all tune how large the area this calculates on is
        checked = set()#tiles that have been checked
        tiles = [tile]
        results = []#unexplored tiles with an acceptable risk
        while len(tiles)>0:
            if len(checked)>maxChecks:
                return results
            neighbors = tiles[0].getNeighbors()
            for neighbor in neighbors:
                if (not (neighbor.wasExplored or neighbor.isWall)) and neighbor.getRisk()<riskTolerance:#kept trying to explore other side of wall
                    if not neighbor in results:
                        results.append(neighbor)
                    if len(results)>=count:
                        return results
                elif neighbor.wasExplored and (not neighbor in checked) and (not neighbor.isWall) and (not neighbor in tiles):#IF Mess, could be improved
                    tiles.append(neighbor)
            checked.add(tiles[0])
            tiles.remove(tiles[0])
        return results
            

    def getRelativeDir(self,x,y,tile):#direction of tile relative to coords
        co = tile.coords
        i=co[0]
        j=co[1]
        re = ""
        if j<y:
            re+="S"
        if j>y:
            re+="N"
        if i>x:
            re+="E"
        if i<x:
            re+="W"
        return re
    
    def getRelativeDirTiles(self,fromT,tile):#direction of tile relative to another tile
        co = tile.coords
        i=co[0]
        j=co[1]
        x=fromT.coords[0]
        y=fromT.coords[1]
        re = ""
        if j<y:
            re+="S"
        if j>y:
            re+="N"
        if i>x:
            re+="E"
        if i<x:
            re+="W"
        return re
    
    def getNeighbors(self,x,y):#get USEFUL neighbors of coords
        neighbors = self.map[(x,y)].getNeighbors()
        re = []
        for ne in neighbors:
            if not (ne.isWall or ne.knownPit or ne.knownWumpus):
                re.append(ne)
        return re

    def getUnexploredNeighbors(self,x,y):#same as above but non explored
        neighbors = self.getNeighbors(x,y)
        r = []
        for neighbor in neighbors:
            if not neighbor.wasExplored:
                r.append(neighbor)
        return r
    
    def getMap(self) -> dict():#cute how i thought i was gonna do this
        return self.map
    
    def logWall(self,x,y,d):#logs a wall, just a helper function to reduce how many times i would write t his code
        if not d in self.wallsFound:
            self.wallsFound+=d
        if not (x,y) in self.map:
            self.map[(x,y)] = Tile(x,y,self)
        tile = self.map[(x,y)]
        tile.declareWall(d)
    
    def updateWalls(self):#expand the walls so as we explore, more walls are added, allows us to constrain the map with 4 bumps
        if "N" in self.wallsFound:
            for i in range(self.minX,self.maxX+1):
                self.logWall(i,self.maxY+1,"N")
        if "S" in self.wallsFound:
            for i in range(self.minX,self.maxX+1):
                self.logWall(i,self.minY-1,"S")
        if "E" in self.wallsFound:
            for i in range(self.minY,self.maxY+1):
                self.logWall(self.maxX+1,i,"E")
        if "W" in self.wallsFound:
            for i in range(self.minY,self.maxY+1):
                self.logWall(self.minX-1,i,"W")
    
    def logTile(self,x,y, percept:str,lastMove:str):#logs tile with percept MOST IMPORTANT FUNCTION
        if x<self.minX:
            self.minX=x
            self.updateWalls()
        if x>self.maxX:
            self.maxX=x
            self.updateWalls()
        if y<self.minY:
            self.minY=y
            self.updateWalls()
        if y>self.maxY:
            self.maxY=y
            self.updateWalls()
        #chunk above updates walls and min/max's as we go

        stench, breeze, glitter, bump, scream = perceptToBools(percept)#convenience
        percepts = PerceptsStruct(stench, breeze, glitter, bump, scream)#cOnVEniEncE
        if bump:#check for wall and deal with that
            adjList = [(x,y+1),(x+1,y),(x,y-1),(x-1,y)]
            dirs = {"N":adjList[0],"E":adjList[1],"S":adjList[2],"W":adjList[3]}#this and above allow for easy conversion of move into wall coords
            self.logWall(dirs[lastMove][0],dirs[lastMove][1],lastMove)
            self.updateWalls()
        
        if not (x,y) in self.map:#if new tile, add it
            self.map[(x,y)] = Tile(x,y,self)
        tile = self.map[(x,y)]
        tile.setPercepts(percepts)
        tile.processPercepts()
        tile.wasExplored = True
        tile.declareSafe()#i stepped on it, its safe for now

    def getTile(self, x,y):#get tile from coords, saves some typing. kinda defeated by privates being kinda shit in python
        if not (x,y) in self.map:
            self.map[x,y]=Tile(x,y,self)
        return self.map[(x,y)]

    def updateMap(self):#recalculates everything and transmits messages
        self.wumpusPropagationTick()
        while not len(self.messagedTiles)==0:
            tile = self.messagedTiles.pop()
            tile.processMessages()
    
    def sendMessage(self, message:'Message'):#allow tiles to dm eachother
        #NOTE bit of complication for the sake of complication but could allow for threading
        message.toTile.messagesIn.append(message)
        self.messagedTiles.append(message.toTile)


class PerceptsStruct:#C++ native likes structs, bite me
    def __init__(self,stench:bool=False, breeze:bool=False, glitter:bool=False, bump:bool=False, scream:bool=False):
        self.stench = stench
        self.breeze = breeze
        self.glitter = glitter
        self.bump = bump
        self.scream = scream
        self.hasDanger = self.stench or self.breeze

class MessageEnum(Enum):#enum for type of message
    PIT_CHANCE=1#sender changes chance of reciever being pit
    WUMPUS_CHANCE_SENSED=2#sender changes chance of reciever being wumpus found by percept
    WUMPUS_CHANCE_PROPAGATION=3#chance that a wumpus has moved here
    SENDER_SAFE=4#sender is known safe
    RECIEVER_SAFE=5#reciever is known safe

class Message:#message class
    def __init__(self, toTile:'Tile',fromTile:'Tile', messageType:MessageEnum, amount: float=0):
        self.toTile = toTile
        self.fromTile = fromTile
        self.amount = amount
        self.messageType=messageType
    def __str__(self):#tostring is pog
        return "["+str(self.toTile.coords)+","+str(self.fromTile.coords)+","+str(self.messageType)+","+str(self.amount)+"]"

class Tile:#describe a tile or "room" in wumpus world
    def __init__(self,x:int,y:int,memMap:MemoryMap):
        self.memMap = memMap
        self.coords = (x,y)
        self.pitRisk = 0.0#risk of being a pit, score of 1 not always a pit
        self.wumpusRisk = 0.0#risk of being a wumpus
        self.notWumpus = False#only to be unsed in non moving
        self.percepts = PerceptsStruct()#list of known percepts
        self.isWall = False
        self.safe = False#used when declared safe, can be reversed by aditional risk being contributed
        self.notPit = False#definitely not a pit
        self.knownPit=False#definitely a pit
        self.knownWumpus = False
        self.overallRisk = 0.0#for use in cost based things
        self.pitContributions:Dict['Tile',float]=dict()
        self.wumpusContributions:Dict['Tile',float]=dict()
        self.stateMachine = 0#place holder, may have a mode where every tile recieves a tick to distribute moving wumpus risk
        self.messagesMade:List[Message]=[]
        self.messagesIn:List[Message]=[]#contributions recieved but not yet processed
        self.wasExplored:bool = False
        self.wallType = ""#NESW
        self.neighborMode = 0 if not self.memMap.moving else 6#0 = default, 1 = spiral, 2 = random

    def __lt__(self,other):#less than, allows for sorting array of tiles by risk
        return self.getRisk()<other.getRisk()

    def __str__(self):
        return str(self.coords)

    def __hash__(self):#enables hashing
        return hash(self.coords)

    def __eq__(self,other):#equal
        return self.coords == other.coords

    def declareWall(self,d:str):#this tile is a wall
        self.isWall = True
        self.declareSafe()#walls cant hurt you
        self.wallType=d#wall type is north south etc
        self.wasExplored=True#lie but it helps
        self.overallRisk = 1000#set high cost for future algos

    def getRisk(self):#funtion to total risk of tile
        return self.pitRisk+self.wumpusRisk

    def setPercepts(self, percepts:PerceptsStruct):#store percepts
        self.percepts=percepts

    def processPercepts(self):#processes the percepts on a tile
        if not self.percepts.hasDanger:#if safe and no bad percepts
            neighbors = self.getNeighbors()
            for neighbor in neighbors:
                self.memMap.sendMessage(Message(neighbor,self,MessageEnum.RECIEVER_SAFE))#tell neighbors they arent dangerous
        
        if not self.wasExplored:#dont need to do this if we already went there, causes infini pit
            if self.percepts.breeze:#if breeze calculate and distribute pit risk
                neighbors = self.getNeighbors()
                numSafe = 0.0
                unsafe = []
                for neighbor in neighbors:
                    if not(neighbor.notPit or neighbor.isWall):
                        unsafe.append(neighbor)
                    else:
                        numSafe+=1
                if numSafe<4:
                    for neighbor in unsafe:
                        message = Message(neighbor,self,MessageEnum.PIT_CHANCE,1/(4-numSafe))#tell neighbors their pit risk
                        self.memMap.sendMessage(message)
                        


        if self.percepts.stench:#handle stench
            if self.memMap.moving:#different behavior for moving wumpi
                factor = 1.0
                risk = (1.0/9.0)*factor
                x = self.coords[0]
                y = self.coords[1]
                tiles = [(x,y),(x+2,y),(x+1,y+1),(x,y+2),(x-1,y+1),(x-2,y),(x-1,y-1),(x,y-2),(x+1,y-1)]#excessive workaround for bad percept driver code
                for t in tiles:
                    tile = self.memMap.getTile(t[0],t[1])
                    tile.wumpusRisk=risk
                    if not tile in self.memMap.wumTiles:
                        self.memMap.justPlacedTiles.append(tile)
                tiles = [(x+1,y),(x,y+1),(x,y-1),(x-1,y)]
                for t in tiles:
                    tile = self.memMap.getTile(t[0],t[1])
                    tile.wumpusRisk=tile.wumpusRisk/4.0
                    if not tile in self.memMap.wumTiles:
                        self.memMap.wumTiles.append(tile)
            elif (not self.wasExplored) :#basicaly same as pit code above but for wumpi
                neighbors = self.getNeighbors()
                numSafe = 0.0
                unsafe = []
                for neighbor in neighbors:
                    if not(neighbor.notWumpus or neighbor.isWall):
                        unsafe.append(neighbor)
                    else:
                        numSafe+=1
                if numSafe<4:
                    for neighbor in unsafe:
                        message = Message(neighbor,self,MessageEnum.WUMPUS_CHANCE_SENSED,1/(4-numSafe))
                        self.memMap.sendMessage(message)
    
    def propagateWumpus(self):#propagates wumpus risk
        neighbors = self.getNeighbors()
        numSafe = 0.0
        unsafe = []
        for neighbor in neighbors:
            if not(neighbor.notWumpus or neighbor.isWall or neighbor.knownPit):
                unsafe.append(neighbor)
            else:
                numSafe+=1
        
        if self.wumpusRisk>1:
            self.wumpusRisk=1
        if numSafe<4:
            for neighbor in unsafe:
                    risk = (((.25*self.wumpusRisk)))
                    risk = risk if (((.25*self.wumpusRisk)))<.2 else .2
                    #print(risk,self.wumpusRisk)
                    if risk>.01:
                        message = Message(neighbor,self,MessageEnum.WUMPUS_CHANCE_PROPAGATION,risk)
                        
                        self.memMap.sendMessage(message)
        self.wumpusRisk=((.25*self.wumpusRisk)*(numSafe))#1.2 causes decay
        if self.wumpusRisk<0:
            self.wumpusRisk=0
        if self.wumpusRisk<.02:#trims down tiles with low risk
            self.wumpusRisk=0
            if self in self.memMap.wumTiles:
                self.memMap.wumTiles.remove(self)
    
    def getNeighbors(self)->List['Tile']:#returns neighbors in different orders
        #this function shapes the exploration pattern
        x = self.coords[0]
        y = self.coords[1]
        tN=self.memMap.getTile(x,y-1)
        tS=self.memMap.getTile(x,y+1)
        tE=self.memMap.getTile(x-1,y)
        tW=self.memMap.getTile(x+1,y)
        re=[]
        if(self.neighborMode==1):#this makes a spiral explore pattern
            re = [0,0,0,0]
            if abs(x)>abs(y):
                re[0]=tS if x>=0 else tN
                re[2]=tN if x>=0 else tS
                re[1]=tE if x>=0 else tW
                re[3]=tW if x>=0 else tE
            elif abs(y)>abs(x):
                re[1]=tN if y>=0 else tS
                re[3]=tS if y>=0 else tN
                re[0]=tE if y>=0 else tW
                re[2]=tW if y>=0 else tE
            else:
                if x>0 and y>0:
                    re=[tE,tN,tW,tS]
                elif x<0 and y>0:
                    re=[tN,tW,tS,tE]
                elif x<0 and y<0:
                    re=[tW,tS,tE,tN]
                else:
                    re=[tS,tE,tN,tW]
        elif(self.neighborMode==6):#this makes a spiral explore pattern biased toward mid map
            mx = int((self.memMap.maxX-self.memMap.minX)/2)#mids
            my = int((self.memMap.maxY-self.memMap.minY)/2)
            re = [0,0,0,0]
            if abs(mx-x)>abs(my-y):
                re[0]=tS if x>=mx else tN
                re[2]=tN if x>=mx else tS
                re[1]=tE if x>=mx else tW
                re[3]=tW if x>=mx else tE
            elif abs(my-y)>abs(mx-x):
                re[1]=tN if y>=my else tS
                re[3]=tS if y>=my else tN
                re[0]=tE if y>=my else tW
                re[2]=tW if y>=my else tE
            else:
                if x>mx and y>my:
                    re=[tE,tN,tW,tS]
                elif x<mx and y>my:
                    re=[tN,tW,tS,tE]
                elif x<mx and y<my:
                    re=[tW,tS,tE,tN]
                else:
                    re=[tS,tE,tN,tW]
        elif self.neighborMode==2:#random
            re= [self.memMap.getTile(x,y+1),self.memMap.getTile(x+1,y),self.memMap.getTile(x,y-1),self.memMap.getTile(x-1,y)]
            random.shuffle(re)
        else:#default explore east to west
            re= [self.memMap.getTile(x,y+1),self.memMap.getTile(x+1,y),self.memMap.getTile(x,y-1),self.memMap.getTile(x-1,y)]
        return re

    def getExploredNeighbors(self)->List['Tile']:#obvious
        l = self.getNeighbors()
        o = []
        for n in l:
            if n.wasExplored and not n.isWall:
                o.append(n)
        return o

    def declareSafe(self):#declare a tile as safe
        self.pitRisk = 0.0
        self.notPit = True
        if not self.memMap.moving:
            self.notWumpus=True
        if not self.wumpusRisk==.9:#dont get rid of freshly placed wumpus risks
            self.wumpusRisk = 0.0
        for con in self.pitContributions:
            self.memMap.sendMessage(Message(con,self,MessageEnum.SENDER_SAFE))#transmit safe
        if not self.memMap.moving:
            for con in self.wumpusContributions:
                self.memMap.sendMessage(Message(con,self,MessageEnum.SENDER_SAFE))#transmit safe

    def processMessages(self):#handles messages
        for message in self.messagesIn:
            messageType:MessageEnum = message.messageType
            if messageType==MessageEnum.PIT_CHANCE:#log pit chance
                if not message.fromTile in self.pitContributions:
                    self.pitContributions[message.fromTile]=0
                self.pitContributions[message.fromTile]+=message.amount
                if self.pitContributions[message.fromTile] == 1:
                    self.knownPit=True
                self.pitRisk+=message.amount

            if messageType==MessageEnum.WUMPUS_CHANCE_SENSED:#log wumpus chance from sensing
                if not message.fromTile in self.wumpusContributions:
                    self.wumpusContributions[message.fromTile]=0
                self.wumpusContributions[message.fromTile]+=message.amount
                if self.wumpusContributions[message.fromTile] == 1 and not self.memMap.moving:
                    self.knownWumpus=True
                self.wumpusRisk+=message.amount

            if messageType==MessageEnum.SENDER_SAFE:#sender is safe
                if self in message.fromTile.pitContributions:
                    pit = message.fromTile.pitContributions[self]
                    neighbors = self.getNeighbors()
                    recievers = []
                    numSafe = 0.0
                    for neighbor in neighbors:
                        if not (neighbor.notPit or neighbor.isWall or neighbor.knownWumpus):
                            recievers.append(neighbor)
                        else:
                            numSafe+=1
                    for neighbor in recievers:
                        self.memMap.sendMessage(Message(neighbor,self,MessageEnum.PIT_CHANCE,pit/(4-numSafe)))
                    message.fromTile.pitContributions[self]=0
                if self in message.fromTile.wumpusContributions:
                    wum = message.fromTile.wumpusContributions[self]
                    neighbors = self.getNeighbors()
                    numSafe = 0.0
                    recievers = []
                    for neighbor in neighbors:
                        if not (neighbor.notWumpus or neighbor.isWall or neighbor.knownPit):
                            recievers.append(neighbor)
                        else:
                            numSafe+=1
                    for neighbor in recievers:
                        self.memMap.sendMessage(Message(neighbor,self,MessageEnum.WUMPUS_CHANCE_SENSED,wum/(4-numSafe)))
                    message.fromTile.wumpusContributions[self]=0
            if messageType==MessageEnum.RECIEVER_SAFE:
                self.declareSafe()    
            if messageType ==MessageEnum.WUMPUS_CHANCE_PROPAGATION:
                self.wumpusRisk+=message.amount
                if not self in self.memMap.wumTiles:
                    self.memMap.wumTiles.append(self)
        self.messagesIn.clear()

def perceptToBools(percept:str):
        return "S" in percept, "B" in percept, "G" in percept, "U" in percept, "C" in percept
        
