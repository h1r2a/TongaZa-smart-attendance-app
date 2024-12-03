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

# Création de l'application FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet toutes les origines (remplacez "*" par des domaines spécifiques si nécessaire)
    allow_credentials=True,
    allow_methods=["*"],  # Permet toutes les méthodes HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permet tous les en-têtes
)

# Configuration de la connexion à MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["attendance_db"]

# Répertoire où nous enregistrerons les encodages des visages
ENCODINGS_DIR = "face_encodings"
Path(ENCODINGS_DIR).mkdir(parents=True, exist_ok=True)  # Crée le répertoire si il n'existe pas

class PointageResponse(BaseModel):
    name: str
    type: str
    date: str  # La date sans l'heure
    time: str  #

# Fonction pour convertir l'ID de MongoDB en string
def str_object_id(id: ObjectId):
    return str(id)

# Schéma pour les individus
class Individu(BaseModel):
    name: str
    id: str

    class Config:
        json_encoders = {
            ObjectId: str
        }


# Schéma pour les pointages
class Pointage(BaseModel):
    individu_id: str
    time: datetime.datetime
    type: str  # 'entry' ou 'exit'

    class Config:
        json_encoders = {
            ObjectId: str
        }

# Vérification si le visage est déjà enregistré
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


# CRUD pour les individus

@app.post("/add_individu/")
async def add_individu(individu: Individu):
    individu_dict = individu.dict()
    individu_dict["id"] = str(ObjectId())  # Créer un id unique pour chaque individu
    await db.individu.insert_one(individu_dict)
    return {"message": "Individu added successfully", "id": individu_dict["id"]}

@app.get("/get_individu/{individu_id}")
async def get_individu(individu_id: str):
    individu = await db.individu.find_one({"id": individu_id})
    if individu is None:
        raise HTTPException(status_code=404, detail="Individu not found")
    return individu

@app.put("/update_individu/{individu_id}")
async def update_individu(individu_id: str, name: str = Form(...)):
    updated_individu = await db.individu.find_one_and_update(
        {"id": individu_id},
        {"$set": {"name": name}},
        return_document=True
    )
    if updated_individu is None:
        raise HTTPException(status_code=404, detail="Individu not found")
    return updated_individu

@app.delete("/delete_individu/{individu_id}")
async def delete_individu(individu_id: str):
    result = await db.individu.delete_one({"id": individu_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Individu not found")
    return {"message": "Individu deleted successfully"}
# Endpoint pour récupérer tous les individus


def serialize_individu(individu):
    individu["_id"] = str(individu["_id"])  # Convertit ObjectId en chaîne
    return individu

@app.get("/get_all_individus/")
async def get_all_individus():
    try:
        individus = await db.individu.find().to_list(length=100)  # Limite à 100 résultats
        if not individus:
            raise HTTPException(status_code=404, detail="No individus found")
        
        # Sérialiser tous les individus pour convertir ObjectId en chaîne
        return [serialize_individu(individu) for individu in individus]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# CRUD pour les pointages

@app.post("/add_pointage/")
async def add_pointage(pointage: Pointage):
    pointage_dict = pointage.dict()
    pointage_dict["time"] = datetime.datetime.now()  # Ajouter l'heure actuelle
    await db.pointage.insert_one(pointage_dict)
    return {"message": "Pointage added successfully"}

@app.get("/get_pointages/{individu_id}")
async def get_pointages(individu_id: str):
    pointages = await db.pointage.find({"individu_id": individu_id}).to_list(length=100)
    if not pointages:
        raise HTTPException(status_code=404, detail="No pointages found for this individual")
    return pointages


# Endpoint POST pour recevoir une image et enregistrer l'empreinte du visage
@app.post("/upload_face/")
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



from bson import ObjectId  # Importer ObjectId depuis bson

@app.get("/get_pointages", response_model=List[PointageResponse])
async def get_pointages():
    # Recherche de tous les pointages dans la collection "pointages"
    pointages = await db.pointage.find().sort("time", -1).limit(10).to_list(length=10)
    
    if not pointages:
        raise HTTPException(status_code=404, detail="No pointages found")
    
    # Formater les résultats
    formatted_pointages = []
    for pointage in pointages:
        # Récupérer l'individu_id pour chaque pointage
        individu_id = pointage.get('individu_id')
        
        try:
            # Convertir l'individu_id en ObjectId
            individu_object_id = ObjectId(individu_id)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid individu_id format: {individu_id}")
        
        # Récupérer le nom de l'individu dans la collection "individus" via l'ObjectId
        individu = await db.individu.find_one({"_id": individu_object_id})
        if not individu:
            raise HTTPException(status_code=404, detail=f"Individu with ID {individu_id} not found")
        
        # Extraire le nom de l'individu
        name = individu.get('name', 'Unknown')
        
        # Extraire le type de pointage et la date/heure
        type_pointage = pointage.get('type', 'Unknown')
        
        # Extraction de la date (sans l'heure)
        date_pointage = pointage.get('time', datetime).strftime("%Y-%m-%d")
        
        # Extraction de l'heure (sans la date)
        time_pointage = pointage.get('time', datetime).strftime("%H:%M:%S")
        
        # Ajouter le pointage formaté à la liste
        formatted_pointages.append(PointageResponse(name=name, type=type_pointage, date=date_pointage, time=time_pointage))
    
    return formatted_pointages




# Endpoint pour vérifier le visage et ajouter un pointage
@app.post("/verify_face_metadata/")
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
                    image_with_box.save(byte_io, format="JPEG", quality=100)
                    byte_io.seek(0)

                    return StreamingResponse(byte_io, media_type="image/jpeg")

        # Si aucune correspondance n'est trouvée
        raise HTTPException(status_code=400, detail="No matching face found.")

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)



@app.post("/upload_pdp/")
async def upload_pdp(
    individu_id: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        # Répertoire pour stocker les photos de profil
        PDP_DIR = "front/public/uploads/profile"
        Path(PDP_DIR).mkdir(parents=True, exist_ok=True)  # Crée le répertoire si inexistant

        # Vérifie si l'individu existe dans la base de données
        individu = await db.individu.find_one({"id": individu_id})
        if not individu:
            raise HTTPException(status_code=404, detail="Individu not found")

        # Nom du fichier basé sur l'individu_id
        file_extension = file.filename.split(".")[-1]  # Récupère l'extension du fichier
        if file_extension.lower() not in ["jpg", "jpeg", "png"]:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        filename = f"{individu_id}.{file_extension}"
        file_path = os.path.join(PDP_DIR, filename)

        # Sauvegarde le fichier sur le disque
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Met à jour l'individu avec le chemin de la photo
        await db.individu.update_one(
            {"id": individu_id},
            {"$set": {"imageFile": filename}}
        )

        return {"message": "Photo uploaded successfully", "file_path": file_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
