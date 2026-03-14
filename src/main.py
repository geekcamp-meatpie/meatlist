from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

from app.ocr import ocr_from_image
from app.todo_generator import generate_todo_with_llm
from app.utils import is_allowed_file

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
