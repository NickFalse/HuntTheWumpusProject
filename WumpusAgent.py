class WumpusAgent:
    def __init__(self):
        self.moves = list()
        self.perceptMemory = dict() 
        self.knownSpaces = dict()
        self.x = 0
        self.y = 0
        self.move = ''
    def setParams(self, gametype, numarrows, numwumpi):
        self.gametype = gametype
        self.numarrows = numarrows
        self.numwumpi = numwumpi
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
    def getMove(self, percept):
        self.move = ""
        print("percept", percept)
        return(self.move)
######################################## all agent code goes above, below just allows oop because lrn2code
global ag
ag = WumpusAgent()
def setParams(gametype, numarrows, numwumpi):
    ag.setParams(gametype, numarrows, numwumpi)
def getMove(percept):
    return ag.getMove(percept)
    