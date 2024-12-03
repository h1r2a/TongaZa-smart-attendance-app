import React, { useState, useEffect } from 'react';
import Navbar from '../Navbar/Navbar';
import './individu.css';
import { CiSearch } from "react-icons/ci";
import individuService from '../../services/IndividuService';
import toastr from "toastr"
const Individu = () => {
  const [peoples, setPeoples] = useState([]);
  const [name, setName] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  // Récupérer la liste des individus
  const handleGetPeople = async () => {
    const data = await individuService.getAllIndividus();
    setPeoples(data);
  };

  const handleAddIndividu = async () => {
    if (name && file) {
      setLoading(true);
      let addedIndividu = null;

      try {
        // Étape 1: Ajouter l'individu (Nom)
        const idInit = "";
        const individu = { name, id: idInit };
        addedIndividu = await individuService.addIndividu(individu);

        // Étape 2: Téléchargement de l'image de face et encodage
        const faceEncodingResponse = await individuService.uploadFaceEncoding(file, addedIndividu.id);

        // Vérifier si une erreur est présente dans la réponse
        if (faceEncodingResponse?.response?.data?.error) {
          console.error("Erreur d'encodage du visage:", faceEncodingResponse.response.data.error);

          // Supprimer l'individu en cas d'erreur
          await individuService.deleteIndividu(addedIndividu.id);

          // Afficher le message d'erreur retourné par le back-end
          toastr.error(faceEncodingResponse.response.data.error);
          return; // Arrêter le processus ici
        }

        // Étape 3: Téléchargement de la photo de profil
        await individuService.uploadPdp(addedIndividu.id, file);

        // Rafraîchir la liste des individus
        handleGetPeople();

        // Afficher un message de succès
        setName("")
        setFile(null)
        toastr.success("Individu ajouté avec succès !");
      } catch (error) {
        // Afficher l'erreur pour faciliter le débogage
        console.error("Erreur lors de l'ajout de l'individu:", error);

        // Supprimer l'individu en cas d'erreur pendant le processus
        if (addedIndividu) {
          await individuService.deleteIndividu(addedIndividu.id);
        }

        // Afficher un message d'erreur générique
        toastr.error("Une erreur est survenue lors de l'ajout de l'individu.");
      } finally {
        // Désactiver le chargement
        setLoading(false);
      }
    } else {
      toastr.error("Veuillez remplir tous les champs.");
    }
  };





  useEffect(() => {
    handleGetPeople();
  }, []);

  return (
    <div className="page-ct">
      <div className="navbar-ct">
        <Navbar />
      </div>
      <div className="content individu-content">
        <div className="listing">
          <div className="ls-header">
            <input type="text" placeholder="Search Someone" />
            <CiSearch color="white" />
          </div>

          <div className="individu list">
            {peoples.map((people) => (
              <div key={people.id} className="card">
                <img
                  src={`uploads/profile/${people.imageFile}`}
                  alt={people.name}
                  className="card-img"
                />
                <div className="card-content">
                  <h3 className="card-name">{people.name}</h3>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="add-form">
          <div className="form-header">
            <h1>TongaZa</h1>
            <p className="form-description">Tongaza is an AI-powered attendance app using face recognition for accurate attendance tracking.</p>
            <p className="form-description">With TongaZa, you can effortlessly track attendance in real-time with the power of AI and facial recognition.</p>
            <p className="form-description">Ensure accurate records of your team or students with seamless face recognition technology, minimizing manual errors.</p>
          </div>


          <div className="form">
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            <div className="file-input">
              <input
                type="file"
                onChange={(e) => setFile(e.target.files[0])}
              />
            </div>

            <button onClick={handleAddIndividu} disabled={loading}>
              {loading ? "Chargement..." : "Ajouter"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Individu;
