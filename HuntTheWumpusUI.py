#HuntTheWumpus.py
#Wumpus World driver
#COSC370, Project 1
#Alan C. Jamieson
#Latest Revision: February 11, 2019

#This driver will ask the user for some information in regards to the format of the Hunt the Wumpus game (credit: Gregory Yob).
#This information will then be passed to the WumpusAgent module (user provided), then randomly assign wumpi, pits, and gold.
#The driver will simulate and provide sensory data as specified in the project document.

#Note: there are very few self-error checks as part of this program.
from random import randint
import WumpusAgent
import copy
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, QSize
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QHBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys
import time
import MemoryMap
from datetime import datetime
#--------------------------
#globals
#--------------------------

#player location


#--------------------------
#game functionalities
#--------------------------

#setupBoard - takes number of wumpi and arrows from input, and returns a randomly sized, populated board
#Key:
#g = gold
#e = player entry
#p = pit
#w = wumpus
#0 = empty space


#stenchCheck - takes the x and y coordinates of the player and returns if there's a wumpus in any adjacent square
def stenchCheck(x, y, l):
    if x > 0 and l[x-1][y] == 'w':
        return True
    if x < len(l)-1 and l[x+1][y] == 'w':
        return True
    if y > 0 and l[x][y-1] == 'w':
        return True
    if y < len(l)-1 and l[x][y+1] == 'w':
        return True
    return False

#glitterCheck - is the gold at my feet?
def glitterCheck(x, y, l):
    if l[x][y] == 'g':
        return True
    return False

#bumpCheck - check the border of the dungeon
def bumpCheck(x, y, l):
    if x < 0 or x > len(l)-1:
        return True
    if y < 0 or y > len(l)-1:
        return True
    return False

#breezeCheck - check to see if a pit is in an adjacent square
def breezeCheck(x, y, l):
    if x > 0 and l[x-1][y] == 'p':
        return True
    if x < len(l)-1 and l[x+1][y] == 'p':
        return True
    if y > 0 and l[x][y-1] == 'p':
        return True
    if y < len(l)-1 and l[x][y+1] == 'p':
        return True
    return False

#screamCheck - takes in the coordinates of the player, and the direction of the shot, returns True if a hit


#deathCheck - takes in the coordinates of the player, and determines if the player got eaten or fell into a pit
def deathCheck(x, y, l):
    if l[x][y] == 'w' or l[x][y] == 'p':
        return True
    return False

#moveWumpi - moves the wumpi, stored as a list of lists
def moveWumpi(w, l):
    #Wumpus will not move onto the gold, entrance, or onto a pit, but could be multiple wumpi in a space
    for wumpus in w:
        direction = randint(1,4)
        if direction == 1 and wumpus[0] != 0 and l[wumpus[0]-1][wumpus[1]] != 'g' and l[wumpus[0]-1][wumpus[1]] != 'p' and l[wumpus[0]-1][wumpus[1]] != 'e':
            l[wumpus[0]][wumpus[1]] = 0
            wumpus[0] = wumpus[0] - 1
            l[wumpus[0]][wumpus[1]] = 'w'
        if direction == 2 and wumpus[0] != len(l)-1 and l[wumpus[0]+1][wumpus[1]] != 'g' and l[wumpus[0]+1][wumpus[1]] != 'p' and l[wumpus[0]+1][wumpus[1]] != 'e':
            l[wumpus[0]][wumpus[1]] = 0
            wumpus[0] = wumpus[0] + 1
            l[wumpus[0]][wumpus[1]] = 'w'
        if direction == 3 and wumpus[1] != 0 and l[wumpus[0]][wumpus[1]-1] != 'g' and l[wumpus[0]][wumpus[1]-1] != 'p' and l[wumpus[0]][wumpus[1]-1] != 'e':
            l[wumpus[0]][wumpus[1]] = 0
            wumpus[1] = wumpus[1] - 1
            l[wumpus[0]][wumpus[1]] = 'w'
        if direction == 4 and wumpus[1] !=len(l)-1 and l[wumpus[0]][wumpus[1]+1] != 'g' and l[wumpus[0]][wumpus[1]+1] != 'p' and l[wumpus[0]][wumpus[1]+1] != 'e':
            l[wumpus[0]][wumpus[1]] = 0
            wumpus[1] = wumpus[1] + 1
            l[wumpus[0]][wumpus[1]] = 'w'

