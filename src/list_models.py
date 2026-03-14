import os
from google import genai
from dotenv import load_dotenv

def list_models():
    load_dotenv(override=True)
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key and "AIza" in api_key:
        api_key = api_key[api_key.find("AIza"):].strip().strip("'").strip('"')
    
    print(f"Checking models for key: {api_key[:10]}...")
    client = genai.Client(api_key=api_key)
    
    try:
        print("Available models:")
        # google-genai SDK でモデル一覧を取得
        for model in client.models.list():
            print(f"- {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
