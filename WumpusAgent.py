class WumpusAgent:
    def __init__(self):
        print("initing")
    def setParams(self, gametype, numarrows, numwumpi):
        self.gametype = gametype
        self.numarrows = numarrows
        self.numwumpi = numwumpi
    def getMove(self, percept):
        print("percept", percept)
        return("N")
######################################## all agent code goes above, below just allows oop because lrn2code
global ag
ag = WumpusAgent()
def setParams(gametype, numarrows, numwumpi):
    ag.setParams(gametype, numarrows, numwumpi)
def getMove(percept):
    return ag.getMove(percept)
    