#winCheck - check to see if player is back on entrance tile, with the gold

class Ui(QtWidgets.QMainWindow):
    def setupBoard(self, wumpi, arrows):
        #get size of board, needs to be at least the number of wumpi + 2 * 2
        n = randint(wumpi+2, 200) if self.gridSize==-1 else self.gridSize

        #initialize board, 0 represents a blank space
        l = []
        for i in range(n):
            temp = [0] * n
            l.append(temp)

        #place the gold
        gx = randint(0, n-1)
        gy = randint(0, n-1)
        l[gx][gy] = 'g'

        #populate the pits, avoiding the gold, capped at twice the size of a single dimension
        #note: we are secretly ok with a pit on top of a pit, so we don't check for that
        numpits = randint(0, n*2)
        for i in range(numpits):
            x = randint(0, n-1)
            y = randint(0, n-1)
            while(x == gx and y == gy):
                x = randint(0, n-1)
                y = randint(0, n-1)
            l[x][y] = 'p'

        #populate the wumpi, avoiding gold and pits
        for i in range(wumpi):
            #loop for checking our x, y value
            flag = True
            while(flag):
                x = randint(0, n-1)
                y = randint(0, n-1)
                if l[x][y] == 0:
                    l[x][y] = 'w'
                    self.wumpilist.append([x,y])
                    flag = False

        #place the entrance, updating player x and y value
        flag = True
        while(flag):
            x = randint(0, n-1)
            y = randint(0, n-1)
            if l[x][y] == 0:
                l[x][y] = 'e'
                playerx = x
                playery = y
                flag = False
        return l, playerx, playery
    def screamCheck(self,x, y, l, d):
        if d == 'n':
            for i in range(x, -1, -1):
                if l[i][y] == 'w':
                    l[i][y] = 0
                    self.killWumpus(i, y, l)
                    return True
        if d == 's':
            for i in range(x, len(l)):
                if l[i][y] == 'w':
                    l[i][y] = 0
                    self.killWumpus(i, y, l)
                    return True
        if d == 'e':
            for i in range(y, len(l)):
                if l[x][i] == 'w':
                    l[x][i] = 0
                    self.killWumpus(x, i, l)
                    return True
        if d == 'w':
            for i in range(y, -1, -1):
                if l[x][i] == 'w':
                    l[x][i] = 0
                    self.killWumpus(x, i, l)
                    return True
        return False

    #kill the wumpus at x, y by removing it from the list
    def killWumpus(self,x, y, l):
        for i in self.wumpilist:
            if i[0] == x and i[1] == y:
                self.wumpilist.remove([x, y])
                break
    def winCheck(self,x, y, l):
        if self.gotgold and l[x][y] == 'e':
            self.isWon = True
            return True
        return False
    def closeEvent(self,event):
        self.autoStepBox.setChecked(False)
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('ui.ui', self)
        self.show()
        self.numwins = 0
        self.numpitdeaths = 0
        self.numwumpusdeaths = 0
        self.numtimeouts = 0
        self.gametype = 2 if self.wumpiTypeCombo.currentText()=="Moving" else 1
        self.numwumpi = self.wumpiNumSpin.value()
        self.numarrows = self.arrowNumSpin.value()
        self.numgames = 1
        self.newGameButton.clicked.connect(self.initBoard)
        self.runStepsButton.clicked.connect(self.onStepButton)
        self.percept = ''
        self.hLayoutFrame = QHBoxLayout(self)
        self.remoteBox.clicked.connect(self.onRemoteCheck)
        self.paintWidget = PaintWidget(self)
        self.hLayoutFrame.addWidget(self.paintWidget)
        self.frame.setLayout(self.hLayoutFrame)
        self.northButton.clicked.connect(self.onDevNorth)
        self.southButton.clicked.connect(self.onDevSouth)
        self.eastButton.clicked.connect(self.onDevEast)
        self.westButton.clicked.connect(self.onDevWest)
        self.closed = False
        self.waitSkipBox.clicked.connect(self.onSkipCheck)
        self.onRemoteCheck()
        self.initBoard()
    def onStepButton(self):
        self.doStep()
        while self.autoStepBox.isChecked():
            QApplication.processEvents()
            self.doStep()
    def onRemoteCheck(self):
        if self.remoteBox.isChecked():
            self.remoteGroup.setEnabled(True)
            self.remoteGroup.setHidden(False)
        else:
            self.remoteGroup.setEnabled(False)
            self.remoteGroup.setHidden(True)
    def onSkipCheck(self):
        self.WumpusAgent.setSkipWait(self.waitSkipBox.isChecked())
    def onDevNorth(self):
        self.percept+="1"
        self.doStep()
    def onDevEast(self):
        self.percept+="2"
        self.doStep()
    def onDevSouth(self):
        self.percept+="3"
        self.doStep()
    def onDevWest(self):
        self.percept+="4"
        self.doStep()
    def drawStuff(self):
        self.paintWidget.setBoard(self.board)
        self.paintWidget.setPlayerPos(self.playerx,self.playery)
        self.paintWidget.setDead(self.isDead)
        self.perceptLabel.setText(self.percept)
        self.paintWidget.path = copy.deepcopy(self.WumpusAgent.getPath())
        if self.showMemoryBox.isChecked():
            self.paintWidget.memoryEnabled(True)
            memory = self.WumpusAgent.getMemory()
            self.paintWidget.setMemory(memory)
        else:
            self.paintWidget.memoryEnabled(False)
        self.update()
    def initBoard(self):
        self.statusLabel.setText("")
        self.isDead = False
        self.isWon = False
        self.remainingarrows = self.arrowNumSpin.value()
        self.percept = ""
        #print("arrow",self.remainingarrows)
        self.nummoves = 0
        self.gotgold = False
        self.wumpilist = []
        self.gametype = 2 if self.wumpiTypeCombo.currentText()=="Moving" else 1
        self.numwumpi = self.wumpiNumSpin.value()
        self.numarrows = self.arrowNumSpin.value()
        self.gridSize = self.gridSpin.value()
        #set board, and player values
        self.board, self.playerx, self.playery = self.setupBoard(self.numwumpi, self.numarrows)
        
        #set parameter for player - this is the reset for the WumpusAgent
        self.WumpusAgent = WumpusAgent
        self.WumpusAgent.setParams(self.gametype, self.numarrows, self.numwumpi)
        self.WumpusAgent.setSkipWait(self.waitSkipBox.isChecked())
        #player got gold?
        

        #wumpus two dimensional array. first value is x, second value is y
        
        if stenchCheck(self.playerx, self.playery, self.board):
            self.percept = self.percept + 'S'
        if glitterCheck(self.playerx, self.playery, self.board):
            self.percept = self.percept + 'G'
        if breezeCheck(self.playerx, self.playery, self.board):
            self.percept = self.percept + 'B'
        self.drawStuff()
        if self.autoStepBox.isChecked():
            self.doStep()
    def doStep(self):
        steps = self.stepsCombo.value()
        initialnum = self.nummoves
        if self.isDead or self.isWon or self.nummoves>=4000000:
            if self.autoNewBox.isChecked():
                self.initBoard()
        while self.isDead != True and self.isWon != True and self.nummoves != 4000000 and (self.nummoves-initialnum)<steps:
            self.nummoves = self.nummoves + 1
            #get move from agent
            move = WumpusAgent.getMove(self.percept)
            #intialize self.percept string
            self.percept = ''
            #move parser
            #increment based on move, perform bump checks, move back if True
            if move == 'N':
                self.playerx = self.playerx - 1
                if bumpCheck(self.playerx, self.playery, self.board):
                    self.percept = self.percept + 'U'
                    self.playerx = self.playerx + 1
            elif move == 'S':
                self.playerx = self.playerx + 1
                if bumpCheck(self.playerx, self.playery, self.board):
                    self.percept = self.percept + 'U'
                    self.playerx = self.playerx - 1
            elif move == 'E':
                self.playery = self.playery + 1
                if bumpCheck(self.playerx, self.playery, self.board):
                    self.percept = self.percept + 'U'
                    self.playery = self.playery - 1
            elif move == 'W':
                self.playery = self.playery - 1
                if bumpCheck(self.playerx, self.playery, self.board):
                    self.percept = self.percept + 'U'
                    self.playery = self.playery + 1
            #collect scream self.percepts
            elif move == 'SN':
                if self.remainingarrows > 0 and self.screamCheck(self.playerx, self.playery, self.board, 'n'):
                    self.percept = self.percept + 'C'
                self.remainingarrows = self.remainingarrows - 1
            elif move == 'SS':
                if self.remainingarrows > 0 and self.screamCheck(self.playerx, self.playery, self.board, 's'):
                    self.percept = self.percept + 'C'
                self.remainingarrows = self.remainingarrows - 1
            elif move == 'SE':
                if self.remainingarrows > 0 and self.screamCheck(self.playerx, self.playery, self.board, 'e'):
                    self.percept = self.percept + 'C'
                self.remainingarrows = self.remainingarrows - 1
            elif move == 'SW':
                if self.remainingarrows > 0 and self.screamCheck(self.playerx, self.playery, self.board, 'w'):
                    self.percept = self.percept + 'C'
                self.remainingarrows = self.remainingarrows - 1
            #win check
            elif move == 'C':
                if self.winCheck(self.playerx, self.playery, self.board):
                    self.numwins = self.numwins + 1
                    if self.autoNewBox.isChecked():
                        self.initBoard()
                    break
            elif move == 'G':
                if self.board[self.playerx][self.playery] == 'g':
                    self.gotgold = True
                    self.board[self.playerx][self.playery] = 0
            else:
                print("Incorrect move string encountered, exiting",move)
                exit()

            #death check!
            if deathCheck(self.playerx, self.playery, self.board):
                
                if self.board[self.playerx][self.playery] == 'p':
                    self.numpitdeaths = self.numpitdeaths + 1
                    self.statusLabel.setText("died in pit")
                    self.isDead = True
                    self.paintWidget.setBoard(self.board)
                    self.paintWidget.setPlayerPos(self.playerx,self.playery)
                    self.paintWidget.setDead(self.isDead)
                    self.perceptLabel.setText(self.percept)
                    self.update()
                else:
                    self.numwumpusdeaths = self.numwumpusdeaths + 1
                    self.statusLabel.setText("died from wumpus")
                    self.isDead = True
                    self.paintWidget.setBoard(self.board)
                    self.paintWidget.setPlayerPos(self.playerx,self.playery)
                    self.paintWidget.setDead(self.isDead)
                    self.perceptLabel.setText(self.percept)
                    self.update()
                if self.autoNewBox.isChecked():
                        self.initBoard()
                break

            #other self.percepts
            if stenchCheck(self.playerx, self.playery, self.board):
                self.percept = self.percept + 'S'
            if glitterCheck(self.playerx, self.playery, self.board):
                self.percept = self.percept + 'G'
            if breezeCheck(self.playerx, self.playery, self.board):
                self.percept = self.percept + 'B'

            #move the wumpi if that game mode selected
            if self.gametype == 2:
                moveWumpi(self.wumpilist, self.board)

            #check if we timed out
            if self.nummoves == 4000000:
                numtimeouts = numtimeouts + 1
            self.drawStuff()
            QApplication.processEvents()
            before = datetime.now()
            after = datetime.now()
            dif = after-before
            while (dif.seconds+float(dif.microseconds)/1000000)<float(self.speedSlider.value())/1000.0:
                QApplication.processEvents()
                after = datetime.now()
                dif = after-before
            #if self.autoStepBox.isChecked():
            #    self.doStep()
            #time.sleep(float(self.speedSlider.value())/1000.0)
            
        #quick status print
        #print("Game number " + str(game) + " complete in " + str(self.nummoves) + " moves.")
        #cleanup for restart
