import React, { useState, useRef, useEffect } from 'react';
import Navbar from '../Navbar/Navbar';
import Webcam from 'react-webcam'; // Importer React Webcam
import pointageService from '../../services/PointageService'; // Importer le service pour la vérification du visage
import './pointage.css';

const Pointage = () => {
  const [capturedImage, setCapturedImage] = useState(null); // État pour stocker l'image capturée
  const [responseImage, setResponseImage] = useState(null); // État pour stocker l'image retournée par l'API
  const [isWebcamOpen, setIsWebcamOpen] = useState(false); // État pour savoir si la webcam est ouverte
  const [type, setType] = useState("entry")
  const webcamRef = useRef(null); // Référence pour React Webcam
  const [pointages, setPointages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);


  // Capturer une image via React Webcam
  const capturePhoto = () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot(); // Capturer une photo
      setCapturedImage(imageSrc); // Stocker l'image capturée dans l'état
      setIsWebcamOpen(false); // Fermer la webcam après capture
    }
  };

  // Réinitialiser l'état et rouvrir la webcam pour une nouvelle capture
  const resetWebcam = () => {
    setCapturedImage(null);
    setResponseImage(null);
    setIsWebcamOpen(true);
  };

  // Gérer l'action ENTRY ou EXIT
  const handleAction = async (type) => {
    setType(type)
    resetWebcam(); // Réinitialiser la webcam avant de capturer l'image
    setTimeout(() => {
      capturePhoto(); // Capturer l'image après l'attente de 3 secondes
    }, 3000); // Attendre 3 secondes avant de capturer l'image
  };


  const handleGetPointage = async () => {
    const response = await pointageService.getAllPointages();
    setPointages(response);
  }
  // Utiliser useEffect pour envoyer l'image après sa capture
  useEffect(() => {
    handleGetPointage();
    if (capturedImage) {
      const processImage = async () => {
        try {
          setIsLoading(true); // Début du processus, active le chargement

          // Convertir l'image capturée en fichier (JPEG)
          const byteString = atob(capturedImage.split(',')[1]);
          const arrayBuffer = new ArrayBuffer(byteString.length);
          const view = new Uint8Array(arrayBuffer);
          for (let i = 0; i < byteString.length; i++) {
            view[i] = byteString.charCodeAt(i);
          }
          const file = new Blob([view], { type: 'image/jpeg' });

          // Vérifier le visage avec l'API
          const result = await pointageService.verifyFace(file);
          await pointageService.verifyFaceAndAddPointage(file, type);
          await handleGetPointage();

          // Vérifier si la réponse est un Blob avant de créer l'URL
          if (result instanceof Blob) {
            const url = URL.createObjectURL(result);
            setResponseImage(url); // Stocker l'URL de l'image retournée
          } else {
            console.error("La réponse de l'API n'est pas un fichier Blob.");
          }
        } catch (error) {
          console.error("Erreur lors de la conversion ou de l'appel API :", error);
        } finally {
          setIsLoading(false); // Fin du processus, désactive le chargement
        }
      };

      processImage(); // Appeler la fonction pour traiter l'image capturée
    }
  }, [capturedImage, type]);
  // Déclencher le useEffect chaque fois que capturedImage change

  return (
    <div className="page-ct">
      <div className="navbar-ct">
        <Navbar />
      </div>
      <div className="content pointage-content">
        <div className="top">
          <div className="actions">
            <button className="btn-green" onClick={() => handleAction("entry")}>
              ENTRY
            </button>
            <button className="btn-red" onClick={() => handleAction("exit")}>
              EXIT
            </button>
          </div>
          <div className="last-pic">
            {isLoading ? (
              <div className="spinner"></div> // Afficher le spinner pendant le chargement
            ) : responseImage ? (
              <img className='result-img' src={responseImage} alt="Face verification result" />
            ) : capturedImage ? (
              <img src={capturedImage} alt="Captured" />
            ) : (
              isWebcamOpen && (
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  width="50%"
                  videoConstraints={{ facingMode: "user" }}
                />
              )
            )}
            
          </div>

        </div>
        <div className="bottom">
          <table className="pointage-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Type</th>
                <th>Date</th>
                <th>Heure</th>
              </tr>
            </thead>
            <tbody>
              {pointages.map((pointage, index) => (
                <tr key={index}>
                  <td>{pointage.name}</td>
                  <td>{pointage.type}</td>
                  <td>{pointage.date}</td>
                  <td>{pointage.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  );
};

export default Pointage;
