import math
import cv2
import numpy as np
from scipy.optimize import curve_fit

#consts
areaThresh = 100
permThresh = 50
turnThresh = 10

#setting resolution related
cap = cv2.VideoCapture(0)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
centreW = width // 2
centreY = height // 2


#set threshold, use newThingy.py to get the HSV values
def setHSV():
    #(lowerTemp, upperTemp) = [53, 69, 44] , [89, 212, 255]
    (lowerTemp, upperTemp) = [69, 170, 15] , [92, 255, 255]
    #(lowerTemp, upperTemp) = [61, 201, 21] , [83, 255, 255]
    (lower, upper) = np.array(lowerTemp), np.array(upperTemp)
    return (lower,upper)

(lower_blue, upper_blue) = setHSV()

#the function format of parabolic vertex form to find centre of the hub
def regressionTarget(x, a, b, c):
	#return a * x + b * x**2 + c
     return a * (x-b) ** 2 + c
    #return a + math.sqrt(b ** 2 - (x - c) ** 2)


#finds the centre point of all the little tape
def getTapeCoord(cur_frame):
    frame = cur_frame
    tapeCoords = []
    tapeX = []
    tapeY = []
    #frame = cv2.imread(file)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for index, i in enumerate(contours):
        a, p, ind = (cv2.contourArea(i), cv2.arcLength(i, True), index)
    #     #print(a,p,ind)
        if a >= areaThresh and p >= permThresh:
            M = cv2.moments(i)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                cv2.drawContours(frame, [i], -1, (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 7, (0, 0, 255), -1)
                cv2.circle(frame, (0,0), 7, (0,0,255), -1)
                cv2.putText(frame, f"center {cx},{cy}",(cx,cy),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                tapeCoords.append((cx,cy))
                tapeX.append(cx)
                tapeY.append(-cy)
                # if cx  - turnThresh > centreW:
                #     print("Turn right")
                # elif cx + turnThresh < centreW:
                #     print("Turn Left")
                # else:
                #     print("Charge")
    return (tapeX, tapeY)

#finds the vertex with the list of x values with corresponding y values (in seperate list)
def findVertex(x, y):
    print(x,y)
    # curve fit
    popt, _ = curve_fit(regressionTarget, x, y)
    # summarize the parameter values
    a, b, c = popt
    #print('y = %.5f * x + %.5f * x^2 + %.5f' % (a, b, c))
    # print(f"{a} * (x-{b}) ** 2 + {c}")
    # print(f"{b},{c}")
    return (b,c)


#for testing purposes
def test():
    cur_frame = cv2.imread("FarLaunchpad6ft0in.png")
    verteX, verteY = getTapeCoord(cur_frame)
    cur_x, cur_y = findVertex(verteX, verteY)
    if cur_x - turnThresh > centreW:
        print("Turn Right")
    elif cur_x + turnThresh < centreW:
        print("Turn Left")
    else:
        print("Charge")

#takes a frame and gets required values
def getValue(frame):
    verteX, verteY = getTapeCoord(frame)
    cur_x, cur_y = findVertex(verteX, verteY)
    if cur_x - turnThresh > centreW:
        #print("Turn Right")
        direct = "R"
    elif cur_x + turnThresh < centreW:
        #print("Turn Left")
        direct = "L"
    else:
        #print("Charge")
        direct = "C"
    return {"x" : cur_x, "y" : cur_y, "dir" : direct}

#turns a dict into the nessacary netwrok table thing
def tableDealer(dealer, tableDict, tableTag):
    for key in tableDict:
        dealer(key, tableDict[key], tableTag)

#runs the loop on the pi
def piLoop():
    while cap.isOpened():
        thing, frame = cap.read()
        table = getValue(frame)
        #Once you have networktables, add dealer as a func that does the thing
        #tableDealer(table)

#print(findVertex(getTapeCoord(cur_frame)))
