#Faith Meyer, Lucius Latham, Nicholas True, and Thomas Dolan
#testHarness.py
#2/17/21
#Project 1
#This file keeps track of all of our testing and game data
#It starts and ends the game and shows the stats of your games
import sys
import glob
import os
from datetime import datetime
if len(sys.argv)==1 or sys.argv[1]=="-help":
    print("testHarness.py wumpusCount arrowCount gameCountPerThread threadCount [fileName]")
    print("testHarness.py -parse [outFile]")
elif sys.argv[1]=="-parse":
    stillData = {"games":0,"wins":0,"deaths":0,"pit":0,"wum":0,"timeout":0,"avgTimePerGame":0}
    stillFiles = glob.glob("./automatedResults/Still/*.txt")
    numStill = len(stillFiles)
    moveData = {"games":0,"wins":0,"deaths":0,"pit":0,"wum":0,"timeout":0,"avgTimePerGame":0}
    moveFiles = glob.glob("./automatedResults/Moving/*.txt")
    numMove = len(moveFiles)

    for fle in stillFiles:
        f = open(fle,"r")
        lines = f.readlines()
        for line in lines:
            data = line[0:-1].split(":")
            stillData[data[0]]+=float(data[1])
        f.close()
    for fle in moveFiles:
        f = open(fle,"r")
        lines = f.readlines()
        for line in lines:
            data = line[0:-1].split(":")
            moveData[data[0]]+=float(data[1])
        f.close()
    outPrefix = "./automatedResults/"
    nme = datetime.now().strftime("results_%d%m%y_%H%M%S")
    outFile = nme+".txt"
    if(len(sys.argv)>2):
        outFile = sys.argv[2]
    f = open(outPrefix+outFile,"w")
    f.write("Still Data: "+ str(stillData)+"\n")
    f.write("Still Stats: win%:"+str(stillData["wins"]/float(stillData["games"]))+" death%:"+str(stillData["deaths"]/float(stillData["games"]))+" pit%:"+str(stillData["pit"]/float(stillData["games"]))+" wumpus%:"+str(stillData["wum"]/float(stillData["games"]))+" timeout%:"+str(stillData["timeout"]/float(stillData["games"]))+"\n")
    f.write("Average time per game:"+str(stillData["avgTimePerGame"]/float(numStill))+"\n")
    f.write("Move Data: "+ str(moveData)+"\n")
    f.write("Move Stats: win%:"+str(moveData["wins"]/float(moveData["games"]))+" death%:"+str(moveData["deaths"]/float(moveData["games"]))+" pit%:"+str(moveData["pit"]/float(moveData["games"]))+" wumpus%:"+str(moveData["wum"]/float(moveData["games"]))+" timeout%:"+str(moveData["timeout"]/float(moveData["games"]))+"\n")
    f.write("Deltas: win%:"+str((stillData["wins"]/float(stillData["games"]))-(moveData["wins"]/float(moveData["games"])))+" death%:"+str((stillData["deaths"]/float(stillData["games"]))-(moveData["deaths"]/float(moveData["games"])))+" pit%"+str((stillData["pit"]/float(stillData["games"]))-(moveData["pit"]/float(moveData["games"])))+" wumpus%:"+str((stillData["wum"]/float(stillData["games"]))-(moveData["wum"]/float(moveData["games"])))+"\n")
    f.write("Average time per game:"+str(moveData["avgTimePerGame"]/float(numMove))+"\n")
    f.close()    

else:
    directory='./automatedResults/'
    os.chdir(directory)
    #files=glob.glob('*.txt')
    #for filename in files:
    #    os.unlink(filename)
    directory='./Moving/'
    os.chdir(directory)
    files=glob.glob('*.txt')
    for filename in files:
        os.unlink(filename)
    directory='../Still/'
    os.chdir(directory)
    files=glob.glob('*.txt')
    for filename in files:
        os.unlink(filename)
    os.chdir("../../")
    wum = int(sys.argv[1])
    arr = int(sys.argv[2])
    gms = int(sys.argv[3])
    thd = int(sys.argv[4])
    name = "testScript.bat"
    if(len(sys.argv)>5):
        name = sys.argv[5]
    f = open(name, "w")
    for i in range(thd):
        f.write("start python HuntTheWumpusAutomated.py "+"1 "+str(wum)+" "+str(arr)+" "+str(gms)+"\n")
    for i in range(thd):
        f.write("start python HuntTheWumpusAutomated.py "+"2 "+str(wum)+" "+str(arr)+" "+str(gms)+"\n")
    f.close()