import os
import sys
from dotenv import load_dotenv

def check_env():
    # .env をロード（上書きなし）
    load_dotenv()
    key_no_override = os.environ.get("GEMINI_API_KEY")
    
    # .env をロード（上書きあり）
    load_dotenv(override=True)
    key_override = os.environ.get("GEMINI_API_KEY")
    
    print(f"Current working directory: {os.getcwd()}")
    print(f"No override key: {key_no_override[:4]}...{key_no_override[-4:] if key_no_override else ''}")
    print(f"Override key:    {key_override[:4]}...{key_override[-4:] if key_override else ''}")
    
    if key_no_override != key_override:
        print("\n[発見] 環境変数に古いキーが残っています。override=True が必要です。")
    else:
        print("\n環境変数は正しく同期されているようです。")

if __name__ == "__main__":
    check_env()
