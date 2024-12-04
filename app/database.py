from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

# Remplacez par votre URI MongoDB
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "your_database_name"

# Créer une instance du client MongoDB
client = AsyncIOMotorClient(MONGO_URI)

# Accéder à la base de données
db = client["attendance_db"]
