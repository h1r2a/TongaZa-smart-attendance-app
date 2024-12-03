from fastapi import FastAPI, File, UploadFile, HTTPException , Form
from fastapi.responses import JSONResponse, StreamingResponse
import face_recognition
import os
import numpy as np
from pathlib import Path
import shutil
from PIL import Image, ImageDraw
import io

# Création de l'application FastAPI
app = FastAPI()

# Répertoire où nous enregistrerons les encodages des visages
ENCODINGS_DIR = "face_encodings"
Path(ENCODINGS_DIR).mkdir(parents=True, exist_ok=True)  # Crée le répertoire si il n'existe pas

# Endpoint POST pour recevoir une image et enregistrer l'empreinte du visage
@app.post("/upload_face/")
async def upload_face(file: UploadFile = File(...), name: str = Form(...)):
    try:
        # Lire l'image envoyée dans la requête
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Convertir l'image en un tableau compréhensible par face_recognition
        image_array = np.array(image)

        # Détecter les visages dans l'image
        face_locations = face_recognition.face_locations(image_array)
        if len(face_locations) == 0:
            raise HTTPException(status_code=400, detail="No face detected")

        # Extraire les encodages des visages détectés
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        if len(face_encodings) == 0:
            raise HTTPException(status_code=400, detail="No face encodings found")

        # Nom de fichier basé sur le nom fourni (clé)
        encoding_filename = os.path.join(ENCODINGS_DIR, f"{name}_encoding.npy")

        # Sauvegarder l'empreinte du visage dans un fichier
        np.save(encoding_filename, face_encodings[0])  # Enregistrer le premier visage (si plusieurs sont détectés)

        return JSONResponse(content={"message": f"Face encoding saved as {encoding_filename}"}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)



@app.post("/verify_face/")
async def verify_face(file: UploadFile = File(...)):
    try:
        # Lire l'image envoyée dans la requête
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Convertir l'image en un tableau compréhensible par face_recognition
        image_array = np.array(image)

        # Détecter les visages dans l'image
        face_locations = face_recognition.face_locations(image_array)
        if len(face_locations) == 0:
            raise HTTPException(status_code=400, detail="No face detected in the image.")

        # Extraire les encodages des visages détectés
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        if len(face_encodings) == 0:
            raise HTTPException(status_code=400, detail="No face encodings found.")

        # Charger les encodages des visages enregistrés et comparer
        for filename in os.listdir(ENCODINGS_DIR):
            if filename.endswith("_encoding.npy"):
                # Charger l'encodage enregistré
                saved_encoding = np.load(os.path.join(ENCODINGS_DIR, filename))

                # Comparer l'encodage envoyé avec les encodages enregistrés
                matches = face_recognition.compare_faces([saved_encoding], face_encodings[0])

                if True in matches:  # Si une correspondance est trouvée
                    # Dessiner un carré vert autour du visage reconnu
                    top, right, bottom, left = face_locations[0]
                    image_with_box = image.copy()
                    draw = ImageDraw.Draw(image_with_box)
                    draw.rectangle([left, top, right, bottom], outline="green", width=5)

                    # Réduire la taille de l'image avant de la renvoyer (par exemple, réduire à 50% de la taille originale)
                    image_with_box = image_with_box.resize((image_with_box.width // 2, image_with_box.height // 2))

                    # Compresser l'image en format JPEG avec une qualité de 75 (à ajuster)
                    byte_io = io.BytesIO()
                    image_with_box.save(byte_io, format="JPEG", quality=50)
                    byte_io.seek(0)

                    return StreamingResponse(byte_io, media_type="image/jpeg")

        # Si aucune correspondance n'est trouvée
        raise HTTPException(status_code=400, detail="No matching face found.")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/verify_face_metadata/")
async def verify_face_metadata(file: UploadFile = File(...)):
    try:
        # Lire l'image envoyée dans la requête
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Convertir l'image en un tableau compréhensible par face_recognition
        image_array = np.array(image)

        # Détecter les visages dans l'image
        face_locations = face_recognition.face_locations(image_array)
        if len(face_locations) == 0:
            raise HTTPException(status_code=400, detail="No face detected in the image.")

        # Extraire les encodages des visages détectés
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        if len(face_encodings) == 0:
            raise HTTPException(status_code=400, detail="No face encodings found.")

        # Charger les encodages des visages enregistrés et comparer
        for filename in os.listdir(ENCODINGS_DIR):
            if filename.endswith("_encoding.npy"):
                # Charger l'encodage enregistré
                saved_encoding = np.load(os.path.join(ENCODINGS_DIR, filename))

                # Comparer l'encodage envoyé avec les encodages enregistrés
                matches = face_recognition.compare_faces([saved_encoding], face_encodings[0])

                if True in matches:  # Si une correspondance est trouvée
                    # Retourner le nom correspondant à l'encodage trouvé
                    name = filename.replace("_encoding.npy", "")
                    return JSONResponse(content={"message": f"Face recognized as {name}"}, status_code=200)

        # Si aucune correspondance n'est trouvée
        raise HTTPException(status_code=400, detail="No matching face found.")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)