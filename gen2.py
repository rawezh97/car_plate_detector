import cv2
import numpy as np
import time
import easyocr
import os
import tkinter as tk
import cvui


def cut():
    global mask
    location = approx
    mask = np.zeros(gray.shape , np.uint8)
    new_img = cv2.drawContours(mask , [location] , 0,255,-1)
    new_img = cv2.bitwise_and(image , image , mask=mask)
    cv2.imshow("new_img" , new_img)

def plate():
	global x1 , y1 , x2 , y2 , croped_image
	(x,y) = np.where(mask==255)
	x1 , y1 = (np.min(x) , np.min(y))
	x2 , y2 = (np.max(x) , np.max(y))
	croped_image = image[x1:x2+2 , y1:y2+2]
	cv2.imshow("croped_image" , croped_image)

reader = easyocr.Reader(['en'])
def ocr():
	result = reader.readtext(croped_image)
	return result
def ocr_button():
    if cvui.button(setting,200,120, "OCR") and cvui.mouse(cvui.CLICK):
        text = ocr()
        if len(text) > 1 :
            plate_text=[]
            for i in text:
                plate_text.append(i[1])
            text = ' '.join(plate_text)
        else :
            for i in text:
                text = i[1]
        if text == []:
            pass
        else:
            print (text)
        time.sleep(1)

def control(arg):
	global Stracture_Elment_A,Stracture_Elment_B,ad_threshold_A,ad_threshold_B
	Stracture_Elment_A = cv2.getTrackbarPos('Stracture_Elment_A','setting')
	Stracture_Elment_B = cv2.getTrackbarPos('Stracture_Elment_B','setting')

	ad_threshold_A = cv2.getTrackbarPos('ad_threshold_A' , 'setting')
	ad_threshold_B = cv2.getTrackbarPos('ad_threshold_A' , 'setting')

Stracture_Elment_A = 1
Stracture_Elment_B = 2
ad_threshold_A = 17
ad_threshold_B = 1

controls = cv2.namedWindow('setting' ,  cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar("Stracture_Elment_A", 'setting' ,1,9, control )
cv2.createTrackbar("Stracture_Elment_B", 'setting' ,2,9, control )
cv2.createTrackbar("ad_threshold_A", 'setting' ,17,180, control )
cv2.createTrackbar("ad_threshold_B", 'setting' ,1,180, control )

print (Stracture_Elment_A)

image_name = []
list = os.listdir("aurupa")
for list in list :
	image_name.append(list)
default = 0
# car_plate

setting = np.zeros((200, 500, 3), np.uint8)
cvui.init('setting')
while True:
    image = cv2.imread(f'/home/world/Desktop/car_plate/aurupa/{image_name[default]}')
    width,height,channels = image.shape
    #print(width,height)
    setting[:] = (49,52,49)
    if cvui.button(setting,200,40, "Next"):
        cvui.init('setting')
        default +=1
        if default >= len(image_name):
            default = 0
    if cvui.button(setting,200,120, "OCR") and cvui.mouse(cvui.CLICK):
    	pass
    resized = 0
    if width > 1000 or height >= 1200 :
        resized = 1
        image = cv2.resize(image , (1120,800))
    if width < 600 and height < 700 :
        resized = 2
        image = cv2.resize(image , (1120,800))
    gray = cv2.cvtColor(image , cv2.COLOR_BGR2GRAY)

    threshold = cv2.threshold(gray,145,255,cv2.THRESH_BINARY)[1]
    blurred = cv2.GaussianBlur(gray , (3,3) , cv2.BORDER_WRAP)

    thresh_blurred = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, ad_threshold_A , 1)##########
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(Stracture_Elment_A , Stracture_Elment_B))
    thre = cv2.morphologyEx(thresh_blurred,cv2.MORPH_OPEN,kernel)

    contour , _ = cv2.findContours(thre , cv2.RETR_TREE , cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contour:
        x,y,w,h = cv2.boundingRect(cnt)
        a = w*h
        ratio = float(w)/h
        if ratio > 2.5 and a > 600 :
            approx = cv2.approxPolyDP(cnt, 0.05* cv2.arcLength(cnt , True),True)
            if len(approx) == 4 and x > 15:
                area = cv2.contourArea(cnt)
                #location = approx
                if cvui.button(setting,200,80, "Shot") and cvui.mouse(cvui.CLICK):
                	print (f"x:{x} , y:{y} , w:{w} , h:{h}")
                	shot = image[x1:x2 , y1:y2]
	                cv2.imwrite("shote.jpg" , shot)

                if resized == 1 :
                    if area > 3000 and area < 35000 :
                        cv2.rectangle(image , (x,y) , (x+w , y+h) , (255,0,0) ,5)
                        cut()
                        plate()
                        ocr_button()
                        #print (str(area)+" resized:" + str(resized))

                    else:
                        pass
                if resized == 2:
                	if area > 3000 and area < 15000 :
                		cv2.rectangle(image , (x,y) , (x+w , y+h) , (0,255,0) ,5)
                		cut()
                		plate()
                		ocr_button()
                		#print (str(area)+" resized:" + str(resized))
                else:
                    if area > 2000 and area < 15000 :
                    	cv2.rectangle(image , (x,y) , (x+w , y+h) , (0,0,255) ,5)
                    	#print (str(area)+" orginal" +"   width:" + str(width) +"       height:" +str(height))
                    	cut()
                    	plate()
                    	ocr_button()

    cv2.imshow("image" , image)
    cv2.imshow("treshold" , thre)
    cv2.imshow("setting" , setting)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
image.release()
cv2.destroyAllWindows()
