from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import individu, pointage, upload, face
from database import db  # Importer la connexion à la base de données

# Initialiser l'application FastAPI
app = FastAPI()

# Configuration du middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vous pouvez restreindre ces origines selon vos besoins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routes
app.include_router(individu.router)
app.include_router(pointage.router)
app.include_router(upload.router)
app.include_router(face.router)
