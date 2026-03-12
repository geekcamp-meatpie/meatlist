import json
from openai import OpenAI
from utils import load_api_key


def generate_todo_with_llm(ocr_text: str) -> dict:
    """
    LLM（OpenAI）を使ってOCRテキストからTodoリストを生成する

    Args:
        ocr_text: OCRで抽出されたテキスト

    Returns:
        {
            "tasks": [{"task": "...", "status": "todo"}, ...],
            "markdown": "- [ ] ...\n- [ ] ..."
        }
    """
    api_key = load_api_key()

    if not api_key:
        # APIキー未設定時のフォールバック処理
        return _fallback_generate(ocr_text)

    try:
        client = OpenAI(api_key=api_key)

        prompt = f"""以下の文章からTodoリストを作成してください。

条件：
・1行1タスク
・不要な文章は削除
・重複するタスクは除去
・MarkdownとJSON両方で出力

以下のJSON形式で出力してください（他のテキストは一切出力しないでください）:
{{
  "tasks": [
    {{"task": "タスク内容", "status": "todo"}}
  ],
  "markdown": "- [ ] タスク内容"
}}

--- 文章 ---
{ocr_text}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはOCRテキストからTodoリストを抽出するアシスタントです。指定されたJSON形式のみで応答してください。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # tasks が存在しなければフォールバック
        if "tasks" not in result:
            return _fallback_generate(ocr_text)

        # markdown が無ければ tasks から生成
        if "markdown" not in result:
            result["markdown"] = _tasks_to_markdown(result["tasks"])

        return result

    except Exception as e:
        print(f"LLMエラー: {e}")
        return _fallback_generate(ocr_text)


def _fallback_generate(ocr_text: str) -> dict:
    """
    APIキー未設定時・エラー時のフォールバック処理
    OCRテキストを1行1タスクとしてそのまま整形する
    """
    lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]

    # 重複除去（順序を保持）
    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    tasks = [{"task": line, "status": "todo"} for line in unique_lines]
    markdown = '\n'.join([f"- [ ] {line}" for line in unique_lines])

    return {
        "tasks": tasks,
        "markdown": markdown
    }


def _tasks_to_markdown(tasks: list) -> str:
    """tasksリストからMarkdown形式を生成する"""
    return '\n'.join([f"- [ ] {t['task']}" for t in tasks])
