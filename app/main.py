from PIL import Image
from meatpie.app.ocr import main as ocr
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
Target_image = upload_file or camera_file
def Return_file():
    return Target_image
