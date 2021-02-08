from MemoryMap import *
class WumpusAgent:
    def __init__(self):
        self.explored = set()
        self.moves = list()
        #self.perceptMemory = dict()
        #self.knownSpaces = dict()#S = Safe, P = pit, W = Wompus, E = Edge
        #self.pitOdds = dict()#0-1, .25 = 1/4 chance
        #self.wompusOdds = dict()#0-1, .25 = 1/4 chance
        self.memMap = MemoryMap()
        self.x = 0
        self.y = 0
        self.move = ''
        self.hasGold = False
        self.kills = 0
        self.undoing = False
        self.pathing = False
        self.path = []
        self.riskTolerance = .1
    def getMemory(self):
        return self.memMap
    def xyToStr(self,x,y):
        return str(x)+","+str(y)
    def posStr(self):
        return self.xyToStr(self.x,self.y)
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
    def undoAll(self):
        self.undoMoves(len(self.moves))
    def undoMoves(self,num):
        self.undoing = True
        self.undoStart = len(self.moves)-1
        self.undoCount = 0
        self.undoFor = num
        self.undo()
    def getOpposite(self, move):
        undoDict = {"N":"S","S":"N","E":"W","W":"E"}
        return undoDict[move]
    def undo(self):
        self.move = self.getOpposite(self.moves[self.undoStart-self.undoCount])
        self.undoCount += 1
        if self.undoCount == self.undoFor:
            self.undoing = False
    def followPath(self,path):
        #print("Follow path:",self.memMap.pathToString(path))
        self.path=path
        self.pathing = True
        self.followStep()
    def followStep(self):
        if self.x==0 and self.y==0 and self.hasGold:
            self.climbOut()
            return
        self.letterToMove(self.path.pop())
        if len(self.path)==0:
            self.pathing = False
    def logPercepts(self, stench, breeze, glitter, bump, scream):
        #adjList = [self.xyToStr(self.x,self.y+1),self.xyToStr(self.x+1,self.y),self.xyToStr(self.x,self.y-1),self.xyToStr(self.x-1,self.y),]
        #dirs = {"N":adjList[0],"E":adjList[1],"S":adjList[2],"W":adjList[3]}
        #if bump:
        #    self.knownSpaces[dirs[self.moves[-1]]]="E"
        if not self.posStr() in self.explored:
            self.explored.add(self.posStr())
            if breeze:
                for xy in adjList:
                    if not xy in self.explored:
                        if xy in self.pitOdds:
                            self.pitOdds[xy]+=.25
                            if self.pitOdds[xy]==1:
                                self.knownSpaces[xy]="P"
                        else:
                            self.pitOdds[xy]=.25
            if stench:
                for xy in adjList:
                    if not xy in self.explored:
                        if xy in self.wompusOdds:
                            self.wompusOdds[xy]+=.25
                            if self.wompusOdds[xy]==1:
                                self.knownSpaces[xy]="W"
                        else:
                            self.wompusOdds[xy]=.25
        if self.knownSpaces[self.posStr()]=="S" or self.posStr()=="0,0":
            self.wompusOdds[self.posStr()]=0
            self.pitOdds[self.posStr()]=0
        
    def reverseIn(self,inp):
        d = inp
        d.reverse()
        return d
    def letterToMove(self,s):
        #print("letter:",s)
        if s=="N":
            self.goNorth()
        if s=="E":
            self.goEast()
        if s=="S":
            self.goSouth()
        if s=="W":
            self.goWest()
    def goSafest(self,avoidExplored:bool=True,tolerance:float=0.1,checks:int=25):
        l = self.memMap.getNearestUnexploredEdges(self.memMap.getTile(self.x,self.y),2,tolerance,checks)
        #print(l)
        l.sort()#puts lowest risk at front
        if len(l)==0:
            xLen = self.memMap.maxX-self.memMap.minX
            yLen = self.memMap.maxY-self.memMap.minY
            bigLen = xLen if xLen>yLen else yLen
            bigLen = 2 if bigLen==0 else bigLen
            self.goSafest(True,tolerance+(float(checks)/(bigLen*bigLen)),checks*2)#tune this to reduce how long it gets stuck in weird situations
            return
        path = self.memMap.getPathTo(self.memMap.getTile(self.x,self.y),l[0])
        self.followPath(self.memMap.pathToMoves(path))
    def setParams(self, gametype, numarrows, numwumpi):
        self.explored = set()
        self.moves = ['init']
        self.memMap = MemoryMap()
        self.perceptMemory = dict()
        self.x = 0
        self.y = 0
        self.move = ''
        self.hasGold = False
        self.kills = 0
        self.undoing = False
        self.moving = gametype==2
        self.numarrows = numarrows
        self.numwumpi = numwumpi
        self.devMode=True
        self.pathing=False
    def getMove(self, percept):
        #print(self.path)
        ###self.perceptMemory[self.posStr()] = percept
        ###self.knownSpaces[self.posStr()]="S"#current space is guarenteed to be currently safe, would be dead if it were bad
        if "U" in percept:
            last = self.moves[-1]
            if last == "N":
                self.y += -1
            elif last == "E":
                self.x +=-1
            elif last =="S":
                self.y +=1
            elif last =="W":
                self.x+=1
        if "G" in percept:
            self.grabGold()
            return self.move
        self.memMap.logTile(self.x,self.y,percept,self.moves[-1])
        self.memMap.updateMap()
        if self.pathing:
            self.followStep()
            return self.move
        if self.undoing:##keep for backtrack support
            self.undo()
            return self.move
        if self.hasGold and not self.pathing:
            self.followPath(self.memMap.pathToMoves(self.reverseIn(self.memMap.getPathTo(self.memMap.map[(0,0)],self.memMap.map[(self.x,self.y)]))))#path from spawn to agent
            #this reversed approach shows to be 25% faster on average
            return self.move
        ###self.logPercepts(stench, breeze, glitter, bump, scream)#data gathering function ###move to mem map
        
        
        
        if self.devMode:
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
        #self.goNorth()
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