#To do at the 1st run: Run arduino("SerialConnectionWithPython*.ino"), Set path, Set panel position(task 29)

# Put off: Take measures for USB-monitor disconnection, making of divided movie
# Plug-in which should be installed: OpenCV
# Tips of python: global variable can be read from function without statement, but cannot substitute (Caution: Mistaking local variable for global variable can be easily happened)
#m*: label, i*:iEntry, b*:button

#Ask which DNMS is work.

import cv2  # For camera capturing
import numpy as np
from tkinter import *   # For GUI
from tkinter import ttk
from tkinter import filedialog
#from PIL import Image, ImageFilter
import datetime # For getting time
import pickle   # Module for saving parameters
import os       # For the checking of folder/file
import smtplib  # For sending notification email
import serial   # Module for the operation of arduino
from email.mime.text import MIMEText
from email.utils import formatdate

#ser = serial.Serial('COM3',9600,timeout=0.01)
ser = serial.Serial('COM3',115200,timeout=0.1)
#===========For email sending==============================================================================
FROM_ADDRESS = 'smarthomecage@gmail.com'
MY_PASSWORD = '6789yuio6789YUIO'
TO_ADDRESS = 'bekkobati@gmail.com'
BCC = 'receiver2@test.net'
SUBJECT = 'Mail from python'
BODY = 'This mail was sent from python program'
#========Basical setting====================================================================================

MaxTaskNum = 100  # Max number of tasks
MaxPanelNum = 40
ULXofTouchWindow = 1166 # Left-up position of the touch panel window
CameraWindowWidth = 640
CameraWindowHeight = 480
TouchWindowWidth = 1366
TouchWindowHeight = 768
CharaMesX = 100
CharaMesY = 0
MainWindowRightFrameX = 100 # The X coordinate of upper left position of the GUI frame which shows task buttons
MainWindowRightFrameY = 30
NosePokeSamplingDensity=10 # Sampling density of nosepoke detection (pixel)
FPS=6
#===========================================================================================================
Phase = 0 # Current main phase
Phase2 = 0
Task = 0 # Number of current task
Path=''

MxCam = -1   # Mice cursor coordinate in the camera window
MyCam = -1
PreMxCam = -1   # Mice cursor coordinate of the previous frame in the camera window
PreMyCam = -1
MxTk = -1  # Mice cursor coordinate in the touch panel window
MyTk = -1
PreMxTk = -1  # Mice cursor coordinate of the previous frame in the touch panel window
PreMyTk = -1
CrossFireX = 100
CrossFireY = 100
CrossFireMoveDistance = 10.0  # Move distance by one button click
TouchPanelRef = [0]*MaxPanelNum
OHCnt=0 # Total frame of operant house update
EndFlag = 0   # If 1, program will be quit
TaskEndFlag = 0
SaveTrg = 0
PickleInst = [0] * MaxTaskNum
IsHousingAnalysis=0 # If housing analysis is working, the value = 1
IsConventionalAnalysis=0 # If non-housing analysis is working, the value = 1
TouchDetectionOn=0 # If any mouse cursor is detected, the value = 1
TouchSymbolCnt = 0
# Nosepoke ROI
NosePokeRoiWidth=0  # Width of nosepoke ROI
NosePokeRoiHeight=0
Position = [[0 for i in range(2)] for j in range(2)]

Distance=0
RoiMovePhase=0
GrabbedID=0
NowPunishing = 0
WaitExposureAdjustCnt = 0
NosePokeIntTh=50
NosePokeHitNumTh=0


Year = 0
Month = 0
Day = 0
Hour = 0
Minute = 0
Second = 0.0
TaskStartYear = 0
TaskStartMonth = 0
TaskStartDay = 0
TaskStartHour = 0
TaskStartMinute = 0
TaskStartSecond = 0.0

TimerRunning=[0]*2
TimerNowTime=[0.0]*2
TimerPreTime=[0.0]*2
TimerCounter=[0]*2
TimerSec=[0]*2


Init = 0
FpsSec = 0
FpsPreSec = 0
ButtonRef = [0]*100
ButtonRef[1] = 2
FrameNum = 0
FPS = 0.0
FrameNumPerSec = 0
CurrentPanelNum = 0

IndicatedWaterPos=0     # Indicate position of water nozzle, 0:intermediate, 1:inside, 2:outside, -1:power off the servo(for silencing)
IndicatedRoofLightPower=1   # If this value is 1, roof light is turned on. If -1, turned off. If 0, do nothing.
RoofLightPowerOn=0      # When 1, roof light is lit. When 0, light-out.
IndicatedInfraredPower=0# If this value is 1, infrared light is turned on. If -1, turned off. If 0, do nothing.
InfraredPowerOn=0       #
IndicatedWaterCue=0     # If this value is 1, water cue light(Green LED) is turned on. If -1, turned off. If 0, do nothing.
WaterCueOn=0            # When 1, water cue is lit. When 0, water cue is out.

IndicatedValveTtlPower=0# If this value is 1, TTL of electric valve onsets. If -1, offsets. If 0, do nothing.
ValveTtlPowerOn=0

IndicatedHoleCue=[0]*5 # If this value is 1, hole cue light is turned on. If -1, turned off. If 0, do nothing (Element numbers correspond to the hole IDs).
HoleCueOn=[0]*5
IndicatedHoleWaterCue=[0]*5 # If this value is 1, hole reward cue light is turned on. If -1, turned off. If 0, do nothing (Element numbers correspond to the hole IDs).
HoleWaterCueOn=[0]*5

WaterPos=0
WaterCue=0
NosePoking=0    # When the nosepoke is detected, this value is 1
DuringTask=0    # Only during task, this value is 1
NowRecording=0  # During recording, this value is 1
EndRecordTimerOn=0  # If 1, end record timer is functional
EndRecordTimerCnt=0 # When this counter equals 0, the recording is stopped
ManualNosePokeOn=-1    #If manual nose poke is activated, 1
NosePokeDetectionOn=1  #If 1, nose poke detection is functional
NowLickRecording=0  #
StartLickRecordingTrg=0 # If 1, recording of lick starts
EndLickRecordingTrg=0   # If 1, recording of lick ends
PreNosePoking=0
NosePokeNum=0

SendingTtl=0                # If 1, TTL output is started
TtlPower=0                  # If 1, TTL signal is sent
TtlSquareOn=0				#if this value is 1, channel 3 becomes enable
TtlITV=2000					#Frequency of TTL pulse (msec)
Ttl1stSquareDuration=1000	#Width of 1st TTL square pulse(msec)
TtlSquareDuration=100		#Width of the following TTL square pulse(msec)
ElapsedTime=0				#Elapsed time after starting ttl pulse output (msec)
ElapsedTimePerFrame=0		#Elapsed time in the current frame(msec)
TtlPreTime=0				#sec*1000+ms, For caluculation
TtlCurrTime=0				#sec*1000+ms, For caluculation
TtlPreQuotient=0			#For caluculation
TtlCurrQuotient=0			#For caluculation
TtlCurrRemainder = 0		#For caluculation
TtlSquareElapsedTime=0		#For caluculation
TtlIsFirst=1				#This value is 1 until 1st long-wide pulse is output
NextShatterTime=0.0
CaptureNum=0

SerialOutPhase = 0
CurrentChannelID=0

#TouchedPanelID=-0   # ID of touched panel

# Make main window
MainWindowRoot = Tk()
MainWindowRoot.title("Main window")
MainWindowRoot.geometry('+5+5')
MainWindowRoot.geometry("1200x200")
MainWindowLeftFrame = ttk.Frame(MainWindowRoot, width=500, height=500, relief='flat', borderwidth=5)
MainWindowLeftFrame.place(x=0, y=0)
MainWindowRightFrame = ttk.Frame(MainWindowRoot, width=1200, height=500, relief='flat', borderwidth=5)
MainWindowRightFrame.place(x=100, y=30, )

# Make control window
ControlWindowRoot = Tk()
ControlWindowRoot.title("Control window")
ControlWindowRoot.geometry('+5+300')
ControlWindowFrame = ttk.Frame(ControlWindowRoot, width=600, height=480, relief='flat', borderwidth=5)
ControlWindowFrame.grid(row=0, column=0, sticky=(N, E, S, W))   # Make frame?

# Make Touch window
TouchWindowRoot = Tk()
TouchWindowRoot.title("Touch window")
TouchWindowRoot.geometry(str(TouchWindowWidth)+"x"+str(TouchWindowHeight))    # Create Touch window
TouchWindowRoot.geometry('+'+str(ULXofTouchWindow)+'+0')    # Move window
CanvasTouchWindow = Canvas(TouchWindowRoot, width = TouchWindowWidth, height = TouchWindowHeight)
CanvasTouchWindow.create_rectangle(0, 0, TouchWindowWidth+1, TouchWindowHeight+1, fill = 'black')  # Draw dark background
CanvasTouchWindow.place(x=-2, y=-2)


class mouseParam:   # Class for get input information of mouse (in the Open CV window)
    def __init__(self, input_img_name):
        self.mouseEvent = {"x": None, "y": None, "event": None, "flags": None}  # マウス入力用のパラメータ
        cv2.setMouseCallback(input_img_name, self.__CallBackFunc, None) # マウス入力の設定
    def __CallBackFunc(self, eventType, x, y, flags, userdata): # コールバック関数
        self.mouseEvent["x"] = x
        self.mouseEvent["y"] = y
        self.mouseEvent["event"] = eventType
        self.mouseEvent["flags"] = flags
    def getData(self):  # マウス入力用のパラメータを返すための関数
        return self.mouseEvent
    def getEvent(self): # マウスイベントを返す関数
        return self.mouseEvent["event"]
    def getFlags(self): # マウスフラグを返す関数
        return self.mouseEvent["flags"]
    def getX(self): # xの座標を返す関数
        return self.mouseEvent["x"]
    def getY(self): # yの座標を返す関数
        return self.mouseEvent["y"]
    def getPos(self):   # xとyの座標を返す関数
        return (self.mouseEvent["x"], self.mouseEvent["y"])

def SaveGeneralParameter():
    global Path, PanelULX, PanelULY, PanelBRX, PanelBRY
    with open('data/Path.dat', 'wb') as fp:
        pickle.dump(Path, fp)
    with open('data/LightTh.dat', 'wb') as fp:
        pickle.dump(LightThVar.get(), fp)
    with open('data/DarkTh.dat', 'wb') as fp:
        pickle.dump(DarkThVar.get(), fp)
    with open('data/NumTh.dat', 'wb') as fp:
        pickle.dump(NumThVar.get(), fp)
    with open('data/InAngle.dat', 'wb') as fp:
        pickle.dump(InAngleVar.get(), fp)
    with open('data/MidAngle.dat', 'wb') as fp:
        pickle.dump(MidAngleVar.get(), fp)
    with open('data/OutAngle.dat', 'wb') as fp:
        pickle.dump(OutAngleVar.get(), fp)
    with open('data/TouchXAdjust.dat', 'wb') as fp:
        pickle.dump(TouchXAdjustVar.get(), fp)
    with open('data/TouchYAdjust.dat', 'wb') as fp:
        pickle.dump(TouchYAdjustVar.get(), fp)

    with open('data/PanelULX.dat', 'wb') as fp:
        pickle.dump(PanelULX, fp)
    with open('data/PanelULY.dat', 'wb') as fp:
        pickle.dump(PanelULY, fp)
    with open('data/PanelBRX.dat', 'wb') as fp:
        pickle.dump(PanelBRX, fp)
    with open('data/PanelBRY.dat', 'wb') as fp:
        pickle.dump(PanelBRY, fp)
    return
def Start(): # Accept task parameters
    global Phase, Init, IsHousingAnalysis, IsConventionalAnalysis, SaveTrg  # Global variant outside this define
    RemoveMainRightWidget()
    Init = 0
    IsHousingAnalysis=1
    IsConventionalAnalysis=0
    SaveTrg = 1
    Phase += 1
    return
def StartNow(): # Manual task starting
    global Phase,Init, IsHousingAnalysis, IsConventionalAnalysis, TaskStartYear, TaskStartMonth, TaskStartDay, TaskStartHour, TaskStartMinute, TaskStartSecond, SaveTrg
    RemoveMainRightWidget()
    Init = 0
    IsHousingAnalysis = 0
    IsConventionalAnalysis = 1
    TaskStartYear = TimeNow.year
    TaskStartMonth = TimeNow.month
    TaskStartDay = TimeNow.day
    TaskStartHour = TimeNow.hour
    TaskStartMinute = TimeNow.minute
    TaskStartSecond = TimeNow.second + TimeNow.microsecond
    SaveTrg=1
    Phase += 2
    return
def StartLickRecording():
    global StartLickRecordingTrg
    StartLickRecordingTrg = 1
    return
def EndLickRecording():
    global EndLickRecordingTrg
    EndLickRecordingTrg = 1
    return
def Back(): # Back to task selection
    global Phase, Init
    RemoveMainRightWidget()
    PutTaskButton()
    Init = 0
    Phase = -1
    return
def SaveTrgOn():
    global SaveTrg
    SaveTrg=1
    SaveGeneralParameter()
    return
def BackToPara():   # Back to parameter input
    global Phase,Init
    RemoveMainRightWidget()
    Init = 0
    Phase -= 1
    return
def EndTaskNow():
    global Init, Phase2
    #Init = 0
    Phase2=-1
    return
def EndFlagOn():
    global EndFlag
    EndFlag = 1
    return
def donothing():
    return
def SelectPathForSaving():
    global Path
    Path=filedialog.askdirectory(initialdir = dir)
    PathForSaving.set(Path)
    SaveGeneralParameter()
    return
def PutTaskButton():
    ButtonWidth = 13
    bTask1 = ttk.Button(MainWindowRightFrame, text='Acclimation(1)', command=Task1, width=ButtonWidth).grid(row=0, column=0)
    bTask2 = ttk.Button(MainWindowRightFrame, text='TouchLit(2)', command=Task2, width=ButtonWidth).grid(row=0, column=1)
    bTask4 = ttk.Button(MainWindowRightFrame, text='TouchLit(4)', command=Task4, width=ButtonWidth).grid(row=0, column=2)
    bTask6 = ttk.Button(MainWindowRightFrame, text='PatternSep(6)', command=Task6, width=ButtonWidth).grid(row=0, column=3)
    bTask17 = ttk.Button(MainWindowRightFrame, text='DAT(17)', command=Task17, width=ButtonWidth).grid(row=0, column=4)
    bTask22 = ttk.Button(MainWindowRightFrame, text='DNMS(22)', command=Task22, width=ButtonWidth).grid(row=0, column=5)
    bTask23 = ttk.Button(MainWindowRightFrame, text='DNMS(23)', command=Task23, width=ButtonWidth).grid(row=0, column=6)
    bTask26 = ttk.Button(MainWindowRightFrame, text='Persev(26)', command=Task26, width=ButtonWidth).grid(row=0, column=7)
    bTask27 = ttk.Button(MainWindowRightFrame, text='PersevB1(27)', command=Task27, width=ButtonWidth).grid(row=0, column=8)
    bTask28 = ttk.Button(MainWindowRightFrame, text='Allo/Ago(28)', command=Task28, width=ButtonWidth).grid(row=0, column=9)
    bTask29 = ttk.Button(MainWindowRightFrame, text='Go/NoGo(29)', command=Task29, width=ButtonWidth).grid(row=1, column=0)
    bTask30 = ttk.Button(MainWindowRightFrame, text='Go/NoGo2(30)', command=Task30, width=ButtonWidth).grid(row=1, column=1)
    bTask31 = ttk.Button(MainWindowRightFrame, text='Timing(31)', command=Task31, width=ButtonWidth).grid(row=1, column=2)

    return
def PutAllPanel():  # Show all panels on the monitor
    for i in range(0, MaxPanelNum):
        ULX = PanelULX[Task][i]
        ULY = PanelULY[Task][i]
        BRX = PanelBRX[Task][i]
        BRY = PanelBRY[Task][i]
        if ULX!=0 or ULY!=0 or BRX!=0 or BRY!=0:
            TouchPanelRef[i] = CanvasTouchWindow.create_rectangle(ULX, ULY, BRX, BRY, fill='white')  # Draw current panel
    return
def PutStartBackButton():   # Put start and back button
    bStart = ttk.Button(MainWindowRightFrame, text='Start', command=Start).grid(row=0, column=0)
    bStartNow = ttk.Button(MainWindowRightFrame, text='Start now', command=StartNow).grid(row=1, column=0)
    bAdjustPanel = ttk.Button(MainWindowRightFrame, text='AdjustPanel', command=SetPanel).grid(row=2, column=0)
    bBack = ttk.Button(MainWindowRightFrame, text='Back', command=Back).grid(row=3, column=0)
    return
def PutPreTaskButton():
    bStartNow = ttk.Button(MainWindowRightFrame, text='StartNow', command=StartNow).grid(row=1, column=10)
    bTimePlus = ttk.Button(MainWindowRightFrame, text='Time+', command=Back).grid(row=2, column=10)
    bTimeMinus = ttk.Button(MainWindowRightFrame, text='Time.', command=Back).grid(row=3, column=10)
    bBackToPara = ttk.Button(MainWindowRightFrame, text='Back', command=BackToPara).grid(row=4, column=10)
def PutEndTaskNowButton():
    bEndTaskNow = ttk.Button(MainWindowRightFrame, text='EndTaskNow', command=EndTaskNow).grid(row=0, column=0)
    return
def RemoveMainRightWidget(): # Destroy all task buttons
    global MainWindowRightFrame
    ChildWidget = MainWindowRightFrame.winfo_children()
    for ChildWidget in ChildWidget:
        ChildWidget.destroy()
    return
def MoveCrossFireUp():  # For panel position setting
    global CrossFireY
    CanvasTouchWindow.move(HorizontalLine, 0.0, -CrossFireMoveDistance)
    #VerticalLine.place(x=10, y=10)
    #CrossFireY-=1
    return
def MoveCrossFireRight():   # For panel position setting
    global CrossFireX
    CanvasTouchWindow.move(VerticalLine, CrossFireMoveDistance, 0.0)
    #CrossFireX+=1
    return
def MoveCrossFireLeft():  # For panel position setting
    global CrossFireX
    CanvasTouchWindow.move(VerticalLine, -CrossFireMoveDistance, 0.0)
    #CrossFireX-=1
    return
def MoveCrossFireDown():  # For panel position setting
    global CrossFireY
    CanvasTouchWindow.move(HorizontalLine, 0.0, CrossFireMoveDistance)
    #CrossFireY+=1
    return
def CoarseMode():  # For panel position setting
    global CrossFireMoveDistance
    CrossFireMoveDistance += 10.0
    if CrossFireMoveDistance > 50.0:
        CrossFireMoveDistance = 50.0
    return
def FineMode():  # For panel position setting
    global CrossFireMoveDistance
    CrossFireMoveDistance -= 10.0
    if CrossFireMoveDistance < 2.0:
        CrossFireMoveDistance = 2.0
    return
def SetPanelPos(): # Go to the next panel position setting
    global Phase, Init, Task, CurrentPanelNum, PanelULX, PanelULY, VerticalLine, HorizontalLine, TouchPanelRef
    Trg=0
    if Phase == 0: # If set button is pushed during setting of upper left position of the touch panel
        WedgetPos = CanvasTouchWindow.coords(VerticalLine)  # Get position of vertical line
        PanelULX[Task][CurrentPanelNum] = WedgetPos[0]  # Get y axis value of the vertical line
        WedgetPos = CanvasTouchWindow.coords(HorizontalLine)
        PanelULY[Task][CurrentPanelNum] = WedgetPos[1]
        NextX = PanelBRX[Task][CurrentPanelNum]
        NextY = PanelBRY[Task][CurrentPanelNum]
        if  NextX==0 and NextY==0:  # If the values are default
            NextX = PanelULX[Task][CurrentPanelNum]+100
            NextY = PanelULY[Task][CurrentPanelNum]+250
        CanvasTouchWindow.coords(VerticalLine, NextX, 0, NextX, TouchWindowHeight)  # Move vertical line of the cross fire
        CanvasTouchWindow.coords(HorizontalLine, 0, NextY, TouchWindowWidth, NextY)
        SaveGeneralParameter()
        Phase += 1
        Init=0
        Trg = 1
    if Phase == 1 and Trg==0:  # If set button is pushed during setting of bottom right position of the touch panel
        WedgetPos = CanvasTouchWindow.coords(VerticalLine)
        PanelBRX[Task][CurrentPanelNum] = WedgetPos[0]
        WedgetPos = CanvasTouchWindow.coords(HorizontalLine)
        PanelBRY[Task][CurrentPanelNum] = WedgetPos[1]
        PosULX = PanelULX[Task][CurrentPanelNum]
        PosULY = PanelULY[Task][CurrentPanelNum]
        PosBRX= PanelBRX[Task][CurrentPanelNum]
        PosBRY = PanelBRY[Task][CurrentPanelNum]
        TouchPanelRef[CurrentPanelNum] = CanvasTouchWindow.create_rectangle(PosULX, PosULY, PosBRX, PosBRY, fill='white')  # Draw current panel

        SaveGeneralParameter()
        Phase += 1
        Init = 0
        Trg = 1
    if Phase == 2 and Trg==0:  # Continue panel setting
        CurrentPanelNum+=1
        Phase=0
        Init = 0
    return
def BackPanelPos(): # Back to the previous panel position setting
    return
def EndPanelSetting():  # Finish panel position setting
    global Phase
    Phase=-1    # Make flag to finish panel position setting loop
    return

def SetPanel(): # Contain main roop during panel position setting
    global Phase, Init, CurrentPanelNum, CrossFireX, CrossFireY, VerticalLine, HorizontalLine
    VerticalLine = CanvasTouchWindow.create_line(100, 0, 100, 1200, fill='blue', tags="Panel")  # Make vertical line of the cross fire
    HorizontalLine = CanvasTouchWindow.create_line(0, 500, 1200, 500, fill='red', tags="Panel")  # Make horizontal line of the cross fire
    Init=0
    CurrentPanelNum=0
    Phase=0
    while EndFlag == 0:
        OperantHouseUpdate()
        if Phase == 0 or Phase == 1:    # Move crossfire to indicate panel coordinates
            if Init == 0:
                RemoveMainRightWidget()
                MainWindowRightFrame.place(x=MainWindowRightFrameX, y=MainWindowRightFrameY, anchor="nw", width=1200, height=500)
                #mStepDistance = ttk.Label(MainWindowRightFrame, text='Step: ' + str(CrossFireMoveDistance) + ' pixel').place(x=200, y=30)
                if Phase == 0:
                    PosX = PanelULX[Task][CurrentPanelNum]
                    PosY = PanelULX[Task][CurrentPanelNum]
                    if PosX == 0 and  PosY == 0:
                        PosX = TouchWindowWidth / 2
                        PosY = TouchWindowHeight / 2
                    CanvasTouchWindow.coords(VerticalLine, PosX, 0, PosX, TouchWindowHeight)    # Move vertical line of the cross fire
                    CanvasTouchWindow.coords(HorizontalLine, 0, PosY, TouchWindowWidth, PosY)   # Move horizontal line of the cross fire
                    mCharaMessage = ttk.Label(MainWindowRightFrame, text='Set left upper coordinate of the panel #'+str(CurrentPanelNum)+'.').place(x=CharaMesX, y=CharaMesY)
                if Phase == 1:
                    mCharaMessage = ttk.Label(MainWindowRightFrame, text='Set right bottom coordinate of the panel #' + str(CurrentPanelNum) + '.').place(x=CharaMesX, y=CharaMesY)
                bMoveUp = ttk.Button(MainWindowRightFrame, text='Up', command=MoveCrossFireUp).place(x=43, y=60)
                bMoveLeft = ttk.Button(MainWindowRightFrame, text='Left', command=MoveCrossFireLeft).place(x=0, y=85)
                bMoveRight = ttk.Button(MainWindowRightFrame, text='Right', command=MoveCrossFireRight).place(x=86, y=85)
                bMoveDown = ttk.Button(MainWindowRightFrame, text='Down', command=MoveCrossFireDown).place(x=43, y=110)
                bCoarseMode = ttk.Button(MainWindowRightFrame, text='Coarse', command=CoarseMode).place(x=200, y=60)
                bFineMode = ttk.Button(MainWindowRightFrame, text='FineMode', command=FineMode).place(x=200, y=85)
                bSet = ttk.Button(MainWindowRightFrame, text='Set', command=SetPanelPos).place(x=200, y=110)

                Init=1
        if Phase == 2:
            if Init == 0:
                RemoveMainRightWidget()
                mCharaMessage = ttk.Label(MainWindowRightFrame, text='Do you want to set the coordinates of the next panel?').place(x=CharaMesX, y=CharaMesY)
                bSetNextPanelYes = ttk.Button(MainWindowRightFrame, text='Yes', command=SetPanelPos).place(x=0, y=60)
                bSetNextPanelNo = ttk.Button(MainWindowRightFrame, text='No', command=EndPanelSetting).place(x=86, y=60)
                Init = 1
        if Phase == -1:
            RemoveMainRightWidget()
            CanvasTouchWindow.delete(VerticalLine)
            CanvasTouchWindow.delete(HorizontalLine)

            for i in range(0, MaxPanelNum):
                if TouchPanelRef[i]:
                    CanvasTouchWindow.delete(TouchPanelRef[i])
                if i > CurrentPanelNum:
                    PanelULX[Task][i] = 0
                    PanelULY[Task][i] = 0
                    PanelBRX[Task][i] = 0
                    PanelBRY[Task][i] = 0

            PutTaskButton()
            Phase = 0
            break
    return

def WaterPosInside():
    global IndicatedWaterPos
    IndicatedWaterPos=1
    return
def WaterPosMiddle():
    global IndicatedWaterPos
    IndicatedWaterPos=0
    return
def WaterPosOutside():
    global IndicatedWaterPos
    IndicatedWaterPos=2
    return

def RoofLightTurnOn():
    global IndicatedRoofLightPower
    IndicatedRoofLightPower=1
    return
def RoofLightTurnOff():
    global IndicatedRoofLightPower
    IndicatedRoofLightPower=-1
    return
def InfraredTurnOn():
    global IndicatedInfraredPower
    IndicatedInfraredPower=1
    return
def InfraredTurnOff():
    global IndicatedInfraredPower
    IndicatedInfraredPower=-1
    return
def WaterCueTurnOn():
    global IndicatedWaterCue
    IndicatedWaterCue=1
    return
def WaterCueTurnOff():
    global IndicatedWaterCue
    IndicatedWaterCue=-1
    return
def ValveTtlTurnOn():
    global IndicatedValveTtlPower
    IndicatedValveTtlPower=1
    return
def ValveTtlTurnOff():
    global IndicatedValveTtlPower
    IndicatedValveTtlPower=-1
    return
def HoleCueTurnOn(Num):
    global IndicatedHoleCue
    IndicatedHoleCue[Num]=1
    return
def HoleCueTurnOff(Num):
    global IndicatedHoleCue
    IndicatedHoleCue[Num]=-1
    return
def HoleWaterCueTurnOn(Num):
    global IndicatedHoleWaterCue
    IndicatedHoleWaterCue[Num]=1
    return
def HoleWaterCueTurnOff(Num):
    global IndicatedHoleWaterCue
    IndicatedHoleWaterCue[Num]=-1
    return


def Task1():
    global Phase, Init, Task
    Init=0
    while EndFlag == 0:
        OperantHouseUpdate()
        if Phase == -1: # Task end process
            Phase = 0
            Task = 0
            break
        if Phase == 0:    # Parameter inputs
            if Init == 0:
                RemoveMainRightWidget()
                PutStartBackButton()
                mSpace = ttk.Label(MainWindowRightFrame, text=' ').grid(row=0, column=1)
                mNumOfDay = ttk.Label(MainWindowRightFrame, text='NumOfDay')
                mNumOfDay.grid(row=0, column=2, sticky=W)
                NumOfDay = StringVar()
                iNumOfDay = ttk.Entry(MainWindowRightFrame, textvariable=NumOfDay)
                iNumOfDay.grid(row=1, column=2)
                mNextTask = ttk.Label(MainWindowRightFrame, text='NextTask')
                mNextTask.grid(row=0, column=3, sticky=W)
                NextTask = StringVar()
                iNextTask = ttk.Entry(MainWindowRightFrame, textvariable=NextTask)
                iNextTask.grid(row=1, column=3)
                Init=1
        if Phase == 1:    # Wait for starting of task
            if Init == 0:
                PutPreTaskButton()
                Init = 1
        if Phase == 2:    # During task
            if Init == 0:
                PutEndTaskNowButton()
                Init = 1
    return

