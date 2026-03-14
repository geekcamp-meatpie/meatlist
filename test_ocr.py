from app.ocr import ocr_from_image
from PIL import Image

try:
    img = Image.open('resized_image.png')
    text = ocr_from_image(img)
    print("SUCCESS:")
    print(text[:100])
except Exception as e:
    import traceback
    traceback.print_exc()