class PaintWidget(QWidget):
    def paintEvent(self, event):
        try:
            self.board
        except:
            self.board = [[]]
            self.playerX = 0
            self.playerY=0
            
        for y in range(0,len(self.board)):
            for x in range(0,len(self.board[y])):
                if(self.board[y][x])==0:
                    self.drawSpace(x,y)
                if(self.board[y][x])=='g':
                    self.drawGold(x,y)
                if(self.board[y][x])=='e':
                    self.entryx = x
                    self.entryy = y
                    self.drawEntry(x,y)
                if(self.board[y][x])=='p':
                    self.drawPit(x,y)
                if(self.board[y][x])=='w':
                    self.drawWumpus(x,y)
        self.drawPlayer(self.playerX,self.playerY)
        self.drawMemory()
        #print("paintevent")
    def memoryEnabled(self,b):
        self.doMem = b
    def setMemory(self,memory):
        self.memory=memory
    def setDead(self,b):
        self.dead = b
    def setPlayerPos(self,y,x):
        self.playerX = x
        self.playerY = y
    def setBoard(self, board):
        self.board = board
    def getBoardDims(self):
        return len(self.board[0]),len(self.board)
    def getDrawDims(self):
        return min(self.geometry().width(),self.geometry().height()),min(self.geometry().width(),self.geometry().height())
    def drawWompArc(self,x,y,f):
        qp = QPainter(self)
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        qp.setPen(QPen(QColor(148,0,211), 3))
        qp.setBrush(QColor(148,0,211))
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        qp.drawArc(x*squareWid,y*squareLen,squareWid,squareLen,5760/2,5760*f)
    def drawPath(self):
        try:
            self.path
        except:
            self.path = []
        qp = QPainter(self)
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        qp.setPen(QPen(QColor(0,255,0), 3))
        qp.setBrush(QColor(0,255,0))
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        tempX = self.playerX
        tempY = self.playerY
        while len(self.path)>=1:
            move = self.path.pop()
            nextX = tempX
            nextY = tempY
            if move=="N":
                nextY-=1
            if move=="S":
                nextY+=1
            if move=="W":
                nextX-=1
            if move=="E":
                nextX+=1
            qp.drawLine(tempX*squareWid+(.5*squareWid),tempY*squareLen+(.5*squareLen),nextX*squareWid+(.5*squareWid),nextY*squareLen+(.5*squareLen))
            tempX = nextX
            tempY = nextY

    def drawPitArc(self,x,y,f):
        qp = QPainter(self)
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        qp.setPen(QPen(QColor(255,255,255), 3))
        qp.setBrush(QColor(255,255,255))
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        #print(x*squareWid,y*squareLen,squareWid,squareLen,0,5760*f)
        qp.drawArc(x*squareWid,y*squareLen,squareWid,squareLen,0,5760*f)
    def xyToNum(self,st):
        s = st.split(",")
        return int(s[0]),int(s[1])
    def drawWall(self,x,y):
        qp = QPainter(self)
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        qp.setBrush(QColor(100,100,100))
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        qp.drawRect((x*squareWid)-(.1*squareWid),(y*squareLen)-(.1*squareLen),squareWid*1.2,squareLen*1.2)
    def drawKnownPit(self,x,y):
        qp = QPainter(self)
        qp.setPen(QPen(QColor(240,240,240), 3))
        qp.setBrush(QColor(240,240,240))
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        qp.drawLine(x*squareWid,y*squareLen,x*squareWid+squareWid,y*squareLen+squareLen)
        qp.drawLine(x*squareWid,y*squareLen+squareLen,x*squareWid+squareWid,y*squareLen)
    def drawKnownWumpus(self,x,y):
        qp = QPainter(self)
        qp.setPen(QPen(QColor(148,0,211), 3))
        qp.setBrush(QColor(148,0,211))
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        qp.drawLine(x*squareWid,y*squareLen,x*squareWid+squareWid,y*squareLen+squareLen)
        qp.drawLine(x*squareWid,y*squareLen+squareLen,x*squareWid+squareWid,y*squareLen)
    def drawVisited(self,x,y):
        qp = QPainter(self)
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        qp.setBrush(QColor(255,255,0))
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        qp.drawRect((x*squareWid)+(.38*squareWid),(y*squareLen)+(.38*squareLen),.25*squareWid,.25*squareLen)
    def drawMemory(self):
        #print(self.doMem)
        if self.doMem:
            #print(self.entryx,self.entryy)
            for t in self.memory.map:
                tile:MemoryMap.Tile = self.memory.map[t]
                #print(tile.coords,tile.pitRisk)
                i= tile.coords[0]
                j = tile.coords[1]
                x = self.entryx + i
                y = self.entryy - j
                if tile.isWall:
                    self.drawWall(x,y)
                if tile.knownWumpus:
                    self.drawKnownWumpus(x,y)
                if tile.knownPit:
                    #print("known"+str(tile))
                    self.drawKnownPit(x,y)
                if tile.wasExplored:
                    self.drawVisited(x,y)
                if self.dead:
                    self.drawPlayer(self.playerX,self.playerY)
                self.drawWompArc(x,y,tile.wumpusRisk)
                self.drawPitArc(x,y,tile.pitRisk)
                self.drawPath()


    def drawSpace(self,x,y):
        #print("drawing space")
        qp = QPainter(self)
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        qp.setBrush(QColor(192,192,192))
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        qp.drawRect(x*squareWid,y*squareLen,squareWid,squareLen)
    def drawPit(self,x,y):
        #print("draw pit")
        qp = QPainter(self)
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        qp.setBrush(QColor(0,0,0))
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        qp.drawRect(x*squareWid,y*squareLen,squareWid,squareLen)
    def drawPlayer(self,x,y):
        #print("draw player")
        qp = QPainter(self)
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        qp.setBrush(QColor(0,0,200))
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        if self.dead:
            qp.setPen(QPen(QColor(200,0,0), 3))
            qp.setBrush(QColor(200,0,0))
            qp.drawLine(x*squareWid,y*squareLen,x*squareWid+squareWid,y*squareLen+squareLen)
            qp.drawLine(x*squareWid,y*squareLen+squareLen,x*squareWid+squareWid,y*squareLen)
            return
        qp.drawRect(x*squareWid,y*squareLen,squareWid,squareLen)
    def drawWumpus(self,x,y):
        #print("draw wum")
        qp = QPainter(self)
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        qp.setBrush(QColor(200,0,0))
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        qp.drawRect(x*squareWid,y*squareLen,squareWid,squareLen)
    def drawGold(self,x,y):
        #print("draw gold")
        qp = QPainter(self)
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        qp.setBrush(QColor(255,215,0))
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        qp.drawRect(x*squareWid,y*squareLen,squareWid,squareLen)
    def drawEntry(self,x,y):
        #print("draw entry")
        qp = QPainter(self)
        boardWid, boardLen = self.getBoardDims()
        drawWid, drawLen = self.getDrawDims()
        qp.setBrush(QColor(0,100,0))
        squareLen = (drawLen/boardLen)
        squareWid = (drawWid/boardWid)
        qp.drawRect(x*squareWid,y*squareLen,squareWid,squareLen)
    



app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()