def Task2():
    global Phase, Task
    Phase = 0
    Task=2
    return
def Task4():
    global Phase, Task
    Phase = 0
    Task = 4
    return
def Task6():
    global Phase, Task
    Phase = 0
    Task = 6
    return
def Task17():
    global Phase, Task
    Phase = 0
    Task = 17
    return
def Task22():
    global Phase, Task
    Phase = 0
    Task = 22
    return
def Task23():
    global Phase, Task
    Phase = 0
    Task = 23
    return
def Task26():
    global Phase, Task
    Phase = 0
    Task = 26
    return
def Task27():
    global Phase, Task
    Phase = 0
    Task = 27
    return
def Task28():
    global Phase, Task
    Phase = 0
    Task = 28
    return
def Task29():   # Go-NoGo task
    global Phase, Phase2, Init, Task, SaveTrg, LoadTrg, TaskStartYear, TaskStartMonth, TaskStartDay, TaskStartHour, TaskStartMinute, TaskStartSecond,PanelULX, PanelULY, PanelBRX, PanelBRY, Year, Month, Day, Hour, Minute, Second, NosePoking, DuringTask, NowRecording

    Task = 29
    Init = 0
    while EndFlag == 0:
        OperantHouseUpdate()

        if Phase == -1:  # Back to the task select phase
            Phase = 0
            Task = 0
            break
        if Phase == 0:  # Parameter inputs
            if Init == 0:
                LoadTrg = 1
                # Make GUI for the setting of the parameters for this task
                RemoveMainRightWidget() # Remove task buttons

                PutStartBackButton()    # Put start/back buttons
                mSpace = ttk.Label(MainWindowRightFrame, text=' ').grid(row=0, column=1)  # Used just as spacer

                mMaxCorrectNum = ttk.Label(MainWindowRightFrame, text='MaxCorrectNum').grid(row=0, column=2, sticky=W)    # Put label
                MaxCorrectNumVar = IntVar()  # Declare variable receiving value from the entry field
                iMaxCorrectNum = ttk.Entry(MainWindowRightFrame, textvariable=MaxCorrectNumVar).grid(row=1, column=2) # Place entry field

                mPresentDur = ttk.Label(MainWindowRightFrame, text='PresentDur(s)').grid(row=0, column=3, sticky=W)
                PresentDurVar = IntVar()
                iPresentDur = ttk.Entry(MainWindowRightFrame, textvariable=PresentDurVar).grid(row=1, column=3)

                mPunishDur = ttk.Label(MainWindowRightFrame, text='PunishDurDur(s)').grid(row=0, column=4, sticky=W)
                PunishDurVar = IntVar()
                iPunishDur = ttk.Entry(MainWindowRightFrame, textvariable=PunishDurVar).grid(row=1, column=4)

                mIti = ttk.Label(MainWindowRightFrame, text='ITI(s)').grid(row=0, column=5, sticky=W)
                ItiVar = IntVar()
                iIti = ttk.Entry(MainWindowRightFrame, textvariable=ItiVar).grid(row=1, column=5)

                mLickDur = ttk.Label(MainWindowRightFrame, text='LickDur(s)').grid(row=0, column=6, sticky=W)
                LickDurVar = IntVar()
                iLickDur = ttk.Entry(MainWindowRightFrame, textvariable=LickDurVar).grid(row=1, column=6)

                mNextTaskTh = ttk.Label(MainWindowRightFrame, text='NextTaskTh(Correct%)').grid(row=0, column=7, sticky=W)
                NextTaskThVar = IntVar()
                iNextTaskTh = ttk.Entry(MainWindowRightFrame, textvariable=NextTaskThVar).grid(row=1, column=7)

                mNextTask = ttk.Label(MainWindowRightFrame, text='NextTask').grid(row=2, column=2, sticky=W)
                NextTaskVar = IntVar()
                iNextTask = ttk.Entry(MainWindowRightFrame, textvariable=NextTaskVar).grid(row=3, column=2)

                mTaskType = ttk.Label(MainWindowRightFrame, text='TaskType').grid(row=2, column=3, sticky=W)    # Put label
                TaskTypeVar = StringVar(MainWindowRightFrame)  # Declare variable receiving value from the entry field
                tTaskType = OptionMenu(MainWindowRightFrame, TaskTypeVar, "Go", "NoGo").grid(row=3, column=3) # Place drop-down list

                mPunishLight = ttk.Label(MainWindowRightFrame, text='PunishLight').grid(row=2, column=4, sticky=W)
                PunishLightVar = StringVar(MainWindowRightFrame)
                tPunishLight = OptionMenu(MainWindowRightFrame, PunishLightVar, "ON", "OFF").grid(row=3, column=4)

                mPanelType = ttk.Label(MainWindowRightFrame, text='PanelType').grid(row=2, column=5, sticky=W)
                PanelTypeVar = StringVar(MainWindowRightFrame)
                tPanelType = OptionMenu(MainWindowRightFrame, PanelTypeVar, "Normal", "Blink").grid(row=3, column=5)

                mWaterCueType = ttk.Label(MainWindowRightFrame, text='WaterCueType').grid(row=2, column=6, sticky=W)
                WaterCueTypeVar = StringVar(MainWindowRightFrame)
                tWaterCueType = OptionMenu(MainWindowRightFrame, WaterCueTypeVar, "Normal", "Blink").grid(row=3, column=6)

                Init = 1

        if LoadTrg == 1:  # If load trigger is on

            Str = "ParametersForTask" + str(Task)
            if os.path.exists(Str+'/MaxCorrectNum.dat') == True:  # If save file exists
                with open(Str+'/MaxCorrectNum.dat', 'rb') as PickleInst[Task]:
                    MaxCorrectNumVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                MaxCorrectNumVar.set(80)     # Default value

            if os.path.exists(Str+'/PresentDur.dat') == True:  # If save file exists
                with open(Str+'/PresentDur.dat', 'rb') as PickleInst[Task]:
                    PresentDurVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                PresentDurVar.set(1)     # Default value

            if os.path.exists(Str+'/PunishDur.dat') == True:  # If save file exists
                with open(Str+'/PunishDur.dat', 'rb') as PickleInst[Task]:
                    PunishDurVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                PunishDurVar.set(1)     # Default value

            if os.path.exists(Str+'/Iti.dat') == True:  # If save file exists
                with open(Str+'/Iti.dat', 'rb') as PickleInst[Task]:
                    ItiVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                ItiVar.set(1)     # Default value
            if os.path.exists(Str+'/LickDur.dat') == True:  # If save file exists
                with open(Str+'/LickDur.dat', 'rb') as PickleInst[Task]:
                    LickDurVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                LickDurVar.set(1)     # Default value
            if os.path.exists(Str+'/NextTaskTh.dat') == True:  # If save file exists
                with open(Str+'/NextTaskTh.dat', 'rb') as PickleInst[Task]:
                    NextTaskThVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                NextTaskThVar.set(1)     # Default value
            if os.path.exists(Str+'/NextTask.dat') == True:  # If save file exists
                with open(Str+'/NextTask.dat', 'rb') as PickleInst[Task]:
                    NextTaskVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                NextTaskVar.set(1)     # Default value
            if os.path.exists(Str+'/TaskType.dat') == True:  # If save file exists
                with open(Str+'/TaskType.dat', 'rb') as PickleInst[Task]:
                    TaskTypeVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                TaskTypeVar.set('Go')     # Default value
            if os.path.exists(Str+'/PunishLight.dat') == True:  # If save file exists
                with open(Str+'/PunishLight.dat', 'rb') as PickleInst[Task]:
                    PunishLightVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                PunishLightVar.set('ON')     # Default value

            if os.path.exists(Str+'/PanelType.dat') == True:  # If save file exists
                with open(Str+'/PanelType.dat', 'rb') as PickleInst[Task]:
                    PanelTypeVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                PanelTypeVar.set('Normal')     # Default value

            if os.path.exists(Str+'/WaterCueType.dat') == True:  # If save file exists
                with open(Str+'/WaterCueType.dat', 'rb') as PickleInst[Task]:
                    WaterCueTypeVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                WaterCueTypeVar.set('Normal')     # Default value
            LoadTrg = 0

        if SaveTrg == 1:    # If save trigger is on
            # Parameters of each task are saved into different folder
            Str="ParametersForTask"+str(Task)   # Path to the folder for saving of parameters
            if os.path.exists(Str) == False:    # If folder for saving parameters is not exist
                os.mkdir(Str)   # Make folder for saving
            with open(Str+'/MaxCorrectNum.dat', 'wb') as PickleInst[Task]:
                pickle.dump(MaxCorrectNumVar.get(),PickleInst[Task])     # Save
            with open(Str+'/PresentDur.dat', 'wb') as PickleInst[Task]:
                pickle.dump(PresentDurVar.get(), PickleInst[Task])     # Save
            with open(Str+'/PunishDur.dat', 'wb') as PickleInst[Task]:
                pickle.dump(PunishDurVar.get(), PickleInst[Task])     # Save
            with open(Str+'/Iti.dat', 'wb') as PickleInst[Task]:
                pickle.dump(ItiVar.get(), PickleInst[Task])     # Save
            with open(Str+'/LickDur.dat', 'wb') as PickleInst[Task]:
                pickle.dump(LickDurVar.get(), PickleInst[Task])     # Save
            with open(Str+'/NextTaskTh.dat', 'wb') as PickleInst[Task]:
                pickle.dump(NextTaskThVar.get(), PickleInst[Task])     # Save
            with open(Str + '/NextTask.dat', 'wb') as PickleInst[Task]:
                pickle.dump(NextTaskVar.get(), PickleInst[Task])  # Save
            with open(Str+'/TaskType.dat', 'wb') as PickleInst[Task]:
                pickle.dump(TaskTypeVar.get(), PickleInst[Task])     # Save
            with open(Str+'/PunishLight.dat', 'wb') as PickleInst[Task]:
                pickle.dump(PunishLightVar.get(), PickleInst[Task])     # Save
            with open(Str+'/PanelType.dat', 'wb') as PickleInst[Task]:
                pickle.dump(PanelTypeVar.get(), PickleInst[Task])     # Save
            with open(Str+'/WaterCueType.dat', 'wb') as PickleInst[Task]:
                pickle.dump(WaterCueTypeVar.get(), PickleInst[Task])     # Save
            SaveTrg = 0


        if Phase == 1:  # Wait for starting of task
            if Init == 0:
                PutPreTaskButton()
                Str = 'Go/NoGo task (' + str(Task) + ')    Start time ' + str(TaskStartMonth) + '/' + str(TaskStartDay) + ' ' + str(TaskStartHour) + ':' + str(TaskStartMinute) + '    Waiting...'
                Init = 1

        if Phase == 2:  # During task
            if Init == 0: # Initialization of the task
                PutEndTaskNowButton()
                Str='Go/NoGo task ('+str(Task)+')    Start time '+str(TaskStartMonth)+'/'+str(TaskStartDay)+' '+str(TaskStartHour)+':'+str(TaskStartMinute)+'    Running'
                mSpace = ttk.Label(MainWindowRightFrame, text='    ').grid(row=0, column=1)  # Used just as spacer
                mStatus = ttk.Label(MainWindowRightFrame, text=Str).grid(row=0, column=2, sticky=E)

                # Convert StringVars of parameters into integer or normal string to use in the following
                MaxCorrectNum=int(MaxCorrectNumVar.get())
                PresentDur = int(PresentDurVar.get())
                PunishDur = int(PunishDurVar.get())
                Iti = int(ItiVar.get())
                LickDur = int(LickDurVar.get())
                NextTaskTh = int(NextTaskThVar.get())
                NextTask = int(NextTaskVar.get())
                TaskType = TaskTypeVar.get()
                PunishLight = PunishLightVar.get()
                PanelType = PanelTypeVar.get()
                WaterCueType = WaterCueTypeVar.get()

                # Declar local variables for this task
                TrialNum=0
                TotalCorrectNum=0
                TotalIncorrectNum=0
                CorrectRate=0
                Writer_TouchEventTxt = open(Path + "/" + str(Year) + "_" + str(Month) + "_" + str(Day) + " " + str(Hour) + "h" + str(Minute) + "m Task" + str(Task) + " CorrectRate" + str(CorrectRate) + " Touch.txt", 'w')  # Initialize the text exporter
                Writer_TouchEventCsv = open(Path + "/" + str(Year) + "_" + str(Month) + "_" + str(Day) + " " + str(Hour) + "h" + str(Minute) + "m Task" + str(Task) + " CorrectRate" + str(CorrectRate) + " Touch.csv", 'w')  # Initialize the text exporter
                StartLickRecording()

                DuringTask = 1
                DoneCorrectResponse = 1
                RoofLightTurnOff()
                InfraredTurnOn()
                WaterCueTurnOn()
                WaterPosInside()
                NowDrinking = 0
                NowPunishing = 0
                TotalCorrectNum = 0
                TotalIncorrectNum = 0
                AutoWaterSupplyNum = 0
                StartRecording()    # Start camera capturing and sending of TTL

                Writer_TouchEventTxt.write('TrialNum\tResult\t\t\tyyyy/mm/dd\th:m\ts\n')  # Write item name
                TrialNum=0
                TtlStart()
                Phase2 = 2
                Init = 1

            if Phase2 == 0:   # Initiation of new trial
                DoneCorrectResponse=0
                Panel = CanvasTouchWindow.create_rectangle(PanelULX[Task][0], PanelULY[Task][0], PanelBRX[Task][0], PanelBRY[Task][0], fill='white')  # Draw panel
                #CanvasTouchWindow.create_rectangle(0, 0, 100,1000, fill='white')  # Draw panel
                TrialNum += 1
                Timer_Start(0)  # Start the latency timer
                Phase2 += 1
            if Phase2 == 1:   # Panel presentation
                Trg = 0
                TouchedPanelID = DetectPanelTouch() # Examine which panel is touched (return panel ID. If none of the panels touched, return -1)
                TouchSymbolCnt = 30
                if (TaskType == 'Go' and TouchedPanelID!=-1) or (TaskType=='NoGo' and TimerSec[0] >= PresentDur): # If mouse responses correctly
                    DoneCorrectResponse = 1
                    WaterPosInside()    # Move water nozzle to the inside position
                    WaterCueTurnOn()
                    NowDrinking = 0
                    TotalCorrectNum += 1      # Increase the number of correct response
                    if TaskType == 'Go':
                        Writer_TouchEventTxt.write(str(TrialNum)+'\tPanelTouched(Correct)\t'+str(Year)+"/"+str(Month)+"/"+str(Day)+"\t"+str(Hour)+":"+str(Minute)+"\t"+str(TimeNow.second)+"."+str(TimeNow.microsecond)+"\n") # Write the response on the text file
                        Writer_TouchEventCsv.write(str(TrialNum) + ',PanelTouched(Correct),' + str(Year) + "," + str(Month) + "," + str(Day) + "," + str(Hour) + "," + str(Minute) + "," + str(TimeNow.second) + "," + str(TimeNow.microsecond))  # Write the response on the csv file
                    if TaskType == 'NoGo':
                        Writer_TouchEventTxt.write(str(TrialNum)+'\tPanelIgnored(Correct)\t'+str(Year)+"/"+str(Month)+"/"+str(Day)+"\t"+str(Hour)+":"+str(Minute)+"\t"+str(TimeNow.second)+"."+str(TimeNow.microsecond)+"\n") # Write the response on the text file
                        Writer_TouchEventTxt.write(str(TrialNum) + ',PanelIgnored(Correct),' + str(Year) + "," + str(Month) + "," + str(Day) + "," + str(Hour) + "," + str(Minute) + "," + str(TimeNow.second) + "," + str(TimeNow.microsecond))  # Write the response on the csv file
                    CanvasTouchWindow.delete(Panel)
                    Timer_End(0)
                    Phase2 = 2  # Start reward phase
                if (TaskType == 'NoGo' and TouchedPanelID!=-1) or (TaskType =='Go' and TimerSec[0] >= PresentDur):  # If mouse responses incorrectly
                    NowPunishing = 1
                    WaterPosOutside()
                    if PunishLight =='ON':
                        RoofLightTurnOn()   # Turn on roof light
                    TotalIncorrectNum += 1
                    if TaskType == 'Go':
                        Writer_TouchEventTxt.write(str(TrialNum) + '\tPanelIgnored(Wrong)\t' + str(Year) + "/" + str(Month) + "/" + str(Day) + "\t" + str(Hour) + ":" + str(Minute) + "\t" + str(TimeNow.second) + "." + str(TimeNow.microsecond)+"\n")  # Write the response on the text file
                        Writer_TouchEventCsv.write(str(TrialNum) + ',PanelIgnored(Wrong),' + str(Year) + "," + str(Month) + "," + str(Day) + "," + str(Hour) + "," + str(Minute) + "," + str(TimeNow.second) + "," + str(TimeNow.microsecond))  # Write the response on the csv file
                    if TaskType == 'NoGo':
                        Writer_TouchEventTxt.write(str(TrialNum) + '\tPanelTouched(Wrong)\t' + str(Year) + "/" + str(Month) + "/" + str(Day) + "\t" + str(Hour) + ":" + str(Minute) + "\t" + str(TimeNow.second) + "." + str(TimeNow.microsecond))  # Write the response on the text file
                        Writer_TouchEventTxt.write(str(TrialNum) + ',PanelTouched(Wrong),' + str(Year) + "," + str(Month) + "," + str(Day) + "," + str(Hour) + "," + str(Minute) + "," + str(TimeNow.second) + "," + str(TimeNow.microsecond))  # Write the response on the csv file
                    CanvasTouchWindow.delete(Panel)
                    Timer_End(0)    # End timer1
                    Timer_Start(0)  # Start punish timer
                    Phase2 = 5 # Start punishment phase
            if Phase2 == 2:  # Reward phase
                if WaterCueType == 'Blink':
                    if TimeNow.microsecond/100%2 == 0:
                        WaterCueTurnOff()
                    if TimeNow.microsecond/100%2 == 1:
                        WaterCueTurnOn()
                if NosePoking == 1 and NowDrinking == 0:    # If the mouse initiates nose poke
                    NowDrinking = 1
                    Timer_Start(0)  # Start lick timer
                if NowDrinking == 1:
                    if DoneCorrectResponse == 1 and TimerSec[0] >= LickDur:   # If lick time exceed the designated time
                        Timer_End(0) # End lick timer
                        WaterPosMiddle()    # Move water nozzle to the intermediate position
                        WaterCueTurnOff()
                        NowDrinking = 0
                        Timer_Start(0)  # Start ITI timer
                        Phase2 = 3
            if Phase2 == 3:   # ITI
                if TimerSec[0] >= Iti:  # If ITI is passed
                    Timer_End(0)
                    Phase2 = 0  # Go to the next trial
                if TotalCorrectNum >= MaxCorrectNum:
                    Phase2=-1 # Go to the task finish phase
            if Phase2 == 5:   # Punishment phase
                if TimerSec[0] >= PunishDur:    # If punishment time is passed
                    RoofLightTurnOff()
                    NowPunishing = 0
                    WaterPosMiddle()    # Move water nozzle to the intermediate position
                    Timer_End(0)  # End punishment timer1
                    Timer_Start(0)  # Start ITI timer
                    Phase2 = 3
            if Phase2 == -1:  # Task finish phase
                DuringTask = 0
                WaterPosMiddle()
                #if Panel!=null:
                if 'Panel' in locals():
                    CanvasTouchWindow.delete(Panel)
                InfraredTurnOff()
                NowPunishing = 0
                if NowRecording == 1:
                    SetEndRecordingTimer(60)
                if TotalCorrectNum > 0 or TotalIncorrectNum > 0:
                    CorrectRate = int(TotalCorrectNum * 100.0 / (TotalCorrectNum + TotalIncorrectNum))
                    Writer_TouchEventTxt.write('TotalNum:'+str(TotalCorrectNum+TotalIncorrectNum)+'  Correct num:'+str(TotalCorrectNum)+'  Incorrect num:'+str(TotalIncorrectNum)+'  Correct rate'+str(CorrectRate)+'%'+"\n")	#結果テキストの一番最後に成績のまとめを記入
                Writer_TouchEventTxt.write('MaxCorrectNum: '+str(MaxCorrectNum)+"\n")
                Writer_TouchEventTxt.write('PresentDur: ' + str(PresentDur)+"\n")
                Writer_TouchEventTxt.write('PunishDur: ' + str(PunishDur)+"\n")
                Writer_TouchEventTxt.write('Iti: ' + str(Iti)+"\n")
                Writer_TouchEventTxt.write('LickDur: ' + str(LickDur)+"\n")
                Writer_TouchEventTxt.write('NextTaskTh: ' + str(NextTaskTh)+"\n")
                Writer_TouchEventTxt.write('NextTask: ' + str(NextTask)+"\n")
                Writer_TouchEventTxt.write('TaskType: ' + str(TaskType)+"\n")
                Writer_TouchEventTxt.write('PunishLight: ' + str(PunishLight)+"\n")
                Writer_TouchEventTxt.write('PanelType: ' + str(PanelType)+"\n")
                Writer_TouchEventTxt.write('WaterCueType: ' + str(WaterCueType)+"\n")
                Writer_TouchEventTxt.close()
                Writer_TouchEventCsv.close()
                EndLickRecording()
                if CorrectRate >= NextTaskTh:
                    Task = NextTask
                SendEmail()
                TtlDelayStop()

                Phase2 = 0
                if IsHousingAnalysis == 1:
                    Phase = 1  # Go back to the task-waiting phase

                if IsConventionalAnalysis == 1:
                    RoofLightTurnOn()
                    Phase = 0  # Go back to the task parameter setting
                    Init = 0
    return

