from PIL import Image
import pyocr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import sys

def adjust_img(data):
    height, width = data.shape[:2]
    new_height = int(height * (300 / 96))  
    new_width = int(width * (300 / 96))
    gray_image = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
    denoised_image = cv2.bilateralFilter(gray_image, 9, 75, 75)
    resize_image = cv2.resize(denoised_image, (new_width, new_height))
    _, binary_image = cv2.threshold(resize_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    recreated_image = binary_image
    cv2.imwrite('resized_image.png', recreated_image)
    return recreated_image

cap = cv2.VideoCapture(0)

# 【修正1】OCRツールの準備はループの「外」に出す
# 理由: ループの中で毎回ツールを探すと、処理が重くなりすぎるため。
tools = pyocr.get_available_tools()
if not tools:
    print("No OCR tools available. Please install Tesseract.")
    sys.exit(1)
tool = tools[0]

print("カメラを起動しました。文字を映して 'c' キーを押すと読み取ります。'q' キーで終了します。")

while True:
    ret, frame = cap.read()
    if ret is False:
        break
    
    cv2.imshow('camera' , frame)
    
    # 【修正2】キーボード入力を受け付ける処理を追加
    # 理由: cv2.waitKey() がないと、OpenCVのウィンドウがフリーズして映像が更新されません。
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        # 'q' キーが押されたらループを抜けて終了する
        break
        
    elif key == ord('c'):
        # 【修正3】'c' キーが押された時だけOCRを実行する
        # 理由: 毎フレーム（1秒間に30回など）OCRを実行するとPCがパンクするため、手動撮影式に変更。
        print("画像を処理中...")
        
        # 前処理を実行し、'resized_image.png' として保存
        adjust_img(frame)
        
        # 【修正4】保存した「前処理済み画像」をPIL形式で読み込んでOCRに渡す
        # 理由: ここが先ほどのエラーの原因です。OpenCV形式の frame ではなく、PIL形式に変換したものを渡します。
        img_pil = Image.open('resized_image.png')
        
        txt1 = tool.image_to_string(
            img_pil,
            lang='jpn+eng',
            builder=pyocr.builders.TextBuilder(tesseract_layout=6)
        )
        print("\n--- OCR読み取り結果 ---")
        print(txt1)
        print("-----------------------\n")

cap.release()
cv2.destroyAllWindows()