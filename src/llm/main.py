import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# モジュール読み込み時に環境変数をロード.
load_dotenv()

# ----------------------------------------------------------------------
# 【モデル変更時の注意点】
# LLMをGoogle Geminiに変更しました。最新の `google-genai` SDK を使用しています。
# 環境変数 GEMINI_API_KEY が必要です。
# ----------------------------------------------------------------------

def get_gemini_client():
    # 環境変数を再ロードして強制的に上書き
    import dotenv
    dotenv.load_dotenv(override=True)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        # クォート、空白、CRLFなどを徹底的に除去
        api_key = api_key.strip().strip("'").strip('"')
        # もし値の中に "GEMINI_API_KEY=" が紛れ込んでいたら除去
        if "=" in api_key:
            api_key = api_key.split("=")[-1].strip()
        # AIza以外の文字が先頭に含まれている場合のガード
        if "AIza" in api_key:
            api_key = api_key[api_key.find("AIza"):]
            
        print(f"DEBUG: Using API Key (length {len(api_key)}): {api_key[:10]}...{api_key[-5:] if len(api_key) > 5 else ''}")
    
    if not api_key:
        print("エラー: GEMINI_API_KEY が設定されていません。")
        return None
        
    try:
        # クライアント初期化
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        print(f"Geminiクライアントの初期化に失敗しました: {e}")
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
    client = get_gemini_client()
    if not client:
        return {
            "error": "APIクライアントの初期化エラー", 
            "todos": [], 
            "markdown": "APIクライアントの初期化に失敗しました。APIキーを確認してください。"
        }

    system_prompt = """
あなたは優秀なタスク管理アシスタントです。
ユーザーから提供されたOCRのテキストデータを分析し、ToDoリストをJSON形式で作成してください。

【抽出ルール】
- OCRのノイズ（記号の誤認、改行の乱れなど）を適切に無視してください。
- 文脈から明らかに「やるべきこと（タスク）」と思われる内容のみを抽出してください。

出力は必ず以下の構造を持つ純粋なJSON形式で返してください。それ以外のテキスト（「分かりました」など）やMarkdownの装飾（```json など）は絶対に含めないでください。

【出力JSONフォーマット】
{
  "todos": [
    {
      "task": "タスクの内容",
      "status": "todo"
    }
  ]
}
"""

    user_prompt = f"以下のテキストからToDoリストを抽出してください:\n\n{ocr_text}"

    try:
        # Gemini API呼び出し (1.5-flash を安定性のために使用。プレフィックスを明示)
        response = client.models.generate_content(
            model='gemini-2.0-flash', # もし失敗したら 'models/gemini-1.5-flash'
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
                response_mime_type='application/json'
            )
        )

        result_text = response.text.strip()
        
        # Markdownのコードブロックが含まれている場合のトリミング
        if result_text.startswith("```"):
            lines = result_text.splitlines()
            if lines[0].startswith("```json"):
                result_text = "\n".join(lines[1:-1])
            elif lines[0].startswith("```"):
                result_text = "\n".join(lines[1:-1])

        # JSON文字列を辞書オブジェクトに変換
        try:
            todo_data = json.loads(result_text)
        except json.JSONDecodeError:
            # パース失敗時のフォールバック
            return {
                "todos": [],
                "markdown": f"AIの応答形式が正しくありませんでした:\n{result_text}",
                "error": "JSON_PARSE_ERROR"
            }

        # 必要なキーが含まれているか確認し、無ければ補完
        if "todos" not in todo_data:
            todo_data["todos"] = []
        
        # MarkdownをPython側で生成（トークン節約と形式安定のため）
        md = "### AI抽出されたToDoリスト\n"
        if not todo_data["todos"]:
            md += "タスクが検出されませんでした。"
        else:
            for t in todo_data["todos"]:
                task_name = t.get("task", "不明なタスク")
                md += f"- [ ] {task_name}\n"
        
        todo_data["markdown"] = md
        return todo_data

    except Exception as e:
        error_msg = str(e)
        user_friendly_msg = "LLMでの処理中にエラーが発生しました。"
        
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            user_friendly_msg = "【制限エラー】Google APIの利用制限に達しました。30秒〜1分ほど待ってから再度お試しください。現在のAPIキーのステータスを確認してください。"
        
        # エラーの詳細はコンソールに出力してデバッグしやすくする
        import traceback
        print("-" * 50)
        print(f"LLM Raw Error Object: {repr(e)}")
        print(f"LLM Error Details:\n{traceback.format_exc()}")
        print(f"Using API Key: {os.environ.get('GEMINI_API_KEY', 'NotFound')[:4]}...")
        print("-" * 50)
        return {
            "error": error_msg, 
            "todos": [], 
            "markdown": user_friendly_msg
        }


# --- 動作確認用 ---
if __name__ == "__main__":

    load_dotenv()
    # テスト実行用のダミーOCRテキスト
    dummy_ocr_text = """
    今日の予定：
    10:00 会議
    スーパーで卵と牛乳を買うこと
    鈴木さんにメールを返信する
    """
    
    print("--- テスト実行 (LLM API呼び出し) ---")
    if not os.environ.get("GEMINI_API_KEY"):
        print("注意: GEMINI_API_KEY が環境変数に設定されていません。")
        print("APIキーを設定してから実行してください。")
    else:
        print("Gemini APIにリクエストを送信中...")
        result = generate_todo_list(dummy_ocr_text)
        print("\n--- 結果 ---")
        # 見やすく出力
        print(json.dumps(result, indent=2, ensure_ascii=False))
