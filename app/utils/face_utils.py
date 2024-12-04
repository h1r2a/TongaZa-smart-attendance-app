import face_recognition
import numpy as np
from PIL import Image
import io
import os

ENCODINGS_DIR = "face_encodings"
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
