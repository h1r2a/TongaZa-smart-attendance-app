import face_recognition
import pickle
import cv2

# Charger les encodages enregistrés
with open("known_faces_encodings.pkl", "rb") as f:
    known_face_encodings, known_face_names = pickle.load(f)

# Capturer l'image via la webcam
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    
    # Trouver tous les visages dans l'image de la webcam
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Comparer les visages capturés avec les visages connus
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        name = "Inconnu"
        
        # Si une correspondance est trouvée, on récupère le nom
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
        
        # Dessiner un rectangle autour du visage et afficher le nom
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    # Afficher l'image avec les visages et le nom
    cv2.imshow('Video', frame)

    # Quitter si la touche 'q' est pressée
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer la caméra et fermer les fenêtres
video_capture.release()
cv2.destroyAllWindows()
