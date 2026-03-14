
from ocr import main as ocr
print(f"取得:{ocr.Text_json}")

import streamlit as st

st.title("みーとぅーりすと🍖")

st.subheader("写真を読み込む")

tab1, tab2 = st.tabs(["ファイルから選択", "カメラで撮影"])

with tab1:
    # ファイル選択
    upload_file = st.file_uploader("画像を選択してください", type=['png', 'jpg', 'jpeg'])
    if upload_file:
        img = Image.open(upload_file)
        st.image(img, caption="アップロードされた画像", use_container_width=True)

with tab2:
    # カメラ起動
    camera_file = st.camera_input("カメラでメモを撮ってください")
    if camera_file:
        img = Image.open(camera_file)
        st.image(img, caption="撮影された画像", use_container_width=True)
                                                  #↑画像の大きさ自動調節
target_image = upload_file or camera_file

if st.button("みーとぅーりすとを作成🍖", type="primary"):
    with st.spinner("作成中"):
        response = photo_capture(target_image)
        if response.get("txt_data"):
            task_list=response[txt_data].splitlines()
            for i, item in enumerate(task_list):
                if item.strip():
             st.checkbox(item, key=f"todo_{i}")
@app.post("/ocr")
async def process_image(file: UploadFile = File(...)):
    """
    画像をアップロードし、OCR → Todo生成を行う

    - 入力: 画像ファイル (jpg/jpeg/png)
    - 出力: OCRテキスト + Todoリスト (JSON + Markdown)
    """
    # ファイル形式チェック
    if not file.filename or not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="対応していないファイル形式です。jpg, jpeg, png のみ対応しています。"
        )

    try:
        # 画像を読み込み
        contents = await file.read()
        pil_image = Image.open(io.BytesIO(contents))

        # OCR実行
        ocr_text = ocr_from_image(pil_image)

        if not ocr_text:
            return {
                "ocr_text": "",
                "tasks": [],
                "markdown": ""
            }

        # LLMでTodo生成
        result = generate_todo_with_llm(ocr_text)

        return {
            "ocr_text": ocr_text,
            "tasks": result["tasks"],
            "markdown": result["markdown"]
        }

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"処理中にエラーが発生しました: {str(e)}")
