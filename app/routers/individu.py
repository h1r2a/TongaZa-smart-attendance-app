from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from bson import ObjectId
from database import db
from utils.serializers import serialize_individu
from bson import ObjectId
from fastapi import Query



router = APIRouter()

class Individu(BaseModel):
    name: str
    id: str

    class Config:
        json_encoders = {
            ObjectId: str
        }

@router.post("/add_individu")
async def add_individu(individu: Individu):
    individu_dict = individu.dict()
    individu_dict["id"] = str(ObjectId())
    await db.individu.insert_one(individu_dict)
    return {"message": "Individu added successfully", "id": individu_dict["id"]}

@router.get("/get_individu/{individu_id}")
async def get_individu(individu_id: str):
    individu = await db.individu.find_one({"id": individu_id})
    if not individu:
        raise HTTPException(status_code=404, detail="Individu not found")
    return serialize_individu(individu)

@router.put("/update_individu/{individu_id}")
async def update_individu(individu_id: str, name: str = Form(...)):
    updated_individu = await db.individu.find_one_and_update(
        {"id": individu_id},
        {"$set": {"name": name}},
        return_document=True
    )
    if not updated_individu:
        raise HTTPException(status_code=404, detail="Individu not found")
    return serialize_individu(updated_individu)

@router.delete("/delete_individu/{individu_id}")
async def delete_individu(individu_id: str):
    result = await db.individu.delete_one({"id": individu_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Individu not found")
    return {"message": "Individu deleted successfully"}


def serialize_individu(individu):
    individu["_id"] = str(individu["_id"])  # Convertit ObjectId en chaîne
    return individu


@router.get("/get_all_individus")
async def get_all_individus(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(8, ge=1, le=100, description="Number of items per page (max 100)")
):
    try:
        # Calculer les valeurs pour le skip et la limite
        skip = (page - 1) * page_size
        limit = page_size

        # Récupérer les individus en fonction de la pagination
        individus = await db.individu.find().skip(skip).limit(limit).to_list(length=limit)
        total_count = await db.individu.count_documents({})  # Nombre total d'individus

        if not individus:
            raise HTTPException(status_code=404, detail="No individus found")
        
        # Sérialiser les individus et ajouter des métadonnées
        return {
            "data": [serialize_individu(individu) for individu in individus],
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size,  # Arrondi vers le haut
            "total_items": total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

