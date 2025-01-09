import streamlit as st
import io
from PIL import Image
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from io import BytesIO

# Créez une instance de FastAPI
app = FastAPI()

# Fonction pour convertir une image PIL en OpenCV
def convert_to_cv2(pil_image):
    """Convert a PIL Image to an OpenCV image (numpy array)."""
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

# Fonction pour convertir une image en niveaux de gris
def grayscale(image):
    """Convert an OpenCV image to grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Fonction pour simuler la reconnaissance de texte avec Tesseract
def image_to_string(image, language='eng'):
    """Simulate text extraction using Tesseract (replace with actual Tesseract call)."""
    # Simulez ici une extraction de texte ou utilisez pytesseract
    import pytesseract
    return pytesseract.image_to_string(image, lang=language)

# Fonction pour traiter l'image et extraire le texte
def process_image(image: BytesIO, language: str = 'eng'):
    # Convertir l'image en format compatible avec OpenCV
    img = Image.open(image)
    img = convert_to_cv2(img)  # Conversion PIL en OpenCV
    # Appliquer un traitement sur l'image si nécessaire
    processed_image = grayscale(img)
    text = image_to_string(processed_image, language=language)
    return text

# Endpoint de l'API pour traiter l'image et renvoyer le texte extrait
@app.post("/extract_text/", response_model=None)
async def extract_text(file: UploadFile = File(...)):
    # Charger le fichier et traiter l'image
    image_bytes = await file.read()
    extracted_text = process_image(BytesIO(image_bytes))
    byte_stream = BytesIO(extracted_text.encode())
    return StreamingResponse(byte_stream, media_type="application/octet-stream")

# Pour démarrer l'application Streamlit
if __name__ == "__main__":
    st.title("Tesseract OCR API")

    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"])
    if uploaded_file is not None:
        image = uploaded_file.read()
        st.image(image, caption="Uploaded Image", use_column_width=True)
        if st.button("Extract Text"):
            extracted_text = process_image(io.BytesIO(image))
            st.text_area("Extracted Text", value=extracted_text, height=300)
