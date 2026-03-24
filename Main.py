import cv2
import time
import math
import numpy as np
import HandTrackingModule as htm
import pyautogui
import autopy
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import macros

# -------------------- Utility --------------------
def putText(img, text, loc=(250, 450), color=(0,255,255)):
    cv2.putText(img,str(text),loc,cv2.FONT_HERSHEY_COMPLEX_SMALL,2,color,2)

# -------------------- Setup --------------------
wCam,hCam=640,480
cap=cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

pTime=0
pyautogui.FAILSAFE=False

detector=htm.handDetector(maxHands=1,detectionCon=0.85,trackCon=0.8)

# -------------------- Audio --------------------
devices=AudioUtilities.GetSpeakers()
interface=devices.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None)
volume=cast(interface,POINTER(IAudioEndpointVolume))
volRange=volume.GetVolumeRange()
minVol=volRange[0]
maxVol=volRange[1]

tipIds=[4,8,12,16,20]

system_mode="NORMAL"
profile=1
macro_start_time=0
profile_msg_time=0

# -------------------- Main Loop --------------------
while True:

    success,img=cap.read()
    if not success:
        continue

    img=detector.findHands(img)
    lmList=detector.findPosition(img,draw=False)

    fingers=[0,0,0,0,0]

    if lmList:

        # Finger Detection
        fingers[0]=1 if lmList[4][1]>lmList[3][1] else 0
        for i in range(1,5):
            fingers[i]=1 if lmList[tipIds[i]][2] < lmList[tipIds[i]-2][2] else 0

        x,y=lmList[8][1],lmList[8][2]
        dot_color=(0,0,255)

        # ============ MODE SWITCH ============
        if fingers==[0,0,0,0,0] and system_mode!="MACRO":
            system_mode="MACRO"
            macro_start_time=time.time()

        elif fingers==[1,1,1,1,1]:
            system_mode="CONTROL"

        # ============ PROFILE SWITCH ============
        if fingers==[1,1,0,0,1]:
            profile=2 if profile==1 else 1
            profile_msg_time=time.time()
            time.sleep(0.7)

        # ============ CONTROL MODE ============
        if system_mode=="CONTROL":

            putText(img,f"CONTROL | PROFILE {profile}",(80,100),(0,255,0))

            # Cursor (Open Palm)
            if fingers==[1,1,1,1,1]:

                w,h=autopy.screen.size()
                X=int(np.interp(x,[100,600],[0,w-1]))
                Y=int(np.interp(y,[50,400],[0,h-1]))
                autopy.mouse.move(X,Y)

                dot_color=(0,255,0)

            # Scroll Up
            elif fingers==[0,1,0,0,0]:
                pyautogui.scroll(300)
                dot_color=(0,255,0)

            # Scroll Down
            elif fingers==[0,1,1,0,0]:
                pyautogui.scroll(-300)
                dot_color=(0,255,0)

            # Volume Control
            elif fingers==[1,1,0,0,0]:

                x1,y1=lmList[4][1],lmList[4][2]
                x2,y2=lmList[8][1],lmList[8][2]

                cv2.circle(img,(x1,y1),10,(255,0,255),cv2.FILLED)
                cv2.circle(img,(x2,y2),10,(255,0,255),cv2.FILLED)
                cv2.line(img,(x1,y1),(x2,y2),(255,0,255),3)

                length=math.hypot(x2-x1,y2-y1)
                vol=np.interp(length,[30,200],[minVol,maxVol])
                volume.SetMasterVolumeLevel(vol,None)

                dot_color=(0,255,0)

        # ============ MACRO MODE ============
        elif system_mode=="MACRO":

            time_passed=time.time()-macro_start_time
            dot_color=(255,0,0)

            if time_passed<2:
                putText(img,"MACRO WAIT...",(150,100),(0,255,255))

            else:
                putText(img,f"MACRO | PROFILE {profile}",(80,100),(255,0,255))

                # -------- PROFILE 1 --------
                if profile==1:

                    if fingers==[1,0,0,0,0]:
                        macros.lock_screen()

                    elif fingers==[0,1,1,0,0]:
                        macros.open_browser()

                    elif fingers==[0,1,0,0,0]:
                        macros.open_vscode()

                    elif fingers==[0,1,0,0,1]:
                        macros.open_instagram()

                    elif fingers==[1,0,0,0,1]:
                        macros.open_notepad()

                # -------- PROFILE 2 --------
                elif profile==2:

                    if fingers==[1,0,0,0,0]:
                        macros.lock_screen()

                    elif fingers==[0,1,1,0,0]:
                        macros.open_youtube()

                    elif fingers==[0,1,0,0,0]:
                        macros.open_notepad()

                    elif fingers==[0,1,0,0,1]:
                        macros.open_instagram()

                    elif fingers==[1,0,0,0,1]:
                        macros.open_vscode()

        # Indicator Dot
        cv2.circle(img,(x,y),15,dot_color,cv2.FILLED)

    # Profile Switch Message
    if time.time()-profile_msg_time < 1.5:
        putText(img,f"PROFILE {profile} ACTIVATED",(120,200),(255,255,0))

    # FPS
    cTime=time.time()
    fps=int(1/(cTime-pTime+0.01))
    pTime=cTime

    cv2.putText(img,f'FPS:{fps}',(480,50),
    cv2.FONT_ITALIC,1,(255,0,0),2)

    cv2.imshow("Hand LiveFeed",img)

    if cv2.waitKey(1) & 0xFF==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()