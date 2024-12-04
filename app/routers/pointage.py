from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import db
import datetime
from utils.serializers import serialize_individu
from bson import ObjectId
router = APIRouter()

class Pointage(BaseModel):
    individu_id: str
    time: datetime.datetime
    type: str  # 'entry' ou 'exit'

    class Config:
        json_encoders = {
            ObjectId: str
        }

    
class PointageResponse(BaseModel):
    name: str
    type: str
    date: str  # La date sans l'heure
    time: str 
    

def serialize_individu(individu):
    individu["_id"] = str(individu["_id"])  # Convertit ObjectId en chaîne
    return individu

@router.post("/")
async def add_pointage(pointage: Pointage):
    pointage_dict = pointage.dict()
    pointage_dict["time"] = datetime.now()
    await db.pointage.insert_one(pointage_dict)
    return {"message": "Pointage added successfully"}

# @router.get("/{individu_id}")
# async def get_pointages(individu_id: str):
#     pointages = await db.pointage.find({"individu_id": individu_id}).to_list(100)
#     if not pointages:
#         raise HTTPException(status_code=404, detail="No pointages found for this individual")
#     return [serialize_pointage(p) for p in pointages]



from bson import ObjectId  # Importer ObjectId depuis bson

@router.get("/get_pointages", response_model=List[PointageResponse])
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