def Task30():   # Go-NoGo task without touch monitor
    global Phase, Phase2, Init, Task, SaveTrg, LoadTrg, TaskStartYear, TaskStartMonth, TaskStartDay, TaskStartHour, TaskStartMinute, TaskStartSecond, PanelULX, PanelULY, PanelBRX, PanelBRY, Year, Month, Day, Hour, Minute, Second, NosePoking, DuringTask, NowRecording

    Task = 30
    Init = 0
    while EndFlag == 0:
        OperantHouseUpdate()

        if Phase == -1:  # Back to the task select phase
            Phase = 0
            Task = 0
            break
        if Phase == 0:  # Parameter inputs
            if Init == 0:
                LoadTrg = 1
                # Make GUI for the setting of the parameters for this task
                RemoveMainRightWidget()  # Remove task buttons

                PutStartBackButton()  # Put start/back buttons
                mSpace = ttk.Label(MainWindowRightFrame, text=' ').grid(row=0, column=1)  # Used just as spacer

                mMaxCorrectNum = ttk.Label(MainWindowRightFrame, text='MaxCorrectNum').grid(row=0, column=2, sticky=W)  # Put label
                MaxCorrectNumVar = IntVar()  # Declare variable receiving value from the entry field
                iMaxCorrectNum = ttk.Entry(MainWindowRightFrame, textvariable=MaxCorrectNumVar).grid(row=1, column=2)  # Place entry field

                mPresentDur = ttk.Label(MainWindowRightFrame, text='PresentDur(s)').grid(row=0, column=3, sticky=W)
                PresentDurVar = IntVar()
                iPresentDur = ttk.Entry(MainWindowRightFrame, textvariable=PresentDurVar).grid(row=1, column=3)

                mPunishDur = ttk.Label(MainWindowRightFrame, text='PunishDurDur(s)').grid(row=0, column=4, sticky=W)
                PunishDurVar = IntVar()
                iPunishDur = ttk.Entry(MainWindowRightFrame, textvariable=PunishDurVar).grid(row=1, column=4)

                mIti = ttk.Label(MainWindowRightFrame, text='ITI(s)').grid(row=0, column=5, sticky=W)
                ItiVar = IntVar()
                iIti = ttk.Entry(MainWindowRightFrame, textvariable=ItiVar).grid(row=1, column=5)

                mLickDur = ttk.Label(MainWindowRightFrame, text='LickDur(s)').grid(row=0, column=6, sticky=W)
                LickDurVar = IntVar()
                iLickDur = ttk.Entry(MainWindowRightFrame, textvariable=LickDurVar).grid(row=1, column=6)

                mNextTaskTh = ttk.Label(MainWindowRightFrame, text='NextTaskTh(Correct%)').grid(row=0, column=7, sticky=W)
                NextTaskThVar = IntVar()
                iNextTaskTh = ttk.Entry(MainWindowRightFrame, textvariable=NextTaskThVar).grid(row=1, column=7)

                mNextTask = ttk.Label(MainWindowRightFrame, text='NextTask').grid(row=2, column=2, sticky=W)
                NextTaskVar = IntVar()
                iNextTask = ttk.Entry(MainWindowRightFrame, textvariable=NextTaskVar).grid(row=3, column=2)

                mTaskType = ttk.Label(MainWindowRightFrame, text='TaskType').grid(row=2, column=3, sticky=W)  # Put label
                TaskTypeVar = StringVar(MainWindowRightFrame)  # Declare variable receiving value from the entry field
                tTaskType = OptionMenu(MainWindowRightFrame, TaskTypeVar, "Go", "NoGo").grid(row=3, column=3)  # Place drop-down list

                mPunishLight = ttk.Label(MainWindowRightFrame, text='PunishLight').grid(row=2, column=4, sticky=W)
                PunishLightVar = StringVar(MainWindowRightFrame)
                tPunishLight = OptionMenu(MainWindowRightFrame, PunishLightVar, "ON", "OFF").grid(row=3, column=4)

                mPanelType = ttk.Label(MainWindowRightFrame, text='PanelType').grid(row=2, column=5, sticky=W)
                PanelTypeVar = StringVar(MainWindowRightFrame)
                tPanelType = OptionMenu(MainWindowRightFrame, PanelTypeVar, "Normal", "Blink").grid(row=3, column=5)

                mWaterCueType = ttk.Label(MainWindowRightFrame, text='WaterCueType').grid(row=2, column=6, sticky=W)
                WaterCueTypeVar = StringVar(MainWindowRightFrame)
                tWaterCueType = OptionMenu(MainWindowRightFrame, WaterCueTypeVar, "Normal", "Blink").grid(row=3, column=6)

                Init = 1

        if LoadTrg == 1:  # If load trigger is on

            Str = "ParametersForTask" + str(Task)
            if os.path.exists(Str + '/MaxCorrectNum.dat') == True:  # If save file exists
                with open(Str + '/MaxCorrectNum.dat', 'rb') as PickleInst[Task]:
                    MaxCorrectNumVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                MaxCorrectNumVar.set(80)  # Default value

            if os.path.exists(Str + '/PresentDur.dat') == True:  # If save file exists
                with open(Str + '/PresentDur.dat', 'rb') as PickleInst[Task]:
                    PresentDurVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                PresentDurVar.set(1)  # Default value

            if os.path.exists(Str + '/PunishDur.dat') == True:  # If save file exists
                with open(Str + '/PunishDur.dat', 'rb') as PickleInst[Task]:
                    PunishDurVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                PunishDurVar.set(1)  # Default value

            if os.path.exists(Str + '/Iti.dat') == True:  # If save file exists
                with open(Str + '/Iti.dat', 'rb') as PickleInst[Task]:
                    ItiVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                ItiVar.set(1)  # Default value
            if os.path.exists(Str + '/LickDur.dat') == True:  # If save file exists
                with open(Str + '/LickDur.dat', 'rb') as PickleInst[Task]:
                    LickDurVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                LickDurVar.set(1)  # Default value
            if os.path.exists(Str + '/NextTaskTh.dat') == True:  # If save file exists
                with open(Str + '/NextTaskTh.dat', 'rb') as PickleInst[Task]:
                    NextTaskThVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                NextTaskThVar.set(1)  # Default value
            if os.path.exists(Str + '/NextTask.dat') == True:  # If save file exists
                with open(Str + '/NextTask.dat', 'rb') as PickleInst[Task]:
                    NextTaskVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                NextTaskVar.set(1)  # Default value
            if os.path.exists(Str + '/TaskType.dat') == True:  # If save file exists
                with open(Str + '/TaskType.dat', 'rb') as PickleInst[Task]:
                    TaskTypeVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                TaskTypeVar.set('Go')  # Default value
            if os.path.exists(Str + '/PunishLight.dat') == True:  # If save file exists
                with open(Str + '/PunishLight.dat', 'rb') as PickleInst[Task]:
                    PunishLightVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                PunishLightVar.set('ON')  # Default value

            if os.path.exists(Str + '/PanelType.dat') == True:  # If save file exists
                with open(Str + '/PanelType.dat', 'rb') as PickleInst[Task]:
                    PanelTypeVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                PanelTypeVar.set('Normal')  # Default value

            if os.path.exists(Str + '/WaterCueType.dat') == True:  # If save file exists
                with open(Str + '/WaterCueType.dat', 'rb') as PickleInst[Task]:
                    WaterCueTypeVar.set(pickle.load(PickleInst[Task]))  # Load
            else:
                WaterCueTypeVar.set('Normal')  # Default value
            LoadTrg = 0

        if SaveTrg == 1:  # If save trigger is on
            # Parameters of each task are saved into different folder
            Str = "ParametersForTask" + str(Task)  # Path to the folder for saving of parameters
            if os.path.exists(Str) == False:  # If folder for saving parameters is not exist
                os.mkdir(Str)  # Make folder for saving
            with open(Str + '/MaxCorrectNum.dat', 'wb') as PickleInst[Task]:
                pickle.dump(MaxCorrectNumVar.get(), PickleInst[Task])  # Save
            with open(Str + '/PresentDur.dat', 'wb') as PickleInst[Task]:
                pickle.dump(PresentDurVar.get(), PickleInst[Task])  # Save
            with open(Str + '/PunishDur.dat', 'wb') as PickleInst[Task]:
                pickle.dump(PunishDurVar.get(), PickleInst[Task])  # Save
            with open(Str + '/Iti.dat', 'wb') as PickleInst[Task]:
                pickle.dump(ItiVar.get(), PickleInst[Task])  # Save
            with open(Str + '/LickDur.dat', 'wb') as PickleInst[Task]:
                pickle.dump(LickDurVar.get(), PickleInst[Task])  # Save
            with open(Str + '/NextTaskTh.dat', 'wb') as PickleInst[Task]:
                pickle.dump(NextTaskThVar.get(), PickleInst[Task])  # Save
            with open(Str + '/NextTask.dat', 'wb') as PickleInst[Task]:
                pickle.dump(NextTaskVar.get(), PickleInst[Task])  # Save
            with open(Str + '/TaskType.dat', 'wb') as PickleInst[Task]:
                pickle.dump(TaskTypeVar.get(), PickleInst[Task])  # Save
            with open(Str + '/PunishLight.dat', 'wb') as PickleInst[Task]:
                pickle.dump(PunishLightVar.get(), PickleInst[Task])  # Save
            with open(Str + '/PanelType.dat', 'wb') as PickleInst[Task]:
                pickle.dump(PanelTypeVar.get(), PickleInst[Task])  # Save
            with open(Str + '/WaterCueType.dat', 'wb') as PickleInst[Task]:
                pickle.dump(WaterCueTypeVar.get(), PickleInst[Task])  # Save
            SaveTrg = 0

        if Phase == 1:  # Wait for starting of task
            if Init == 0:
                PutPreTaskButton()
                Str = 'Go/NoGo task (' + str(Task) + ')    Start time ' + str(TaskStartMonth) + '/' + str(TaskStartDay) + ' ' + str(TaskStartHour) + ':' + str(TaskStartMinute) + '    Waiting...'
                Init = 1

        if Phase == 2:  # During task
            if Init == 0:  # Initialization of the task
                PutEndTaskNowButton()
                Str = 'Go/NoGo task (' + str(Task) + ')    Start time ' + str(TaskStartMonth) + '/' + str(TaskStartDay) + ' ' + str(TaskStartHour) + ':' + str(TaskStartMinute) + '    Running'
                mSpace = ttk.Label(MainWindowRightFrame, text='    ').grid(row=0, column=1)  # Used just as spacer
                mStatus = ttk.Label(MainWindowRightFrame, text=Str).grid(row=0, column=2, sticky=E)

                # Convert StringVars of parameters into integer or normal string to use in the following
                MaxCorrectNum = int(MaxCorrectNumVar.get())
                PresentDur = int(PresentDurVar.get())
                PunishDur = int(PunishDurVar.get())
                Iti = int(ItiVar.get())
                LickDur = int(LickDurVar.get())
                NextTaskTh = int(NextTaskThVar.get())
                NextTask = int(NextTaskVar.get())
                TaskType = TaskTypeVar.get()
                PunishLight = PunishLightVar.get()
                PanelType = PanelTypeVar.get()
                WaterCueType = WaterCueTypeVar.get()

                # Declar local variables for this task
                TrialNum = 0
                TotalCorrectNum = 0
                TotalIncorrectNum = 0
                CorrectRate = 0
                Writer_TouchEventTxt = open(
                    Path + "/" + str(Year) + "_" + str(Month) + "_" + str(Day) + " " + str(Hour) + "h" + str(Minute) + "m Task" + str(Task) + " CorrectRate" + str(CorrectRate) + " Touch.txt",
                    'w')  # Initialize the text exporter
                Writer_TouchEventCsv = open(
                    Path + "/" + str(Year) + "_" + str(Month) + "_" + str(Day) + " " + str(Hour) + "h" + str(Minute) + "m Task" + str(Task) + " CorrectRate" + str(CorrectRate) + " Touch.csv",
                    'w')  # Initialize the text exporter
                StartLickRecording()

                DuringTask = 1
                DoneCorrectResponse = 1
                RoofLightTurnOff()
                InfraredTurnOn()
                HoleWaterCueTurnOn(0)
                #WaterPosInside()
                NowDrinking = 0
                NowPunishing = 0
                TotalCorrectNum = 0
                TotalIncorrectNum = 0
                AutoWaterSupplyNum = 0
                StartRecording()  # Start camera capturing and sending of TTL

                Writer_TouchEventTxt.write('TrialNum\tResult\t\t\tyyyy/mm/dd\th:m\ts\n')  # Write item name
                TrialNum = 0
                TtlStart()

                NowDrinking = 1
                Timer_Start(0)  # Start lick timer
                Phase2 = 2
                Init = 1

            if Phase2 == 0:  # Initiation of new trial
                DoneCorrectResponse = 0
                HoleCueTurnOn(0)    # Onset hole cue
                #Panel = CanvasTouchWindow.create_rectangle(PanelULX[Task][0], PanelULY[Task][0], PanelBRX[Task][0], PanelBRY[Task][0], fill='white')  # Draw panel
                # CanvasTouchWindow.create_rectangle(0, 0, 100,1000, fill='white')  # Draw panel
                TrialNum += 1
                Timer_Start(0)  # Start the latency timer
                Phase2 += 1
            if Phase2 == 1:  # Panel presentation
                TouchedPanelID = DetectHoleTouch(0)  # Examine which panel is touched (return panel ID. If none of the panels touched, return -1)
                Trg = 0
                if PanelType == 'Blink':
                    if TimeNow.microsecond // 100 % 2 == 0:
                        HoleCueTurnOff(0)
                    if TimeNow.microsecond // 100 % 2 == 1:
                        HoleCueTurnOn(0)
                TouchSymbolCnt = 30
                if (TaskType == 'Go' and TouchedPanelID != -1) or (TaskType == 'NoGo' and TimerSec[0] >= PresentDur):  # If mouse responses correctly
                    print("z")
                    DoneCorrectResponse = 1
                    #WaterPosInside()  # Move water nozzle to the inside position
                    HoleWaterCueTurnOn(0)
                    ValveTtlTurnOn()
                    NowDrinking = 0
                    TotalCorrectNum += 1  # Increase the number of correct response
                    if TaskType == 'Go':
                        Writer_TouchEventTxt.write(
                            str(TrialNum) + '\tPanelTouched(Correct)\t' + str(Year) + "/" + str(Month) + "/" + str(Day) + "\t" + str(Hour) + ":" + str(Minute) + "\t" + str(TimeNow.second) + "." + str(
                                TimeNow.microsecond) + "\n")  # Write the response on the text file
                        Writer_TouchEventCsv.write(
                            str(TrialNum) + ',PanelTouched(Correct),' + str(Year) + "," + str(Month) + "," + str(Day) + "," + str(Hour) + "," + str(Minute) + "," + str(TimeNow.second) + "," + str(
                                TimeNow.microsecond))  # Write the response on the csv file
                    if TaskType == 'NoGo':
                        Writer_TouchEventTxt.write(
                            str(TrialNum) + '\tPanelIgnored(Correct)\t' + str(Year) + "/" + str(Month) + "/" + str(Day) + "\t" + str(Hour) + ":" + str(Minute) + "\t" + str(TimeNow.second) + "." + str(
                                TimeNow.microsecond) + "\n")  # Write the response on the text file
                        Writer_TouchEventTxt.write(
                            str(TrialNum) + ',PanelIgnored(Correct),' + str(Year) + "," + str(Month) + "," + str(Day) + "," + str(Hour) + "," + str(Minute) + "," + str(TimeNow.second) + "," + str(
                                TimeNow.microsecond))  # Write the response on the csv file
                    HoleCueTurnOff(0)
                    Timer_End(0)

                    NowDrinking = 1
                    Timer_Start(0)  # Start lick timer
                    Phase2 = 2  # Start reward phase

                if (TaskType == 'NoGo' and TouchedPanelID != -1) or (TaskType == 'Go' and TimerSec[0] >= PresentDur):
                    #print("pun")
                    NowPunishing = 1
                    #WaterPosOutside()
                    if PunishLight == 'ON':
                        RoofLightTurnOn()  # Turn on roof light
                    TotalIncorrectNum += 1
                    if TaskType == 'Go':
                        Writer_TouchEventTxt.write(
                            str(TrialNum) + '\tPanelIgnored(Wrong)\t' + str(Year) + "/" + str(Month) + "/" + str(Day) + "\t" + str(Hour) + ":" + str(Minute) + "\t" + str(TimeNow.second) + "." + str(
                                TimeNow.microsecond) + "\n")  # Write the response on the text file
                        Writer_TouchEventCsv.write(
                            str(TrialNum) + ',PanelIgnored(Wrong),' + str(Year) + "," + str(Month) + "," + str(Day) + "," + str(Hour) + "," + str(Minute) + "," + str(TimeNow.second) + "," + str(
                                TimeNow.microsecond))  # Write the response on the csv file
                    if TaskType == 'NoGo':
                        Writer_TouchEventTxt.write(
                            str(TrialNum) + '\tPanelTouched(Wrong)\t' + str(Year) + "/" + str(Month) + "/" + str(Day) + "\t" + str(Hour) + ":" + str(Minute) + "\t" + str(TimeNow.second) + "." + str(
                                TimeNow.microsecond))  # Write the response on the text file
                        Writer_TouchEventTxt.write(
                            str(TrialNum) + ',PanelTouched(Wrong),' + str(Year) + "," + str(Month) + "," + str(Day) + "," + str(Hour) + "," + str(Minute) + "," + str(TimeNow.second) + "," + str(
                                TimeNow.microsecond))  # Write the response on the csv file
                    HoleCueTurnOff(0)
                    Timer_End(0)  # End timer1
                    Timer_Start(0)  # Start punish timer
                    Phase2 = 5  # Start punishment phase
            if Phase2 == 2:  # Reward phase
                if WaterCueType == 'Blink':
                    if TimeNow.microsecond // 100 % 2 == 0:
                        HoleWaterCueTurnOff(0)
                    if TimeNow.microsecond // 100 % 2 == 1:
                        HoleWaterCueTurnOn(0)
                #if NosePoking == 1 and NowDrinking == 0:  # If the mouse initiates nose poke

                if NowDrinking == 1:
                    if DoneCorrectResponse == 1 and TimerSec[0] >= LickDur:  # If lick time exceed the designated time
                        Timer_End(0)  # End lick timer
                        ValveTtlTurnOff()
                        #WaterPosMiddle()  # Move water nozzle to the intermediate position
                        HoleWaterCueTurnOff(0)
                        NowDrinking = 0
                        Timer_Start(0)  # Start ITI timer
                        Phase2 = 3
            if Phase2 == 3:  # ITI
                if TimerSec[0] >= Iti:  # If ITI is passed
                    Timer_End(0)
                    Phase2 = 0  # Go to the next trial
                if TotalCorrectNum >= MaxCorrectNum:
                    Phase2 = -1  # Go to the task finish phase
            if Phase2 == 5:  # Punishment phase
                if TimerSec[0] >= PunishDur:  # If punishment time is passed
                    RoofLightTurnOff()
                    NowPunishing = 0
                    #WaterPosMiddle()  # Move water nozzle to the intermediate position
                    Timer_End(0)  # End punishment timer1
                    Timer_Start(0)  # Start ITI timer
                    Phase2 = 3
            if Phase2 == -1:  # Task finish phase
                DuringTask = 0
                #WaterPosMiddle()
                # if Panel!=null:
                HoleCueTurnOff(0)
                InfraredTurnOff()
                NowPunishing = 0
                if NowRecording == 1:
                    SetEndRecordingTimer(60)
                if TotalCorrectNum > 0 or TotalIncorrectNum > 0:
                    CorrectRate = int(TotalCorrectNum * 100.0 / (TotalCorrectNum + TotalIncorrectNum))
                    Writer_TouchEventTxt.write(
                        'TotalNum:' + str(TotalCorrectNum + TotalIncorrectNum) + '  Correct num:' + str(TotalCorrectNum) + '  Incorrect num:' + str(TotalIncorrectNum) + '  Correct rate' + str(
                            CorrectRate) + '%' + "\n")  # Write the brief summary of the result
                Writer_TouchEventTxt.write('MaxCorrectNum: ' + str(MaxCorrectNum) + "\n")   # Write the parameters of the task in the result text
                Writer_TouchEventTxt.write('PresentDur: ' + str(PresentDur) + "\n")
                Writer_TouchEventTxt.write('PunishDur: ' + str(PunishDur) + "\n")
                Writer_TouchEventTxt.write('Iti: ' + str(Iti) + "\n")
                Writer_TouchEventTxt.write('LickDur: ' + str(LickDur) + "\n")
                Writer_TouchEventTxt.write('NextTaskTh: ' + str(NextTaskTh) + "\n")
                Writer_TouchEventTxt.write('NextTask: ' + str(NextTask) + "\n")
                Writer_TouchEventTxt.write('TaskType: ' + str(TaskType) + "\n")
                Writer_TouchEventTxt.write('PunishLight: ' + str(PunishLight) + "\n")
                Writer_TouchEventTxt.write('PanelType: ' + str(PanelType) + "\n")
                Writer_TouchEventTxt.write('WaterCueType: ' + str(WaterCueType) + "\n")
                Writer_TouchEventTxt.close()
                Writer_TouchEventCsv.close()
                EndLickRecording()
                if CorrectRate >= NextTaskTh:
                    Task = NextTask
                SendEmail()
                TtlDelayStop()

                Phase2 = 0
                if IsHousingAnalysis == 1:
                    Phase = 1  # Go back to the task-waiting phase

                if IsConventionalAnalysis == 1:
                    RoofLightTurnOn()
                    Phase = 0  # Go back to the task parameter setting
                    Init = 0
    return
