"OCR機能の実装"
from PIL import Image
import pyocr  # type: ignore
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2

def adjust_img(data):
  height, width = data.shape[:2]
  new_height = int(height * (300 / 96))  
  new_width = int(width * (300 / 96))
  gray_image = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
  denoised_image = cv2.bilateralFilter(gray_image, 9, 75, 75)
  resize_image = cv2.resize(denoised_image, (new_width, new_height))
  _, binary_image = cv2.threshold(resize_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
  recreated_image=binary_image
  return cv2.imwrite('resized_image.png', recreated_image) 

#url="/workspaces/python/meatpie/png/print-ocr1.png"
cap=cv2.VideoCapture(0)
while True:
 ret, frame = cap.read()
 cv2.imshow('camera' , frame)
 adjust_img(frame)
 if ret is False:
   break
 tools = pyocr.get_available_tools()
 tool = tools[0]
 txt1 = tool.image_to_string(
    frame,
    lang='jpn+eng',
    builder=pyocr.builders.TextBuilder(tesseract_layout=6)
)
print(txt1)

  
cap.release()
cv2.destroyAllWindows()

if ret is False:
	raise ValueError(f"Failed to capture image")



