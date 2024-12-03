import face_recognition
import pickle
import os

# Dossier où les images des personnes seront stockées
known_faces_dir = "known_faces"

# Dossier pour enregistrer les encodages des visages
encoding_file = "known_faces_encodings.pkl"

# Assurer que le dossier existe
if not os.path.exists(known_faces_dir):
    os.makedirs(known_faces_dir)

# Liste pour stocker les encodages et les noms
known_face_encodings = []
known_face_names = []

# Fonction pour enregistrer un visage
def enregistrer_visage(image_path, name):
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]
    
    known_face_encodings.append(encoding)
    known_face_names.append(name)

# Exemple d'enregistrement de personnes connues
enregistrer_visage("test.jpg", "Alice")
enregistrer_visage("bob.jpg", "Bob")

# Sauvegarder les encodages dans un fichier
with open(encoding_file, "wb") as f:
    pickle.dump((known_face_encodings, known_face_names), f)

print("Visages enregistrés avec succès !")
