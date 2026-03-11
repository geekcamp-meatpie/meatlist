from PIL import Image
import pyocr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import sys
from dataclasses import dataclass

filepath = '/workspaces/python/meatpie/png/print-ocr1.png'

@dataclass
class todolist():
   text:str 
   def to_json(self):
    data = {"txt_data":self.text}
    return data




def adjust_img(data):
    height, width = data.shape[:2]
    new_height = int(height * (300 / 96))  
    new_width = int(width * (300 / 96))
    gray_image = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
    #denoised_image = cv2.bilateralFilter(gray_image, 9, 75, 75)
    resize_image = cv2.resize(gray_image, (new_width, new_height))
    _, binary_image = cv2.threshold(resize_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    recreated_image = binary_image
    cv2.imwrite('resized_image.png', recreated_image)
    return print("sucucess")

cap = cv2.VideoCapture(0)

tools = pyocr.get_available_tools()
if not tools:
    print("No OCR tools available. Please install Tesseract.")
    sys.exit(1)
tool = tools[0]

def video_capture():
  cap = cv2.VideoCapture(0)
  tools = pyocr.get_available_tools()
  if not tools:
    print("No OCR tools available. Please install Tesseract.")
    sys.exit(1)
    tool = tools[0]
  while True:
    ret, frame = cap.read()
    if ret is False:
        break
    
    cv2.imshow('camera' , frame)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        # 'q' キーが押されたらループを抜けて終了する
        break
    elif key == ord('c'):
        # 【修正3】'c' キーが押された時だけOCRを実行する
        print("画像を処理中...")
        adjust_img(frame)
        img_pil = Image.open('resized_image.png')
        
        txt1 = tool.image_to_string(
            img_pil,
            lang='jpn',
            builder=pyocr.builders.TextBuilder(tesseract_layout=6)
        )
        print("\n--- OCR読み取り結果 ---")
        print(txt1)
        print("-----------------------\n")

def photo_capture(filepath):
    img = cv2.imread(filepath)
    adjust_img(img)
    img_pil = Image.open('resized_image.png')
    txt1 = tool.image_to_string(
        img_pil,
        lang='jpn',
        builder=pyocr.builders.TextBuilder(tesseract_layout=4)
    )
    return todolist.to_json(todolist(txt1))
Text_json = photo_capture(filepath)
#cap.release()
#cv2.destroyAllWindows()