#Faith Meyer, Lucius Latham, Nicholas True, and Thomas Dolan
#WumpusAgent.py
#2/17/21
#Project 1
#This file keeps track of all of the movements that can be made for the agent, wumpus, etc
from MemoryMap import *
class WumpusAgent:
    def __init__(self):
        self.explored = set()
        self.moves = list()

        self.memMap = MemoryMap()
        self.x = 0
        self.y = 0
        self.move = ''
        self.hasGold = False
        self.kills = 0
        self.pathing = False
        self.path = []
        self.riskTolerance = .1
        self.moveCount = 0
        self.flip=False
        self.waitSkip=False #Dev option, Default to False used to skip 20k wait on ui
    def getMemory(self):
        return self.memMap
############################travel methods
    def goNorth(self):
        self.y += 1
        self.moves.append("N")
        self.move = "N"
    def goSouth(self):
        self.y += -1
        self.moves.append("S")
        self.move = "S"
    def goEast(self):
        self.x += 1
        self.moves.append("E")
        self.move = "E"
    def goWest(self):
        self.x += -1
        self.moves.append("W")
        self.move = "W"
############################shoot methods
    def shootNorth(self):
        self.moves.append("SN")
        self.move = "SN"
    def shootSouth(self):
        self.moves.append("SS")
        self.move = "SS"
    def shootEast(self):
        self.moves.append("SE")
        self.move = "SE"
    def shootWest(self):
        self.moves.append("SW")
        self.move = "SW"
##########################others
    def grabGold(self):
        #print("grabbed gold")
        self.move = "G"
        self.hasGold=True
        self.pathing = False
        self.path=[]
    def climbOut(self):
        self.move = "C"

    #sets all flags and vars to follow path then does first step
    def followPath(self,path):
        self.path=path
        self.pathing = True
        self.followStep()

    #individual step in following a path
    def followStep(self):
        if self.x==0 and self.y==0 and self.hasGold:#dip if home with gold
            self.climbOut()
            return
        self.letterToMove(self.path.pop())#move
        if len(self.path)==0:#if done pathing, change flag
            self.pathing = False
    
    #reverses the input
    def reverseIn(self,inp):
        d = inp
        d.reverse()
        return d

    #helper function, calls a move function from a direction   
    def letterToMove(self,s):
        if s=="N":
            self.goNorth()
        if s=="E":
            self.goEast()
        if s=="S":
            self.goSouth()
        if s=="W":
            self.goWest()

    #go to the safest tile, typically unexplored. will check a larger and larger area for
    #a tile with a low enough risk, risk allowed goes up the more checks are done
    def goSafest(self,avoidExplored:bool=True,tolerance:float=0.1,checks:int=25):
        l = self.memMap.getNearestUnexploredEdges(self.memMap.getTile(self.x,self.y),2,tolerance,checks)
        #print(l)
        l.sort()#puts lowest risk at front
        if len(l)==0:
            xLen = self.memMap.maxX-self.memMap.minX
            yLen = self.memMap.maxY-self.memMap.minY
            bigLen = xLen if xLen>yLen else yLen
            bigLen = 10 if bigLen<10 else bigLen
            self.goSafest(True,tolerance+(float(checks)/(bigLen*bigLen)),checks*2)#tune this to reduce how long it gets stuck in weird situations
            return
        path = self.memMap.getPathTo(self.memMap.getTile(self.x,self.y),l[0])
        self.followPath(self.memMap.pathToMoves(path))
    
    #called on new game, resets everything
    def setParams(self, gametype, numarrows, numwumpi):
        self.explored = set()#none explored
        self.moves = ['init']#first mover
        self.memMap = MemoryMap()#new memories
        self.memMap.moving=True if gametype==2 else False#input handling on movement
        self.x = 0
        self.y = 0
        self.move = ''#holds move
        self.hasGold = False
        self.kills = 0#wumpi killed
        self.moving = self.memMap.moving
        self.numarrows = numarrows if numarrows>-1 else 1
        self.numwumpi = numwumpi if numarrows>-1 else 1
        self.devMode=True#enables remote
        self.pathing=False#flag for if currently following a path
        self.moveCount=0

    def skipWait(self,b:bool):#function to override wait
        self.waitSkip = b

    def getMove(self, percept):#gets move from agent
        if "U" in percept:#handle bump and adjust coords
            last = self.moves[-1]#get last move
            if last == "N":#if dir, reverse that coord chance
                self.y += -1
            elif last == "E":
                self.x +=-1
            elif last =="S":
                self.y +=1
            elif last =="W":
                self.x+=1
        
        if "G" in percept:#if standing on gold
            self.grabGold()
            return self.move#return so move not overriden
        
        self.memMap.logTile(self.x,self.y,percept,self.moves[-1])#logs tile standing on
        self.memMap.updateMap()#update the map, this lets all the tiles communicate their findings with eachother
        #especially useful on moving wumpi where risk moves around

        if(self.moving and self.moveCount<20000 and not self.waitSkip):#moving wumpi are much denser against the wall as game goes on, this helps us avoid them
            #this code is disabled on waitSkip being true, this is just to make it better on the ui
            self.shootNorth()
            self.moveCount+=1
            #print(self.moveCount)
            return self.move

        if self.pathing:#if following a path
            self.followStep()
            return self.move

        if self.hasGold and not self.pathing:
            self.followPath(self.memMap.pathToMoves(self.reverseIn(self.memMap.getPathTo(self.memMap.map[(0,0)],self.memMap.map[(self.x,self.y)]))))#path from spawn to agent
            #this reversed approach shows to be 25% faster on average
            return self.move        
        
        
        if self.devMode:#remote control for testing or just swag
            if "1" in percept:
                self.goNorth()
                return(self.move)
            elif "2" in percept:
                self.goEast()
                return(self.move)
            elif "3" in percept:
                self.goSouth()
                return(self.move)
            elif "4" in percept:
                self.goWest()
                return(self.move)
        
        self.goSafest()
        
        return(self.move)
######################################## all agent code goes above, below just allows oop because lrn2code
global ag
ag = WumpusAgent()
def setParams(gametype, numarrows, numwumpi):
    ag.setParams(gametype, numarrows, numwumpi)
def getMove(percept):
    return ag.getMove(percept)
def getMemory():
    return ag.getMemory()
def setSkipWait(b:bool):
    ag.skipWait(b)
def getPath():
    return ag.path