def Task31():
    global Phase, Task
    Phase = 0
    Task = 31
    return

def StartRecording():   # Start camera caputring
    global NowRecording, NowTime, SendingTtl, ElapsedTime, ElapsedTimePerFrame, TtlPreTime, TtlCurrTime, TtlPreQuotient, TtlCurrQuotient, TtlCurrRemainder, TtlSquareElapsedTime, TtlCnt, TtlIsFirst, TtlPower, TtlSquareOn, Writer_TtlLogCsv
    if NowRecording==0:
        NowRecording = 1
        SendingTtl = 1
        ElapsedTime = 0
        ElapsedTimePerFrame = 0
        TtlPreTime = TimeNow.second * 1000 + (TimeNow.microsecond / 1000)
        TtlCurrTime = TimeNow.second * 1000 + (TimeNow.microsecond / 1000)
        TtlPreQuotient = 0
        TtlCurrQuotient = 0
        TtlCurrRemainder = 0
        TtlSquareElapsedTime = 0
        TtlCnt = 0
        TtlIsFirst = 1
        TtlPower = -1
        TtlSquareOn = 0
        Writer_TtlLogCsv = open(Path + "/" + str(Year) + "_" + str(Month) + "_" + str(Day) + " " + str(Hour) + "h" + str(Minute) + "m Task" + str(Task) + " TTL.csv", 'w')  # Initialize the text exporter
    return
