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