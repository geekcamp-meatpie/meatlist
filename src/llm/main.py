import os
import json
from openai import OpenAI

# ----------------------------------------------------------------------
# 【モデル変更時の注意点】
# 他のLLM（AnthropicのClaudeや、GoogleのGeminiなど）を使用する場合は、
# 以下のクライアント初期化部分と、API呼び出し部分（generate_todo_list内）を
# それぞれのSDKに合わせて書き換えてください。
# 
# 例: Geminiの場合
# import google.generativeai as genai
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# model = genai.GenerativeModel('gemini-pro')
# response = model.generate_content(prompt)
#
# 例: Anthropic (Claude) の場合
# import anthropic
# client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
# response = client.messages.create(...)
# ----------------------------------------------------------------------

# OpenAIクライアントの初期化（環境変数 OPENAI_API_KEY が必要です）
# 実行前に `set OPENAI_API_KEY=your_api_key_here` などで設定してください。
def get_openai_client():
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        return client
    except Exception as e:
        print(f"OpenAIクライアントの初期化に失敗しました: {e}")
        return None


def generate_todo_list(ocr_text: str) -> dict:
    """
    OCRから抽出されたテキストを受け取り、LLMにToDoリストをJSONで生成させる関数

    Args:
        ocr_text (str): OCRで読み取ったテキストデータ

    Returns:
        dict: 生成されたToDoリストの辞書データ（JSONパース済）
              失敗した場合は空の辞書またはエラー情報を含む辞書を返す
    """
    client = get_openai_client()
    if not client:
        return {"error": "APIクライアントの初期化エラー", "todos": []}

    system_prompt = """
あなたは優秀なタスク管理アシスタントです。
ユーザーから提供されたOCRのテキストデータを分析し、ToDoリストを作成してください。
出力は必ず以下の構造を持つJSON形式で返してください。それ以外のテキストやMarkdownの装飾（```json など）は含めないでください。

【出力JSONフォーマット例】
{
  "todos": [
    {
      "task": "牛乳を買う",
      "status": "todo"
    },
    {
      "task": "企画書を提出する",
      "status": "todo"
    }
  ]
}
"""

    user_prompt = f"以下のテキストからToDoリストを作成してください:\n\n{ocr_text}"

    try:
        # OpenAI API呼び出し (他のモデルにする場合はここを変更)
        response = client.chat.completions.create(
            model="gpt-4o-mini", # または "gpt-3.5-turbo", "gpt-4o" など
            response_format={ "type": "json_object" }, # JSON出力を強制
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3, # タスク抽出なので低めに設定
        )

        result_text = response.choices[0].message.content
        
        # JSON文字列を辞書オブジェクトに変換して返す
        todo_data = json.loads(result_text)
        return todo_data

    except Exception as e:
        print(f"LLMでの処理中にエラーが発生しました: {e}")
        return {"error": str(e), "todos": []}


# --- 動作確認用 ---
if __name__ == "__main__":
    # テスト実行用のダミーOCRテキスト
    # dummy_ocr_text = \"\"\"
    # 今日の予定：
    # 10:00 会議
    # スーパーで卵と牛乳を買うこと
    # 鈴木さんにメールを返信する
    # \"\"\"
    
    print("--- テスト実行 (LLM API呼び出し) ---")
    if not os.environ.get("OPENAI_API_KEY"):
        print("注意: OPENAI_API_KEY が環境変数に設定されていません。")
        print("APIキーを設定してから実行してください。")
    else:
        print("OpenAI APIにリクエストを送信中...")
        result = generate_todo_list(dummy_ocr_text)
        print("\n--- 結果 ---")
        # 見やすく出力
        print(json.dumps(result, indent=2, ensure_ascii=False))
