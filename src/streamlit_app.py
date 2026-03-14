import streamlit as st
from PIL import Image
import json

try:
    from ocr import ocr_from_image
    from llm import generate_todo_list
except ImportError:
    from .ocr import ocr_from_image
    from .llm import generate_todo_list

# =========================================
# ページ設定
# =========================================
st.set_page_config(
    page_title="みーとぅーりすと🍖",
    page_icon="🍖",
    layout="wide"
)

st.title("みーとぅーりすと🍖")
st.caption("手書きメモ・ノート・ホワイトボードの画像をアップロードして、Todoリストに変換します")

st.divider()

# =========================================
# 画像入力（タブで選択・撮影を切替）
# =========================================
st.subheader("📷 写真を読み込む")

tab1, tab2 = st.tabs(["📁 ファイルから選択", "📸 カメラで撮影"])

uploaded_image = None  # 最終的に使う画像

with tab1:
    upload_file = st.file_uploader(
        "画像を選択してください",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )
    if upload_file:
        uploaded_image = Image.open(upload_file)

with tab2:
    camera_file = st.camera_input("カメラでメモを撮ってください")
    if camera_file:
        uploaded_image = Image.open(camera_file)

# =========================================
# メイン処理（画像が選択された場合）
# =========================================
if uploaded_image:
    st.divider()

    # 左右レイアウト
    col_left, col_right = st.columns([1, 1], gap="large")

    # ---- 左：アップロード画像 ----
    with col_left:
        st.subheader("🖼️ アップロード画像")
        st.image(uploaded_image, use_container_width=True)

    # ---- 右：AI解析結果 ----
    with col_right:
        st.subheader("✅ AI解析結果")

        # セッションに結果をキャッシュ（再実行防止）
        if "result" not in st.session_state or st.session_state.get("last_image") != id(uploaded_image):
            with st.spinner("AIが解析中...（5〜15秒かかります）"):
                try:
                    # OCR実行
                    ocr_text = ocr_from_image(uploaded_image)

                    if not ocr_text:
                        st.warning("テキストを検出できませんでした。別の画像をお試しください。")
                        st.stop()

                    # LLMでTodo生成
                    result = generate_todo_list(ocr_text)

                    # セッションに保存
                    st.session_state["result"] = result
                    st.session_state["ocr_text"] = ocr_text
                    st.session_state["last_image"] = id(uploaded_image)

                except RuntimeError as e:
                    st.error(f"OCRエラー: {e}")
                    st.stop()
                except Exception as e:
                    st.error(f"処理中にエラーが発生しました: {e}")
                    st.stop()

        result = st.session_state["result"]
        ocr_text = st.session_state["ocr_text"]

        # もし結果にエラーが含まれていれば警告を表示
        if result.get("error"):
            st.warning(result.get("markdown", "AIの処理でエラーが発生しました。"))

        # OCR生テキスト（折りたたみ）
        with st.expander("🔍 OCR読み取り結果（生テキスト）"):
            st.text(ocr_text)

        # Markdown / JSON タブ切替
        tab_md, tab_json = st.tabs(["📋 Markdown", "{ } JSON"])

        with tab_md:
            markdown_text = result.get("markdown", "Markdown形式のデータが生成されませんでした。")
            st.code(markdown_text, language="markdown")

            # .md ダウンロード
            st.download_button(
                label="💾 .md としてダウンロード",
                data=markdown_text,
                file_name="todo.md",
                mime="text/markdown",
                use_container_width=True
            )

        with tab_json:
            todos = result.get("todos", [])
            json_text = json.dumps(todos, ensure_ascii=False, indent=2)
            st.code(json_text, language="json")

            # .json ダウンロード
            st.download_button(
                label="💾 .json としてダウンロード",
                data=json_text,
                file_name="todo.json",
                mime="application/json",
                use_container_width=True
            )

else:
    # 画像未選択時のガイダンス
    st.info("👆 上のタブから画像を選択またはカメラで撮影してください")
    st.markdown("""
    **対応している画像の例**
    - 📝 手書きメモ
    - 📓 ノート
    - 🖊️ ホワイトボード
    - 📄 印刷された文書
    - 📋 会議メモ
    """)
