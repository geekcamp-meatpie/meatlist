import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# 対応画像形式
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


def load_api_key() -> str | None:
    """OpenAI APIキーを環境変数から取得する"""
    return os.getenv("OPENAI_API_KEY")


def is_allowed_file(filename: str) -> bool:
    """ファイル拡張子が対応形式かチェックする"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS
