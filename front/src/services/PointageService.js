import axios from "axios";
import toastr from "toastr"
const API_BASE_URL = "http://localhost:8000"; // Base URL de l'API

const pointageService = {
  // Ajouter un pointage
  async addPointage(individuId, type) {
    try {
      const response = await axios.post(`${API_BASE_URL}/add_pointage/`, {
        individu_id: individuId,
        type: type,
      });
      return response.data;
    } catch (error) {
      console.error("Erreur lors de l'ajout du pointage :", error);
      throw error.response?.data || error;
    }
  },

  // Vérifier un visage et créer un pointage
  async verifyFaceAndAddPointage(file, type) {
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("type", type);

      const response = await axios.post(`${API_BASE_URL}/verify_face_metadata/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toastr.success(response.data.message)

      return response.data;
    } catch (error) {
      console.error("Erreur lors de la vérification du visage :", error);
      throw error.response?.data || error;
    }
  },

  // Récupérer les pointages d'un individu
  async getPointages(individuId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/get_pointages/${individuId}`);
      return response.data;
    } catch (error) {
      console.error("Erreur lors de la récupération des pointages :", error);
      throw error.response?.data || error;
    }
  },


  async verifyFace(file) {
    try {
        const formData = new FormData();
        formData.append("file", file);

        // Envoi de la requête pour vérifier le visage
        const response = await axios.post(`${API_BASE_URL}/verify_face/`, formData, {
            headers: { "Content-Type": "multipart/form-data" },
            responseType: 'blob', // Demander une réponse en format Blob
        });

        // Vérification si la réponse est un Blob (image ou JSON)
        if (response.data instanceof Blob) {
            return response.data
        }
    } catch (error) {
        // Si l'erreur provient de la réponse de l'API (par exemple, un code d'erreur 400)
        if (error.response && error.response.data instanceof Blob) {
            // Convertir le Blob de l'erreur en texte pour obtenir un message JSON
            const text = await error.response.data.text();
            const errorObj = JSON.parse(text);
            toastr.error(errorObj.error || "Une erreur est survenue lors de la vérification du visage."); // Afficher l'erreur
        } else {
            // Si l'erreur ne vient pas de la réponse de l'API, afficher une erreur générique
            toastr.error("Une erreur est survenue lors de la vérification du visage.");
        }

        // Logguer les erreurs si elles surviennent
        throw error; // Retourner l'erreur si nécessaire
    }
},
async getAllPointages() {
  try {
    const response = await axios.get(`${API_BASE_URL}/get_pointages`);
    console.log(response.data);
    return response.data;
  } catch (error) {
    console.error("Erreur lors de la récupération de tous les pointages :", error);
    throw error.response?.data || error;
  }
},


  
};

export default pointageService;
