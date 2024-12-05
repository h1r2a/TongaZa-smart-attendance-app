from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from database import db
from pathlib import Path
import os
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
from bson import ObjectId
router = APIRouter()

PDP_DIR = "../front/public/uploads/profile"
Path(PDP_DIR).mkdir(parents=True, exist_ok=True)


ENCODINGS_DIR = "../face_encodings"
os.makedirs(ENCODINGS_DIR, exist_ok=True)

def is_face_registered(file_data: bytes):
    try:
        # Convertir l'image reçue en tableau compréhensible par face_recognition
        image = Image.open(io.BytesIO(file_data))
        image_array = np.array(image)

        # Détecter les visages dans l'image
        face_locations = face_recognition.face_locations(image_array)
        if len(face_locations) == 0:
            return False

        # Extraire les encodages des visages détectés
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        if len(face_encodings) == 0:
            return False

        # Comparer avec les encodages enregistrés
        for filename in os.listdir(ENCODINGS_DIR):
            if filename.endswith("_encoding.npy"):
                saved_encoding = np.load(os.path.join(ENCODINGS_DIR, filename))
                matches = face_recognition.compare_faces([saved_encoding], face_encodings[0])
                if True in matches:
                    return True  # Si une correspondance est trouvée, le visage est déjà enregistré

        return False

    except Exception as e:
        return False


@router.post("/upload_pdp/")
async def upload_pdp(individu_id: str = Form(...), file: UploadFile = File(...)):
    individu = await db.individu.find_one({"id": individu_id})
    if not individu:
        raise HTTPException(status_code=404, detail="Individu not found")

    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    filename = f"{individu_id}.{file_extension}"
    file_path = os.path.join(PDP_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    await db.individu.update_one({"id": individu_id}, {"$set": {"imageFile": filename}})
    return {"message": "Photo uploaded successfully", "file_path": file_path}


@router.post("/upload_face/")
async def upload_face(file: UploadFile = File(...), name: str = Form(...)):
    try:
        # Lire l'image envoyée dans la requête
        image_data = await file.read()

        # Vérifier si le visage est déjà enregistré
        if is_face_registered(image_data):
            raise HTTPException(status_code=400, detail="Face already registered")

        # Convertir l'image en un tableau compréhensible par face_recognition
        image = Image.open(io.BytesIO(image_data))
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

@router.delete("/delete_encoding/{name}")
async def delete_encoding(name: str):
    try:
        # Define the path to the encoding file
        encoding_file_path = os.path.join(ENCODINGS_DIR, f"{name}_encoding.npy")

        # Check if the encoding file exists
        if not os.path.exists(encoding_file_path):
            raise HTTPException(status_code=404, detail="Encoding file not found")

        # Delete the file
        os.remove(encoding_file_path)

        return {"message": f"Encoding file {name}_encoding.npy deleted successfully"}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
