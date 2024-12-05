import React, { useState, useEffect } from 'react';
import Navbar from '../Navbar/Navbar';
import './individu.css';
import { CiSearch } from "react-icons/ci";
import individuService from '../../services/IndividuService';
import toastr from "toastr";

const Individu = () => {
  const [peoples, setPeoples] = useState([]);
  const [name, setName] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const pageSize = 8; // Nombre d'éléments par page

  // Récupérer la liste paginée des individus
  const handleGetPeople = async (page = 1) => {
    try {
      const data = await individuService.getAllIndividus(page, pageSize);
      setPeoples(data.data); // Les individus
      setCurrentPage(data.page); // Page actuelle
      setTotalPages(data.total_pages); // Nombre total de pages
    } catch (error) {
      console.error("Erreur lors de la récupération des individus:", error);
      toastr.error("Impossible de récupérer les individus.");
    }
  };

  const handleAddIndividu = async () => {
    if (name && file) {
      setLoading(true);
      let addedIndividu = null;

      try {
        const idInit = "";
        const individu = { name, id: idInit };
        addedIndividu = await individuService.addIndividu(individu);

        const faceEncodingResponse = await individuService.uploadFaceEncoding(file, addedIndividu.id);

        if (faceEncodingResponse?.response?.data?.error) {
          console.error("Erreur d'encodage du visage:", faceEncodingResponse.response.data.error);
          await individuService.deleteIndividu(addedIndividu.id);
          toastr.error(faceEncodingResponse.response.data.error);
          return;
        }

        await individuService.uploadPdp(addedIndividu.id, file);

        handleGetPeople(currentPage);
        setName("");
        setFile(null);
        toastr.success("Individu ajouté avec succès !");
      } catch (error) {
        console.error("Erreur lors de l'ajout de l'individu:", error);
        if (addedIndividu) {
          await individuService.deleteIndividu(addedIndividu.id);
        }
        toastr.error("Une erreur est survenue lors de l'ajout de l'individu.");
      } finally {
        setLoading(false);
      }
    } else {
      toastr.error("Veuillez remplir tous les champs.");
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      handleGetPeople(currentPage + 1);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      handleGetPeople(currentPage - 1);
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

          <div className="individu ">
            <div className="list">
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

            <div className="pagination">
              <button 
                className="page-btn" 
                onClick={handlePreviousPage} 
                disabled={currentPage === 1}>
                «
              </button>
              <span className="page-number">Page {currentPage} of {totalPages}</span>
              <button 
                className="page-btn" 
                onClick={handleNextPage} 
                disabled={currentPage === totalPages}>
                »
              </button>
            </div>
          </div>
        </div>

        <div className="add-form">
          <div className="form-header">
            <h1>TongaZa</h1>
            <p className="form-description">
              Tongaza is an AI-powered attendance app using face recognition for accurate attendance tracking.
            </p>
            <p className="form-description">
              With TongaZa, you can effortlessly track attendance in real-time with the power of AI and facial recognition.
            </p>
            <p className="form-description">
              Ensure accurate records of your team or students with seamless face recognition technology, minimizing manual errors.
            </p>
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
