from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

# パッケージベースのインポートを使用（srcディレクトリがパスに含まれている前提）
try:
    from ocr import ocr_from_image
    from llm import generate_todo_list
    from utils import is_allowed_file
except ImportError:
    # 実行環境によってパスが異なる場合のフォールバック
    from .ocr import ocr_from_image
    from .llm import generate_todo_list
    from .utils import is_allowed_file


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

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """画像をアップロードしてTodoリストを生成する"""
    if not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="許可されていないファイル形式です")
    
    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        
        # OCR実行
        ocr_text = ocr_from_image(image)
        
        if not ocr_text:
            return {"todos": [], "markdown": "", "message": "テキストを検出できませんでした"}
            
        # LLM実行
        result = generate_todo_list(ocr_text)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
