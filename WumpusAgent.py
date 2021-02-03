class WumpusAgent:
    def __init__(self):
        self.explored = set()
        self.moves = list()
        self.perceptMemory = dict()
        self.knownSpaces = dict()#S = Safe, P = pit, W = Wompus, E = Edge
        self.pitOdds = dict()#0-1, .25 = 1/4 chance
        self.wompusOdds = dict()#0-1, .25 = 1/4 chance
        self.x = 0
        self.y = 0
        self.move = ''
        self.hasGold = False
        self.kills = 0
        self.undoing = False
    def getMemory(self):
        return self.knownSpaces, self.pitOdds, self.wompusOdds
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
        self.move = "G"
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
        self.move = getOpposite(self.moves[self.undoStart-self.undoCount])
        self.undoCount += 1
        if self.undoCount == self.undoFor:
            self.undoing = False
    def perceptToBools(self,percept):
        return "S" in percept, "B" in percept, "G" in percept, "U" in percept, "C" in percept
    def logPercepts(self, stench, breeze, glitter, bump, scream):
        adjList = [self.xyToStr(self.x,self.y+1),self.xyToStr(self.x+1,self.y),self.xyToStr(self.x,self.y-1),self.xyToStr(self.x-1,self.y),]
        dirs = {"N":adjList[0],"E":adjList[1],"S":adjList[2],"W":adjList[3]}
        if bump:
            self.knownSpaces[dirs[self.moves[-1]]]="E"
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
        
    
    

    def setParams(self, gametype, numarrows, numwumpi):
        self.explored = set()
        self.moves = list()
        self.perceptMemory = dict()
        self.knownSpaces = dict()#S = Safe, P = pit, W = Wompus, E = Edge
        self.pitOdds = dict()#0-1, .25 = 1/4 chance
        self.wompusOdds = dict()#0-1, .25 = 1/4 chance
        self.x = 0
        self.y = 0
        self.move = ''
        self.hasGold = False
        self.kills = 0
        self.undoing = False
        self.moving = gametype==2
        self.numarrows = numarrows
        self.numwumpi = numwumpi
    def getMove(self, percept):
        print(self.pitOdds)
        self.perceptMemory[self.posStr()] = percept
        self.knownSpaces[self.posStr()]="S"#current space is guarenteed to be currently safe, would be dead if it were bad
        if self.undoing:##keep for backtrack support
            self.undo()
        stench, breeze, glitter, bump, scream = self.perceptToBools(percept)#bools to make parsing easier
        self.logPercepts(stench, breeze, glitter, bump, scream)#data gathering function
        
        
        
        
        self.goNorth()

        print("percept", percept)
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