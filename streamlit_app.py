from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
from random import randint
import uuid
import io
from PIL import Image
import pytesseract
import numpy as np
import cv2

# Assurez-vous que python-multipart est installé pour gérer les fichiers
from fastapi import HTTPException

# Dossier pour sauvegarder les images téléchargées
IMAGEDIR = "images/"

# Créez une instance de FastAPI
app = FastAPI()

# Assurez-vous que le dossier pour les images existe
os.makedirs(IMAGEDIR, exist_ok=True)

# Fonction pour convertir l'image PIL en OpenCV
def convert_to_cv2(pil_image):
    """Convert a PIL Image to an OpenCV image (numpy array)."""
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

# Fonction pour extraire le texte d'une image
def process_image(image: io.BytesIO):
    # Convertir l'image en format PIL
    img = Image.open(image)
    img_cv = convert_to_cv2(img)  # Conversion PIL en OpenCV
    # Appliquer un traitement si nécessaire, comme convertir en gris
    gray_image = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    # Extraire le texte avec Tesseract
    text = pytesseract.image_to_string(gray_image)
    return text

# Endpoint de l'API pour télécharger et traiter l'image
@app.post("/extract_text/")
async def extract_text(file: UploadFile = File(...)):
    try:
        # Lire le fichier téléchargé
        contents = await file.read()
        image_stream = io.BytesIO(contents)

        # Traiter l'image et extraire le texte
        extracted_text = process_image(image_stream)
        extract_text ="test"
        # Retourner le texte extrait
        return JSONResponse(content={"extracted_text": extracted_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint pour télécharger une image et la sauvegarder
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Générer un nom unique pour le fichier
        filename = f"{uuid.uuid4()}.jpg"
        contents = await file.read()

        # Sauvegarder le fichier dans le répertoire d'images
        with open(f"{IMAGEDIR}{filename}", "wb") as f:
            f.write(contents)

        return {"filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint pour récupérer une image aléatoire depuis le répertoire
@app.get("/show/")
async def read_random_file():
    try:
        # Obtenir une image aléatoire depuis le répertoire
        files = os.listdir(IMAGEDIR)
        if not files:
            raise HTTPException(status_code=404, detail="No images found")
        
        random_index = randint(0, len(files) - 1)
        path = f"{IMAGEDIR}{files[random_index]}"
        
        return FileResponse(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
