<<<<<<< HEAD
from PIL import Image
import pyocr
import cv2
import sys
from dataclasses import dataclass
from app.ocr.main import Return_file

filepath = Return_file()

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



tools = pyocr.get_available_tools()
if not tools:
    print("No OCR tools available. Please install Tesseract.")
    sys.exit(1)
tool = tools[0]

#↓動画キャプチャのコードは一旦コメントアウトしておきます。（動画でのocrは要相談）
#cap = cv2.VideoCapture(0)
#cap.release()
#cv2.destroyAllWindows()
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
#動画キャプチャここまで

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
=======
from PIL import Image
import pyocr
import numpy as np
import cv2
import sys
from dataclasses import dataclass


@dataclass
class TodoItem:
    """Todoアイテムのデータクラス"""
    text: str

    def to_json(self):
        return {"task": self.text, "status": "todo"}


def _get_ocr_tool():
    """OCRエンジン（Tesseract）を取得する"""
    tools = pyocr.get_available_tools()
    if not tools:
        raise RuntimeError(
            "OCRツールが見つかりません。Tesseractをインストールしてください。\n"
            "Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "Mac: brew install tesseract tesseract-lang\n"
            "Linux: apt install tesseract-ocr tesseract-ocr-jpn"
        )
    return tools[0]


def adjust_img(data):
    """
    画像の前処理を行う（グレースケール化・リサイズ・二値化）

    Args:
        data: OpenCV形式の画像データ (numpy array)

    Returns:
        前処理済みの画像データ (numpy array)
    """
    height, width = data.shape[:2]
    # 96dpi → 300dpi 相当にリサイズ
    new_height = int(height * (300 / 96))
    new_width = int(width * (300 / 96))

    # グレースケール変換
    gray_image = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)

    # リサイズ
    resize_image = cv2.resize(gray_image, (new_width, new_height))

    # 大津の二値化
    _, binary_image = cv2.threshold(
        resize_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return binary_image


def ocr_from_image(pil_image: Image.Image) -> str:
    """
    PIL Imageからテキストを抽出する（API連携用メイン関数）

    Args:
        pil_image: PIL.Image オブジェクト

    Returns:
        抽出されたテキスト文字列
    """
    # PIL Image → OpenCV形式に変換
    img_array = np.array(pil_image)

    # グレースケールの場合はBGRに変換（OpenCVの後の処理でBGRであることを期待している場合）
    if len(img_array.shape) == 2:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
    # RGBAの場合はRGBに変換
    elif len(img_array.shape) == 3 and img_array.shape[2] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
    elif len(img_array.shape) == 3:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    # 前処理
    processed = adjust_img(img_array)

    # 前処理済み画像をPILに戻す
    processed_pil = Image.fromarray(processed)

    # OCR実行
    tool = _get_ocr_tool()
    text = tool.image_to_string(
        processed_pil,
        lang='jpn',
        builder=pyocr.builders.TextBuilder(tesseract_layout=6)
    )

    # テキストの整理（空行除去・前後の空白トリム）
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)


def photo_capture(filepath: str) -> str:
    """
    ファイルパスから画像を読み込みOCRを実行する

    Args:
        filepath: 画像ファイルのパス

    Returns:
        抽出されたテキスト文字列
    """
    img = cv2.imread(filepath)

    if img is None:
        raise FileNotFoundError(f"画像ファイルが見つかりません: {filepath}")

    # 前処理
    processed = adjust_img(img)

    # PILに変換してOCR
    processed_pil = Image.fromarray(processed)

    tool = _get_ocr_tool()
    text = tool.image_to_string(
        processed_pil,
        lang='jpn',
        builder=pyocr.builders.TextBuilder(tesseract_layout=6)
    )

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)
>>>>>>> 13f7bddc438c15b9012d0445c084d366b516609b