def SetEndRecordingTimer(FrameNum): # Start a timer for stopping camera caputring
    global EndRecordTimerOn, EndRecordTimerCnt
    EndRecordTimerOn = 1
    EndRecordTimerCnt=FrameNum
    return
def EndRecording(): # Stop camera caputring
    global NowRecording, SendingTtl, Writer_TtlLogCsv
    if NowRecording==1:
        NowRecording = 0
        VideoWriter.release()
        Writer_TtlLogCsv.close()
        SendingTtl = 0
    return

def Timer_Start(i): # Start general propose timer
    global NowTime, TimerRunning, TimerCounter, TimerSec, TimerPreTime
    TimerRunning[i] = 1
    TimerCounter[i] = 0
    TimerSec[i] = 0
    TimerPreTime[i] = TimeNow.microsecond // 100000
    return
def Timer_End(i):   # End general propose timer
    global TimerRunning
    TimerRunning[i] = 0
    return

def DetectPanelTouch(): # Return number of the touch panel on the monitor
    global MxTk, MyTk, PanelULX, PanelULY, PanelBRX, PanelBRY, Task, TouchDetectionOn, MaxPanelNum
    TouchedPanelID = -1
    if TouchDetectionOn==1:
        for i in range(0, MaxPanelNum):
            if MxTk >= PanelULX[Task][i] and MyTk >= PanelULY[Task][i] and MxTk <= PanelBRX[Task][i] and MyTk <= PanelBRY[Task][i]:
                TouchedPanelID=i
                break
    TouchDetectionOn=0
    return TouchedPanelID

def DetectHoleTouch(Num):   # Return number of the infrared sensor of the hole
    Value=1000
    TouchedHoleID = -1
    if Num==0:
        ser.flushInput()  # Clear input buffer from arduino
        Value=int(ser.readline().decode("utf-8").strip('\n').strip('\r'))  # Read the input value of the infrared sensor (Work when combined with "Serial conection with python 4")
        #print(Value)
        if Value < 500:
            TouchedHoleID=0
            #print("detect")
        else:
            TouchedHoleID=-1
    return TouchedHoleID
def TtlStart():
    return
def TtlDelayStop():
    return
def MeasureDistance():  # general-purpose
    global Distance, Position
    Distance = (Position[0][0] - Position[1][0]) * (Position[0][0] - Position[1][0]) + (Position[0][1] - Position[1][1]) * (Position[0][1] - Position[1][1])
    return
def ToggleManualNosePoke(): # Function of the manual nosepoke button
    global ManualNosePokeOn
    ManualNosePokeOn *= -1
    return
def ToggleManualLedOn():    # Function of the LED test button
    global RoofLightPowerOn, InfraredPowerOn, WaterCueOn, ValveTtlPowerOn, HoleCueOn, HoleWaterCueOn
    Trg=0
    if RoofLightPowerOn==0:
        RoofLightPowerOn=1
        InfraredPowerOn=1
        WaterCueOn=1
        ValveTtlPowerOn=1
        HoleCueOn[0]=1
        HoleWaterCueOn[0]=1
        Trg=1
    if RoofLightPowerOn==1 and Trg==0:
        RoofLightPowerOn=0
        InfraredPowerOn=0
        WaterCueOn=0
        ValveTtlPowerOn=0
        HoleCueOn[0]=0
        HoleWaterCueOn[0]=0
    return
def motion(event):  # Get mouse coordinate in tkinter window
    global MxTk, MyTk, PreMxTk, PreMyTk, TouchDetectionOn, TouchSymbolCnt
    PreMxTk = MxTk
    PreMyTk = MyTk
    MxTk = event.x
    MyTk = event.y
    TouchDetectionOn=1
    TouchSymbolCnt = 30
def create_message(from_addr, to_addr, bcc_addrs, subject, body):   # For email
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Bcc'] = bcc_addrs
    msg['Date'] = formatdate()
    return msg
def send(from_addr, to_addrs, msg):  # For email
    smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.ehlo()
    smtpobj.login(FROM_ADDRESS, MY_PASSWORD)
    smtpobj.sendmail(from_addr, to_addrs, msg.as_string())
    smtpobj.close()
    return
def SendEmail():  # For email
    to_addr = TO_ADDRESS
    subject = SUBJECT
    body = BODY
    msg = create_message(FROM_ADDRESS, to_addr, BCC, subject, body)
    send(FROM_ADDRESS, to_addr, msg)
    return


# Summary of menu bar
# File-> SaveParameter
# Setting -> adjustPanelLoc, SetTaskSchedule,RecFPS,PlayFPS,encoder,SetEmail,resetPara, FreezeDetect, Blinder
# Manual -> startRecord, endRecord, ResetMicon, ResetCam
menubar = Menu(MainWindowRoot)
FileMenu = Menu(menubar, tearoff=0)
FileMenu.add_command(label="Save parameters", command=SaveTrgOn)
#FileMenu.add_command(label="Reset parameters", command=donothing)
#FileMenu.add_command(label="Exit", command=EndFlagOn)
menubar.add_cascade(label="File", menu=FileMenu)
SettingMenu = Menu(menubar, tearoff=0)
#SettingMenu.add_command(label="Adjust panel position", command=SetPanel)
#SettingMenu.add_command(label="Set task schedule", command=donothing)
#SettingMenu.add_command(label="Set video recording FPS", command=donothing)
#SettingMenu.add_command(label="Set video playback FPS", command=donothing)
#SettingMenu.add_command(label="Select encoder", command=donothing)
#SettingMenu.add_command(label="Set notification email", command=donothing)
#SettingMenu.add_command(label="Freeze detection mode", command=donothing)
#SettingMenu.add_command(label="Blinder mode", command=donothing)
menubar.add_cascade(label="Setting", menu=SettingMenu)
ManualMenue = Menu(menubar, tearoff=0)
#ManualMenue.add_command(label="Start record", command=donothing)
#ManualMenue.add_command(label="Stop record", command=donothing)
#ManualMenue.add_command(label="Reset microcomputer", command=donothing)
#ManualMenue.add_command(label="Reset camera", command=donothing)
menubar.add_cascade(label="Manual operation", menu=ManualMenue)
MainWindowRoot.config(menu=menubar)

# Make menu GUI
PathForSaving=StringVar()
PathForSaving.set(Path)
mPathForSaving = ttk.Label(MainWindowLeftFrame, textvariable=PathForSaving)
mPathForSaving.place(x=270, y=0)
mName = ttk.Label(MainWindowLeftFrame, text="Animal name:")
mName.place(x=0, y=0)
StrFPS = StringVar()
mFPS = ttk.Label(MainWindowLeftFrame, textvariable=StrFPS)
mFPS.place(x=0, y=150)
AnimalName = StringVar()
iAnimalName = ttk.Entry(MainWindowLeftFrame, textvariable=AnimalName)
iAnimalName.place(x=100, y=0)
bFolderPath = ttk.Button(MainWindowLeftFrame, text='Folder path', command=SelectPathForSaving)
bFolderPath.place(x=0, y=30)
bSaveTrgOn = ttk.Button(MainWindowLeftFrame, text='SavePara', command=SaveTrgOn)
bSaveTrgOn.place(x=0, y=55)
bExit = ttk.Button(MainWindowLeftFrame, text='Exit', command=EndFlagOn)
bExit.place(x=0, y=80)
PutTaskButton()

# Make Label
mLightTh = ttk.Label(ControlWindowFrame, text='LightTh:')
mLightTh.grid(row=1, column=1, sticky=E)
mDarkTh = ttk.Label(ControlWindowFrame, text='DarkTh:')
mDarkTh.grid(row=2, column=1, sticky=E)
mNumTh = ttk.Label(ControlWindowFrame, text='NumTh:')
mNumTh.grid(row=3, column=1, sticky=E)
mInAngle = ttk.Label(ControlWindowFrame, text='InAngle:')
mInAngle.grid(row=4, column=1, sticky=E)
mMidAngle = ttk.Label(ControlWindowFrame, text='MidAngle:')
mMidAngle.grid(row=5, column=1, sticky=E)
mOutAngle = ttk.Label(ControlWindowFrame, text='OutAngle:')
mOutAngle.grid(row=6, column=1, sticky=E)
mTouchXAdjust = ttk.Label(ControlWindowFrame, text='TouchX adjust:')
mTouchXAdjust.grid(row=7, column=1, sticky=E)
mTouchYAdjust = ttk.Label(ControlWindowFrame, text='TouchY adjust:')
mTouchYAdjust.grid(row=8, column=1, sticky=E)
# Make Input
LightThVar = IntVar(ControlWindowRoot)
iLightTh = ttk.Entry(ControlWindowFrame, textvariable=LightThVar, width=5)
iLightTh.grid(row=1, column=2, sticky=W)
DarkThVar = IntVar(ControlWindowRoot)
iDarkTh = ttk.Entry(ControlWindowFrame, textvariable=DarkThVar, width=5)
iDarkTh.grid(row=2, column=2, sticky=W)
NumThVar = IntVar(ControlWindowRoot)
iNumTh = ttk.Entry(ControlWindowFrame, textvariable=NumThVar, width=5)
iNumTh.grid(row=3, column=2, sticky=W)
InAngleVar = IntVar(ControlWindowRoot)
iInAngle = ttk.Entry(ControlWindowFrame, textvariable=InAngleVar, width=5)
iInAngle.grid(row=4, column=2, sticky=W)
MidAngleVar = IntVar(ControlWindowRoot)
iMidAngle = ttk.Entry(ControlWindowFrame, textvariable=MidAngleVar, width=5)
iMidAngle.grid(row=5, column=2, sticky=W)
OutAngleVar = IntVar(ControlWindowRoot)
iOutAngle = ttk.Entry(ControlWindowFrame, textvariable=OutAngleVar, width=5)
iOutAngle.grid(row=6, column=2, sticky=W)
TouchXAdjustVar = IntVar(ControlWindowRoot)
iTouchXAdjust = ttk.Entry(ControlWindowFrame, textvariable=TouchXAdjustVar, width=5)
iTouchXAdjust.grid(row=7, column=2, sticky=W)
TouchYAdjustVar = IntVar(ControlWindowRoot)
iTouchYAdjust = ttk.Entry(ControlWindowFrame, textvariable=TouchYAdjustVar, width=5)
iTouchYAdjust.grid(row=8, column=2, sticky=W)

# Make Button

bInAngle = ttk.Button(ControlWindowFrame, text='InAngle', command=WaterPosInside)
bInAngle.grid(row=9, column=1, sticky=W)
bMidAngle = ttk.Button(ControlWindowFrame, text='MidAngle', command=WaterPosMiddle)
bMidAngle.grid(row=10, column=1, sticky=W)
bOutAngle = ttk.Button(ControlWindowFrame, text='OutAngle', command=WaterPosOutside)
bOutAngle.grid(row=11, column=1, sticky=W)
bLed = ttk.Button(ControlWindowFrame, text='LED', command=ToggleManualLedOn)
bLed.grid(row=12, column=1, sticky=W)
bLedBlink = ttk.Button(ControlWindowFrame, text='LED(blink)', command=Start)
bLedBlink.grid(row=13, column=1, sticky=W)
bManualNosePoke = ttk.Button(ControlWindowFrame, text='ManualNosePoke', command=ToggleManualNosePoke)
bManualNosePoke.grid(row=13, column=1, sticky=W)

