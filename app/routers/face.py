from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from bson import ObjectId
from database import db
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import datetime
import face_recognition
import os
import numpy as np
from pathlib import Path
import shutil
from PIL import Image, ImageDraw
import io

router = APIRouter()

PDP_DIR = "../front/public/uploads/profile"
Path(PDP_DIR).mkdir(parents=True, exist_ok=True)


ENCODINGS_DIR = "../face_encodings"
os.makedirs(ENCODINGS_DIR, exist_ok=True)
def str_object_id(id: ObjectId):
    return str(id)

class Pointage(BaseModel):
    individu_id: str
    time: datetime.datetime
    type: str  # 'entry' ou 'exit'

    class Config:
        json_encoders = {
            ObjectId: str
        }
@router.post("/verify_face_metadata/")
async def verify_face_metadata(file: UploadFile = File(...), type: str = Form(...)):
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
                    # Extraire l'ID de la personne (nom du fichier sans "_encoding.npy")
                    individu_id = filename.replace("_encoding.npy", "")
                    
                    # Trouver l'individu dans la base de données pour obtenir le nom
                    individu = await db.individu.find_one({"id": individu_id})
                    if individu is None:
                        raise HTTPException(status_code=404, detail="Individu not found in database")

                    # Ajouter le pointage (entrée ou sortie) dans la base de données
                    pointage = Pointage(individu_id=str_object_id(individu['_id']), time=datetime.datetime.now(), type=type)
                    await db.pointage.insert_one(pointage.dict())

                    # Retourner le nom de la personne et une confirmation de pointage
                    if type == "entry":
                        message = f"{individu['name']} has entered at {pointage.time.strftime('%H:%M:%S')}."
                    elif type == "exit":
                        message = f"{individu['name']} has exited at {pointage.time.strftime('%H:%M:%S')}."
                    else:
                        message = f"Face recognized as {individu['name']} and {type} pointage recorded."

                    # Retourner le message en format JSON avec un code de statut 200
                    return JSONResponse(
                        content={"message": message},
                        status_code=200
                    )

        # Si aucune correspondance n'est trouvée
        raise HTTPException(status_code=400, detail="No matching face found.")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)






@router.post("/verify_face/")
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
                    image_with_box.save(byte_io, format="JPEG", quality=100)
                    byte_io.seek(0)

                    return StreamingResponse(byte_io, media_type="image/jpeg")

        # Si aucune correspondance n'est trouvée
        raise HTTPException(status_code=400, detail="No matching face found.")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)