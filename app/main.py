from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

from ocr import ocr_from_image
from todo_generator import generate_todo_with_llm
from utils import is_allowed_file

app = FastAPI(
    title="Meatlist API",
    description="画像からAI-OCRで文字を抽出し、Todoリストを生成するAPI",
    version="1.0.0"
)

# CORS設定（スマホフロントからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """ヘルスチェック"""
    return {"status": "ok", "message": "Meatlist API is running"}


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
        response = ocr(target_image)
        if response.get("task"):
            for i, item in enumerate(response["task"]):
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