VideoCapture = cv2.VideoCapture(0, cv2.CAP_DSHOW)       #Make video capture
cv2.namedWindow("CameraWindow")                     #Make video window
cv2.moveWindow("CameraWindow", 250, 300)
mouseData = mouseParam("CameraWindow") # Instantiate class for get mouse cursor coordinates of camera window

fourcc = cv2.VideoWriter_fourcc(*'MJPG')    #Define the codec and create VideoWriter object
VideoWriter = cv2.VideoWriter("CapturedImage .avi",fourcc, 20.0, (CameraWindowWidth, CameraWindowHeight)) #Prepare to save movie

def InitLickWriter():   # Inisiate txt export of lick log function
    global Writer_LickEventTxt, Writer_LickEventCsv, Path
    Writer_LickEventTxt = open(Path + "/" + str(Year) + "_" + str(Month) + "_" + str(Day) + " " + str(Hour) + "h" + str(Minute) + "m Task" + str(Task) + " Lick.txt", 'w')  # Initialize the text exporter
    Writer_LickEventCsv = open(Path + "/" + str(Year) + "_" + str(Month) + "_" + str(Day) + " " + str(Hour) + "h" + str(Minute) + "m Task" + str(Task) + " Lick.csv", 'w')  # Initialize the text exporter
    return
def EndLickWriter():   # End txt export of lick log function
    global Writer_LickEventTxt, Writer_LickEventCsv
    Writer_LickEventTxt.close()
    Writer_LickEventCsv.close()
    return

def OperantHouseUpdate():
    global FrameNum, OHCnt, TimeNow, FpsPreSec, FpsSec, FrameNumPerSec,w,EndFlag,BreakFlag,ret,frame,cv2,VideoWriter,Line, MainWindowRoot, ControlWindowRoot,TouchWindowRoot,ret, frame,cv2,Phase, TimerRunning, TimerNowTime, TimerPreTime, TimerCounter, TimerSec, TouchSymbolCnt, Year, Month, Day, Hour, Minute, Second, NosePokeRoiULX, NosePokeRoiULY, NosePokeRoiBRX, NosePokeRoiBRY, NosePokeRoiWidth, NosePokeRoiHeight, NosePoking, TouchSymbolCnt, MxCam, MyCam, RoiMovePhase, GrabbedID, Position, Distance, CameraWindowWidth, CameraWindowHeight, NosePokeSamplingDensity, NowPunishing, WaitExposureAdjustCnt, NosePokeIntTh, LightThVar, RoofLightPowerOn, ManualNosePokeOn, NosePokeDetectionOn, NosePokeHitNumTh, StartLickRecordingTrg, NowLickRecording, EndLickRecordingTrg, PreNosePoking, NosePokeNum, EndRecordTimerOn, EndRecordTimerCnt, TtlCurrTime, ElapsedTimePerFrame, ElapsedTime, TtlCurrQuotient, TtlCurrRemainder, TtlSquareElapsedTime, TtlPreQuotient, TtlCnt, TtlSquareOn, TtlSquareElapsedTime, TtlIsFirst, TtlOutputOn, TtlPreTime, TtlPower, SendingTtl, NextShatterTime, CaptureNum, FPS, Writer_LickEventTxt, SerialOutPhase, CurrentChannelID, IndicatedRoofLightPower, RoofLightPowerOn, IndicatedInfraredPower, InfraredPowerOn, IndicatedWaterCue, WaterCueOn, IndicatedValveTtlPower, ValveTtlPowerOn, IndicatedHoleCue, HoleCueOn, IndicatedHoleWaterCue, HoleWaterCueOn
    OHCnt+=1    # Counter
    #print('Phase: '+str(Phase)+'  Phase2: '+str(Phase2)+'  Task: '+str(Task)+' @'+str(CrossFireMoveDistance))
    # Declaration of local variables
    RoiR=255
    RoiG = 0
    RoiB = 0
    Red=0
    Green=0
    Blue=0
    Int=0
    SamplingPosX = 0
    SamplingPosY = 0
    Angle=90

    # Caliculate FPS
    FrameNum += 1
    TimeNow = datetime.datetime.now()
    FpsPreSec = FpsSec
    FpsSec = TimeNow.second
    if FpsSec != FpsPreSec:
        FPS=FrameNumPerSec
        StrFPS.set("FPS "+str(FPS))
        FrameNumPerSec=0
    else:
        FrameNumPerSec+=1

    # Get time
    Year = TimeNow.year
    Month = TimeNow.month
    Day = TimeNow.day
    Hour = TimeNow.hour
    Minute = TimeNow.minute
    Second = TimeNow.second
    # Update each windows
    MainWindowRoot.update()
    ControlWindowRoot.update()
    TouchWindowRoot.update()
    ret, Img = VideoCapture.read()

    if StartLickRecordingTrg==1:    # If recording of lick onset and offset is activated
        StartLickRecordingTrg = 0
        if NowLickRecording == 0:
            InitLickWriter()        # Init text export object of lick
            NowLickRecording = 1
    if EndLickRecordingTrg == 1:
        EndLickRecordingTrg = 0
        if NowLickRecording == 1:
            EndLickWriter()
            NowLickRecording = 0
    # Process of the movement of the nosepoke ROI
    cv2.waitKey(2)
    MxCam = mouseData.getX()    # Get mouse cursor coordinate
    MyCam = mouseData.getY()
    if RoiMovePhase == 3 and mouseData.getEvent() == 0: # If left click is released again
        RoiMovePhase = 0    # Get back the ROI phase
        GrabbedID = 0
    for i in range(2):  # Measure distances between mouse cursor and each tab of nose poke ROI
        if RoiMovePhase == 0 and mouseData.getEvent() == 1:
            Position[0][0]=MxCam
            Position[0][1]=MyCam
            if i==0:
                Position[1][0] = NosePokeRoiULX # Substitute upper left tab of the ROI
                Position[1][1] = NosePokeRoiULY
            if i==1:
                Position[1][0] = NosePokeRoiBRX # Substitute bottom right tab of the ROI
                Position[1][1] = NosePokeRoiBRY
            MeasureDistance()   # Measure distance
            if Distance < 64:   # If mouse cursor and tab are close enough
                GrabbedID = i+1 # Keep which tab is selected, 1: upper left  2: botton right
                RoiMovePhase = 1
    if RoiMovePhase==1 or RoiMovePhase==2:  # Move ROI tab according to the mouse cursor
        if GrabbedID==1:    # If upper left tab is selected
            NosePokeRoiULX = MxCam
            NosePokeRoiULY = MyCam
            if NosePokeRoiULX < 5:  # Limit the positions of the ROI tab not to stick out from the window
                NosePokeRoiULX = 5
            if NosePokeRoiULY < 5:
                NosePokeRoiULY = 5
            if NosePokeRoiULX > CameraWindowWidth - 10:
                NosePokeRoiULX = CameraWindowWidth - 10
            if NosePokeRoiULY > CameraWindowHeight - 10:
                NosePokeRoiULY = CameraWindowHeight - 10
            if NosePokeRoiULX > NosePokeRoiBRX: # Limit the positions of the ROI tab not to flip
                NosePokeRoiULX = NosePokeRoiBRX-5
            if NosePokeRoiULY > NosePokeRoiBRY:
                NosePokeRoiULY = NosePokeRoiBRY-5
            with open('data/NosePokeRoiULX.dat', 'wb') as fp:   # Save position of the tabs every frame
                pickle.dump(NosePokeRoiULX, fp)  # Save
            with open('data/NosePokeRoiULY.dat', 'wb') as fp:
                pickle.dump(NosePokeRoiULY, fp)  # Save
        if GrabbedID==2:    # If bottom right tab is selected
            NosePokeRoiBRX = MxCam
            NosePokeRoiBRY = MyCam
            if NosePokeRoiBRX < 10:
                NosePokeRoiBRX = 10
            if NosePokeRoiBRY < 10:
                NosePokeRoiBRY = 10
            if NosePokeRoiBRX > CameraWindowWidth - 5:
                NosePokeRoiBRX = CameraWindowWidth - 5
            if NosePokeRoiBRY > CameraWindowHeight - 5:
                NosePokeRoiBRY = CameraWindowHeight - 5
            if NosePokeRoiBRX < NosePokeRoiULX:
                NosePokeRoiBRX = NosePokeRoiULX+5
            if NosePokeRoiBRY < NosePokeRoiULY:
                NosePokeRoiBRY = NosePokeRoiULY+5
            with open('data/NosePokeRoiBRX.dat', 'wb') as fp:
                pickle.dump(NosePokeRoiBRX, fp)  # Save
            with open('data/NosePokeRoiBRY.dat', 'wb') as fp:
                pickle.dump(NosePokeRoiBRY, fp)  # Save
        if mouseData.getEvent() == 0:   # If left click is released
            RoiMovePhase = 2

        if RoiMovePhase == 2 and mouseData.getEvent() == 1: # If left click again
            RoiMovePhase = 3
    NosePokeRoiWidth = NosePokeRoiBRX - NosePokeRoiULX
    NosePokeRoiHeight = NosePokeRoiBRY - NosePokeRoiULY
    if RoiMovePhase == 0:   # If ROI is not moving
        RoiB = 255  # Change ROI color to blue
        RoiG = 0
        RoiR = 0
    if RoiMovePhase >= 1:   # If ROI is moving
        RoiB = 255  # Change ROI color to light blue
        RoiG = 100
        RoiR = 100
    cv2.line(Img, (NosePokeRoiULX, NosePokeRoiULY), (NosePokeRoiBRX, NosePokeRoiULY), (RoiB, RoiG, RoiR), 1)   # Draw nosepoke ROI line
    cv2.line(Img, (NosePokeRoiULX,NosePokeRoiBRY), (NosePokeRoiULX, NosePokeRoiULY), (RoiB, RoiG, RoiR), 1)   # Draw nosepoke ROI line
    cv2.line(Img, (NosePokeRoiBRX,NosePokeRoiBRY), (NosePokeRoiULX,NosePokeRoiBRY), (RoiB, RoiG, RoiR), 1)   # Draw nosepoke ROI line
    cv2.line(Img, (NosePokeRoiBRX,NosePokeRoiULY), (NosePokeRoiBRX,NosePokeRoiBRY), (RoiB, RoiG, RoiR), 1)   # Draw nosepoke ROI line
    cv2.rectangle(Img, (NosePokeRoiULX-3,NosePokeRoiULY-3), (NosePokeRoiULX+3,NosePokeRoiULY+3), (RoiB, RoiG, RoiR), -1)  # Draw nosepoke ROI tab
    cv2.rectangle(Img, (NosePokeRoiBRX-3,NosePokeRoiBRY-3), (NosePokeRoiBRX+3,NosePokeRoiBRY+3), (RoiB, RoiG, RoiR), -1)  # Draw nosepoke ROI tab
    if NosePoking==1:
        cv2.rectangle(Img, (NosePokeRoiULX, NosePokeRoiBRY+20), (NosePokeRoiULX+40, NosePokeRoiBRY+60), (0, 0, 255), -1)  # Draw dot

    if TouchSymbolCnt > 0:  # Process of touch symbol
        TouchSymbolCnt-=1
        cv2.rectangle(Img, (5,5), (80,80), (255, 255, 255), -1)  # Draw panel touching symbol

    #Detect nosepoke to the touch window
    NosePokeHitNum = 0
    NosePoking = 0
    NosePokeSamplingNumX = round(NosePokeRoiWidth / NosePokeSamplingDensity)
    NosePokeSamplingNumY = round(NosePokeRoiHeight / NosePokeSamplingDensity)
    if NosePokeSamplingNumX > 0 and NosePokeSamplingNumY > 0:
        for i in range(NosePokeSamplingNumY - 1):
            Y=i+1
            X=0
            for i2 in range(NosePokeSamplingNumX - 1):
                X = i2 + 1
                SamplingPosX = NosePokeRoiULX+(X*NosePokeSamplingDensity)
                SamplingPosY = NosePokeRoiULY+(Y*NosePokeSamplingDensity)
                Blue = Img[SamplingPosY, SamplingPosX, 0]
                Green = Img[SamplingPosY, SamplingPosX, 1]
                Red = Img[SamplingPosY, SamplingPosX, 2]
                Int = (int(Blue)+int(Green)+int(Red))/3
                if NowPunishing == 0 and WaitExposureAdjustCnt <= 0:
                    if RoofLightPowerOn==1:
                        NosePokeIntTh=LightThVar.get()  # Set the threshold of light phase
                    if RoofLightPowerOn==0:
                        NosePokeIntTh = DarkThVar.get() # Set the threshold of dark phase
                    if Int < NosePokeIntTh:    # If light intensity of sampled pixel exceed the threshold
                        NosePokeHitNum +=1  # Increase the positive sampled pixel number
                        cv2.rectangle(Img, (SamplingPosX-1, SamplingPosY-1), (SamplingPosX+1, SamplingPosY+1), (0, 0, 255), -1) # Draw red dot
                    if Int >= NosePokeIntTh:
                        cv2.rectangle(Img, (SamplingPosX-1, SamplingPosY-1), (SamplingPosX+1, SamplingPosY+1), (255, 0, 0), -1) # Draw blue dot
    NosePoking = 0
    if NosePokeDetectionOn == 1:    # If nosepoke detection is functional
        NosePokeHitNumTh = NumThVar.get()   # Get the threshold number of nosepoke detection
        if NosePokeHitNum >= NosePokeHitNumTh:  # If hit num exceed the threshold for the detection of the nosepoking
            NosePoking = 1
        if NowLickRecording==1:
            if PreNosePoking == 0 and NosePoking == 1:  # if this frame is the onset of nose poke
                Writer_LickEventTxt.write("NosePokeStart\t" + str(Year) + " / " + str(Month) + " / " + str(Day) + "\t" + str(Hour) + ":" + str(Minute) + "\t" + str(TimeNow.second) + "." + str(TimeNow.microsecond) + "\n")    # Write the onset of the nose poke on the text file
                Writer_LickEventCsv.write("NosePokeStart," + str(Year) + "," + str(Month) + "," + str(Day) + "," + str(Hour) + "," + str(Minute) + "," + str(TimeNow.second) + "." + str(TimeNow.microsecond) + "\n")   # Write the onset of the nose poke on the csv file
                NosePokeNum += 1
    if NowLickRecording == 1:
        if PreNosePoking == 1 and NosePoking == 0:  # if this frame is end of the nose poke
            Writer_LickEventTxt.write('NosePokeEnd\t' + str(Year) + " / " + str(Month) + " / " + str(Day) + "\t" + str(Hour) + ":" + str(Minute) + "\t" + str(TimeNow.second) + "." + str(TimeNow.microsecond)+"\n")   # Write the offset of the nose poke on the text file
            Writer_LickEventCsv.write('NosePokeEnd,' + str(Year) + "," + str(Month) + "," + str(Day) + "," + str(Hour) + "," + str(Minute) + "," + str(TimeNow.second) + "." + str(TimeNow.microsecond) + "\n")  # Write the offset of the nose poke on the csv file
    PreNosePoking = NosePoking  # Keep the value for the next frame

    if ManualNosePokeOn==1: # In nose poke is positive by pushing manual nosepoke button
        NosePoking=1


    cv2.imshow("CameraWindow", Img)  # Show captured video frame
    if NowRecording==1:
        if NextShatterTime <= ElapsedTime:
            if ret == True:
                VideoWriter.write(Img)  # Record captured video of the current frame
                ShatterWaitTime = 1000.0 / float(FPS)
                NextShatterTime += ShatterWaitTime
                CaptureNum += 1
            else:
                EndFlag = 1
    # Process of Timers
    for i in range(2):
        if TimerRunning[i]==1:
            TimerNowTime[i]=TimeNow.microsecond//100000
            if TimerNowTime[i] != TimerPreTime[i]:  # If it past 0.1 sec
                TimerCounter[i]+=1
                TimerSec[i]=TimerCounter[i]/10  # Caliculate time in sec
                TimerPreTime[i]=TimerNowTime[i]
    #print(TimerSec[0])
    if EndRecordTimerOn==1: # If record end trigger is on
        EndRecordTimerCnt-=1    # Decrease the counter
        if EndRecordTimerCnt<=0:    # If it's time for stop recording
            EndRecording()  # Stop recording
            EndRecordTimerOn=0  # Change recording status variable

    if SendingTtl==1:
        TtlCurrTime = TimeNow.second*1000 + (TimeNow.microsecond/1000)
        if TtlCurrTime >= TtlPreTime:
            ElapsedTimePerFrame = TtlCurrTime - TtlPreTime
        if TtlCurrTime < TtlPreTime:
            ElapsedTimePerFrame = 60000 - TtlPreTime + TtlCurrTime
        ElapsedTime += ElapsedTimePerFrame
        TtlCurrQuotient = ElapsedTime // TtlITV     # Quotient
        TtlCurrRemainder = ElapsedTime % TtlITV     # Remainder
        Trg = 0
        if TtlPreQuotient < TtlCurrQuotient:
            TtlSquareElapsedTime = TtlCurrRemainder #
            TtlPower=1 # Turn on TTL output
            TtlPreQuotient = TtlCurrQuotient
            Trg=1
            TtlCnt+=1
        if TtlSquareOn==1 and Trg==0:   #
            TtlSquareElapsedTime += ElapsedTimePerFrame #
            if (TtlIsFirst == 1 and TtlSquareElapsedTime >= Ttl1stSquareDuration) or (TtlIsFirst == 0 and TtlSquareElapsedTime >= TtlSquareDuration):   #
                TtlIsFirst= 0
                TtlPower=-1 # Turn off TTL output
        TtlPreTime = TtlCurrTime

    # Reflect indicated variables
    if TtlPower==1:
        TtlSquareOn = 1   # Change TTL status variable
    if TtlPower==-1:
        TtlSquareOn = 0   # Change TTL status variable

    if IndicatedRoofLightPower==1:
        IndicatedRoofLightPower=0
        RoofLightPowerOn=1   # Change roof light status variable
    if IndicatedRoofLightPower==-1:
        IndicatedRoofLightPower=0
        RoofLightPowerOn=0  # Change roof light status variable

    if IndicatedInfraredPower==1:
        IndicatedInfraredPower=0
        InfraredPowerOn=1   # Change infrared status variable
    if IndicatedInfraredPower==-1:
        IndicatedInfraredPower=0
        InfraredPowerOn=0   # Change infrared status variable

    if IndicatedWaterCue==1:
        IndicatedWaterCue=0
        WaterCueOn=1   # Change water cue (located beneath the slit) status variable
    if IndicatedWaterCue==-1:
        IndicatedWaterCue=0
        WaterCueOn=0    # Change water cue (located beneath the slit) status variable

    if IndicatedValveTtlPower==1:
        IndicatedValveTtlPower=0
        ValveTtlPowerOn=1   # Change valve TTL status variable
    if IndicatedValveTtlPower==-1:
        IndicatedValveTtlPower=0
        ValveTtlPowerOn=0   # Change valve TTL status variable

    for i in range(5):
        if IndicatedHoleCue[i]==1:
            IndicatedHoleCue[i]=0
            HoleCueOn[i]=1  # Change hole cue status variable
        if IndicatedHoleCue[i]==-1:
            IndicatedHoleCue[i]=0
            HoleCueOn[i]=0  # Change hole cue status variable

        if IndicatedHoleWaterCue[i]==1:
            IndicatedHoleWaterCue[i]=0
            HoleWaterCueOn[i]=1 # Change hole water cue status variable
        if IndicatedHoleWaterCue[i]==-1:
            IndicatedHoleWaterCue[i]=0
            HoleWaterCueOn[i]=0 # Change hole water cue status variable

    if IndicatedWaterPos==1:    # If water nozzle is indicated to be inside
        Angle=int(InAngleVar.get())  # Get angle value from input column
    if IndicatedWaterPos==0:    # If water nozzle is indicated to be middle
        Angle=int(MidAngleVar.get()) # Get angle value from input column
    if IndicatedWaterPos==2:    # If water nozzle is indicated to be outside
        Angle=int(OutAngleVar.get()) # Get angle value from input column

    Trg=0
    if SerialOutPhase==0:   # Select channel
        if CurrentChannelID==0:
            ser.write(b'a') # Send type of the following information to arduino
        if CurrentChannelID==1:
            ser.write(b'b')
        if CurrentChannelID==2:
            ser.write(b'c')
        if CurrentChannelID==3:
            ser.write(b'd')
        if CurrentChannelID == 4:
            ser.write(b'e')
        if CurrentChannelID == 5:
            ser.write(b'f')
        if CurrentChannelID == 6:
            ser.write(b'g')
        if CurrentChannelID == 7:
            ser.write(b'h')
        SerialOutPhase=1
    if SerialOutPhase==1:    # Send value to regulate switching of the channel
        if CurrentChannelID==0:
            TempBinary = bytes(str(TtlSquareOn), 'utf-8')
        if CurrentChannelID==1:
            TempBinary = bytes(str(RoofLightPowerOn), 'utf-8')
        if CurrentChannelID==2:
            TempBinary = bytes(str(InfraredPowerOn), 'utf-8')
        if CurrentChannelID==3:
            TempBinary = bytes(str(WaterCueOn), 'utf-8')
        if CurrentChannelID == 4:
            TempBinary = bytes(str(ValveTtlPowerOn), 'utf-8')
        if CurrentChannelID == 5:
            TempBinary = bytes(str(HoleCueOn[0]), 'utf-8')
        if CurrentChannelID == 6:
            TempBinary = bytes(str(HoleWaterCueOn[0]), 'utf-8')
        if CurrentChannelID == 7:
            TempBinary = bytes(chr(Angle), 'utf-8')
            #Angle="90"
            #print(chr(Angle)+chr(Angle))
            #print("a")
        ser.write(TempBinary)   # Send information to arduino
        SerialOutPhase = 0
        CurrentChannelID += 1
        if CurrentChannelID >= 8:
            CurrentChannelID = 0

    #abc=ser.readline().decode("utf-8").strip('\n').strip('\r')  # Read the input value of the infrared sensor (Work when combined with "Serial conection with python 3")
    #print(abc)
    #print("int"+abc)
    #if OHCnt%7==7:
        #ser.flushInput()    # Clear input buffer from arduino

    if TtlPower!=0:
        if TtlPower == 1 and TtlCnt > 0:
            Writer_TtlLogCsv.write("TTL ON," + str(TtlCnt) + "," + str(TimeNow.hour) + "," + str(TimeNow.minute) + "," + str(TimeNow.second) + "." + str(TimeNow.microsecond)+"\n") # # Write the timing of TTL onset and offset
        if TtlPower == -1 and TtlCnt > 0:
            Writer_TtlLogCsv.write("TTL OFF," + str(TtlCnt) + "," + str(TimeNow.hour) + "," + str(TimeNow.minute) + "," + str(TimeNow.second) + "." + str(TimeNow.microsecond)+"\n")
        TtlPower = 0

    return

