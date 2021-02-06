from enum import Enum
from typing import Union, Any, List, Optional, cast
class MemoryMap:
    def __init__(self):
        self.map = dict()
        self.messagedTiles: List['Tile'] = []
        self.moving = False
        self.minX = 0
        self.minY = 0
        self.maxX = 0
        self.maxY = 0
        self.wallsFound = ''#NESW
    def getMap(self) -> dict():
        return self.map
    def logWall(self,x,y,d):
        if not d in self.wallsFound:
            self.wallsFound+=d
        if not (x,y) in self.map:
            self.map[(x,y)] = Tile(x,y,self)
        tile = self.map[(x,y)]
        tile.declareWall(d)
    def updateWalls(self):
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
    def logTile(self,x,y, percept:str,lastMove:str):
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
        #print("====================================================")
        stench, breeze, glitter, bump, scream = perceptToBools(percept)
        percepts = PerceptsStruct(stench, breeze, glitter, bump, scream)
        if lastMove == 'init':
            self.home = (x,y)
        if bump:
            adjList = [(x,y+1),(x+1,y),(x,y-1),(x-1,y)]
            dirs = {"N":adjList[0],"E":adjList[1],"S":adjList[2],"W":adjList[3]}
            self.logWall(dirs[lastMove][0],dirs[lastMove][1],lastMove)
            self.updateWalls()
        if not (x,y) in self.map:
            self.map[(x,y)] = Tile(x,y,self)
        tile = self.map[(x,y)]
        tile.setPercepts(percepts)
        tile.processPercepts()
        tile.wasExplored = True
        tile.declareSafe()#i stepped on it, its safe for now
    def getTile(self, x,y):
        if not (x,y) in self.map:
            self.map[x,y]=Tile(x,y,self)
        return self.map[(x,y)]
    def updateMap(self):
        while not len(self.messagedTiles)==0:
            tile = self.messagedTiles.pop()
            tile.processMessages()
    def sendMessage(self, message:'Message'):
        message.toTile.messagesIn.append(message)
        self.messagedTiles.append(message.toTile)
        #print(len(self.messagedTiles))


class PerceptsStruct:
    def __init__(self,stench:bool=False, breeze:bool=False, glitter:bool=False, bump:bool=False, scream:bool=False):
        self.stench = stench
        self.breeze = breeze
        self.glitter = glitter
        self.bump = bump
        self.scream = scream
        self.hasDanger = self.stench or self.breeze
class MessageEnum(Enum):
    PIT_CHANCE=1#sender changes chance of reciever being pit
    WUMPUS_CHANCE_SENSED=2#sender changes chance of reciever being wumpus found by percept
    WUMPUS_CHANCE_PROPAGATION=3#chance that a wumpus has moved here
    SENDER_SAFE=4#sender is known safe
    RECIEVER_SAFE=5#reciever is known safe
class Message:
    def __init__(self, toTile:'Tile',fromTile:'Tile', messageType:MessageEnum, amount: float=0):
        self.toTile = toTile
        self.fromTile = fromTile
        self.amount = amount
        self.messageType=messageType
    def __str__(self):
        return "["+str(self.toTile.coords)+","+str(self.fromTile.coords)+","+str(self.messageType)+","+str(self.amount)+"]"
class Tile:#DO MORE CASTING https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
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
    def __str__(self):
        return str(self.coords)
    def __hash__(self):
        return hash(self.coords)
    def __eq__(self,other):
        return self.coords == other.coords
    def declareWall(self,d:str):
        self.isWall = True
        self.declareSafe()
        self.wallType=d
        self.overallRisk = 1000#set high cost for future algos
    
    def setPercepts(self, percepts:PerceptsStruct):
        self.percepts=percepts
    def processPercepts(self):
        #print("processing", self.percepts.breeze)
        if not self.percepts.hasDanger:
            neighbors = self.getNeighbors()
            for neighbor in neighbors:
                self.memMap.sendMessage(Message(neighbor,self,MessageEnum.RECIEVER_SAFE))
        if not self.wasExplored:
            if self.percepts.breeze:# and not self.wasExplored:#handle breeze
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
                        message = Message(neighbor,self,MessageEnum.PIT_CHANCE,1/(4-numSafe))
                        self.memMap.sendMessage(message)


        if self.percepts.stench:#handle breeze
            if (not self.wasExplored):# or self.moving:
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
    def getNeighbors(self)->List['Tile']:#returns North, east, south, west
        x = self.coords[0]
        y = self.coords[1]
        return [self.memMap.getTile(x,y+1),self.memMap.getTile(x+1,y),self.memMap.getTile(x,y-1),self.memMap.getTile(x-1,y)]
    def declareSafe(self):
        self.pitRisk = 0.0
        self.notPit = True
        if not self.memMap.moving:
            self.notWumpus=True
        self.wumpusRisk = 0.0
        for con in self.pitContributions:
            self.memMap.sendMessage(Message(con,self,MessageEnum.SENDER_SAFE))
        for con in self.wumpusContributions:
            self.memMap.sendMessage(Message(con,self,MessageEnum.SENDER_SAFE))
    def processMessages(self):
        for message in self.messagesIn:
            #print(self.coords,message,message.toTile.notPit,message.fromTile.notPit)
            messageType:MessageEnum = message.messageType
            if messageType==MessageEnum.PIT_CHANCE:
                if not message.fromTile in self.pitContributions:
                    self.pitContributions[message.fromTile]=0
                self.pitContributions[message.fromTile]+=message.amount
                if self.pitContributions[message.fromTile] == 1:
                    self.knownPit=True
                self.pitRisk+=message.amount

            if messageType==MessageEnum.WUMPUS_CHANCE_SENSED:
                if not message.fromTile in self.wumpusContributions:
                    self.wumpusContributions[message.fromTile]=0
                self.wumpusContributions[message.fromTile]+=message.amount
                if self.wumpusContributions[message.fromTile] == 1 and not self.memMap.moving:
                    self.knownWumpus=True
                self.wumpusRisk+=message.amount

            if messageType==MessageEnum.SENDER_SAFE:
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
                    unsafe = []
                    for neighbor in neighbors:
                        if neighbor.notWumpus or neighbor.isWall or neighbor.knownPit:
                            unsafe.append(neighbor)
                        else:
                            numSafe+=1
                    for neighbor in unsafe:
                        self.memMap.sendMessage(Message(neighbor,self,MessageEnum.WUMPUS_CHANCE_SENSED,wum/(4-numSafe)))
                    message.fromTile.wumpusContributions[self]=0
            if messageType==MessageEnum.RECIEVER_SAFE:
                self.declareSafe()    
            if messageType ==MessageEnum.WUMPUS_CHANCE_PROPAGATION:
                print("moving wumpi")
        self.messagesIn.clear()
    
    #Contribution system: allow each tile to know where its risk origionates
    #tiles should check if something is already declared safe before contributing
    def getRisk(self):#get the risk of the tile 0 = no risk, higher number higher risk
        return pitRisk + wumpusRisk



def perceptToBools(percept:str):
        return "S" in percept, "B" in percept, "G" in percept, "U" in percept, "C" in percept
        