import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# モジュール読み込み時に環境変数をロード（既存の環境変数を上書き）
load_dotenv(override=True)

# ----------------------------------------------------------------------
# 【プロバイダー変更のお知らせ】
# Google Gemini の不安定さを解消するため、Groq (Llama 3) に切り替えました。
# OpenAI SDK を使用して Groq Cloud に接続します。
# 環境変数 GROQ_API_KEY が必要です。
# ----------------------------------------------------------------------

def get_llm_client():
    """
    Groqクライアント（OpenAI SDK互換）の初期化
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        api_key = api_key.strip().strip("'").strip('"')
        
    if not api_key:
        print("エラー: GROQ_API_KEY が設定されていません。")
        return None
        
    try:
        # Groq は OpenAI SDK と互換性があります
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )
        return client
    except Exception as e:
        print(f"LLMクライアントの初期化に失敗しました: {e}")
        return None


def generate_todo_list(ocr_text: str) -> dict:
    """
    OCRから抽出されたテキストを受け取り、LLMにToDoリストをJSONで生成させる関数
    """
    client = get_llm_client()
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
        # Groq API呼び出し (llama-3.3-70b は非常に高性能で高速です)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"} # JSONモードを有効化
        )

        result_text = response.choices[0].message.content.strip()
        
        # JSON文字列を辞書オブジェクトに変換
        try:
            todo_data = json.loads(result_text)
        except json.JSONDecodeError:
            return {
                "todos": [],
                "markdown": f"AIの応答形式が正しくありませんでした:\n{result_text}",
                "error": "JSON_PARSE_ERROR"
            }

        if "todos" not in todo_data:
            todo_data["todos"] = []
        
        # Markdown生成
        md = "### AI抽出されたToDoリスト (by Groq)\n"
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
        print(f"LLM Error Details: {error_msg}")
        return {
            "error": error_msg, 
            "todos": [], 
            "markdown": f"LLMでの処理中にエラーが発生しました: {error_msg}"
        }


# --- 動作確認用 ---
if __name__ == "__main__":
    dummy_ocr_text = """
    今日の予定：
    10:00 会議
    スーパーで卵と牛乳を買うこと
    鈴木さんにメールを返信する
    """
    print("--- Groq テスト実行 ---")
    result = generate_todo_list(dummy_ocr_text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