MainWindowRoot.update()
ControlWindowRoot.update()
TouchWindowRoot.update()

if os.path.exists('data/Path.dat') == True: # Upper left X coordinate of touch panel on the window
   with open('data/Path.dat', 'rb') as fp:
       Path = pickle.load(fp)
else:
    Path = 'C:\\'   # Default path for saving

# Load parameters of control window
if os.path.exists('data/LightTh.dat') == True: # Upper left X coordinate of touch panel on the window
   with open('data/LightTh.dat', 'rb') as fp:
       LightThVar.set(pickle.load(fp))  # Load
else:
    LightThVar.set(50)    # Default path for saving

if os.path.exists('data/DarkTh.dat') == True: # Upper left X coordinate of touch panel on the window
   with open('data/DarkTh.dat', 'rb') as fp:
       DarkThVar.set(pickle.load(fp))  # Load
else:
    DarkThVar.set(50)    # Default path for saving

if os.path.exists('data/NumTh.dat') == True:  # Upper left X coordinate of touch panel on the window
    with open('data/NumTh.dat', 'rb') as fp:
        NumThVar.set(pickle.load(fp))  # Load
else:
    NumThVar.set(3)  # Default path for saving

if os.path.exists('data/InAngle.dat') == True:  # Upper left X coordinate of touch panel on the window
    with open('data/InAngle.dat', 'rb') as fp:
        InAngleVar.set(pickle.load(fp))  # Load
else:
    InAngleVar.set(0)  # Default path for saving

if os.path.exists('data/MidAngle.dat') == True:  # Upper left X coordinate of touch panel on the window
    with open('data/MidAngle.dat', 'rb') as fp:
        MidAngleVar.set(pickle.load(fp))  # Load
else:
    MidAngleVar.set(90)  # Default path for saving

if os.path.exists('data/OutAngle.dat') == True:  # Upper left X coordinate of touch panel on the window
    with open('data/OutAngle.dat', 'rb') as fp:
        OutAngleVar.set(pickle.load(fp))  # Load
else:
    OutAngleVar.set(180)  # Default path for saving

if os.path.exists('data/TouchXAdjust.dat') == True:  # Upper left X coordinate of touch panel on the window
    with open('data/TouchXAdjust.dat', 'rb') as fp:
        TouchXAdjustVar.set(pickle.load(fp))  # Load
else:
    TouchXAdjustVar.set(0)  # Default path for saving

if os.path.exists('data/TouchYAdjust.dat') == True:  # Upper left X coordinate of touch panel on the window
    with open('data/TouchYAdjust.dat', 'rb') as fp:
        TouchYAdjustVar.set(pickle.load(fp))  # Load
else:
    TouchYAdjustVar.set(0)  # Default path for saving


if os.path.exists('data/PanelULX.dat') == True: # Upper left X coordinate of touch panel on the window
   with open('data/PanelULX.dat', 'rb') as fp:
       PanelULX = pickle.load(fp)
else:
    PanelULX = [[0]*MaxPanelNum]*MaxTaskNum
if os.path.exists('data/PanelULY.dat') == True: # Upper left Y coordinate of touch panel on the window
    with open('data/PanelULY.dat', 'rb') as fp:
        PanelULY = pickle.load(fp)
else:
    PanelULY = [[0] * MaxPanelNum] * MaxTaskNum
if os.path.exists('data/PanelBRX.dat') == True: # Lower right X coordinate of touch panel on the window
    with open('data/PanelBRX.dat', 'rb') as fp:
        PanelBRX = pickle.load(fp)
else:
    PanelBRX = [[0] * MaxPanelNum] * MaxTaskNum
if os.path.exists('data/PanelBRY.dat') == True: # Lower right Y coordinate of touch panel on the window
    with open('data/PanelBRY.dat', 'rb') as fp:
        PanelBRY = pickle.load(fp)
else:
    PanelBRY = [[0] * MaxPanelNum] * MaxTaskNum

if os.path.exists('data/NosePokeRoiULX.dat') == True: # Upper left X coordinate of nose poke detection ROI
    with open('data/NosePokeRoiULX.dat', 'rb') as fp:
        NosePokeRoiULX = pickle.load(fp)
else:
    NosePokeRoiULX = 100

if os.path.exists('data/NosePokeRoiULY.dat') == True: # Upper left Y coordinate of nose poke detection ROI
    with open('data/NosePokeRoiULY.dat', 'rb') as fp:
        NosePokeRoiULY = pickle.load(fp)
else:
    NosePokeRoiULY = 100

if os.path.exists('data/NosePokeRoiBRX.dat') == True: # Bottom right X coordinate of nose poke detection ROI
    with open('data/NosePokeRoiBRX.dat', 'rb') as fp:
        NosePokeRoiBRX = pickle.load(fp)
else:
    NosePokeRoiBRX = 200

if os.path.exists('data/NosePokeRoiBRY.dat') == True: # Bottom right Y coordinate of nose poke detection ROI
    with open('data/NosePokeRoiBRY.dat', 'rb') as fp:
        NosePokeRoiBRY = pickle.load(fp)
else:
    NosePokeRoiBRY = 200

TouchWindowRoot.bind('<Motion>', motion)
ret, Img = VideoCapture.read()    #Capture video frame
cv2.imshow("CameraWindow", Img)  # Show captured video frame
#mouseData = mouseParam("CameraWindow") # Instantiate class for get mouse cursor coordinates of camera window
while EndFlag==0: # Main roop of non-task period
    Phase = 0
    OperantHouseUpdate()

ser.close()
VideoWriter.release()
VideoCapture.release()
cv2.destroyAllWindows()

