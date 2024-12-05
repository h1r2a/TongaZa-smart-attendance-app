import axios from "axios";
import toastr from "toastr";
const API_BASE_URL = "http://localhost:8000"; // Remplacez par l'URL de votre backend

const individuService = {


  getAllIndividus: async (page = 1, pageSize = 8) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/get_all_individus`, {
        params: {
          page,
          page_size: pageSize, // correspond à "page_size" attendu par le backend
        },
      });
      return response.data; // Les métadonnées et les données paginées
    } catch (error) {
      console.error("Erreur lors de la récupération des individus:", error);
      throw error; // Remontez l'erreur si nécessaire
    }
  },
  


  // Ajouter un nouvel individu
  addIndividu: async (individu) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/add_individu/`, individu);
      return response.data;
    } catch (error) {
      return error
    }
  },

  // Récupérer un individu par son ID
  getIndividu: async (individuId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/get_individu/${individuId}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching individu:", error.response?.data || error.message);
      throw error;
    }
  },

  // Mettre à jour un individu par son ID
  updateIndividu: async (individuId, updatedData) => {
    try {
      const formData = new FormData();
      for (const key in updatedData) {
        formData.append(key, updatedData[key]);
      }
      const response = await axios.put(`${API_BASE_URL}/update_individu/${individuId}`, formData);
      return response.data;
    } catch (error) {
      console.error("Error updating individu:", error.response?.data || error.message);
      throw error;
    }
  },

  // Supprimer un individu par son ID
  deleteIndividu: async (individuId) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}/delete_individu/${individuId}`);
      return response.data;
    } catch (error) {
      console.error("Error deleting individu:", error.response?.data || error.message);
      throw error;
    }
  },

  // Upload d'une image pour un individu
  uploadPdp: async (individuId, file) => {
    try {
      const formData = new FormData();
      formData.append("individu_id", individuId);
      formData.append("file", file);

      const response = await axios.post(`${API_BASE_URL}/upload_pdp/`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } catch (error) {
      return error

    }
  },


  uploadFaceEncoding: async (file, name) => {
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("name", name);

      const response = await axios.post(`${API_BASE_URL}/upload_face/`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      return response.data; // The success message from FastAPI
    } catch (error) {
      return error
    }
  },


  deleteFaceEncoding: async (name) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}/delete_encoding/${name}`);
      toastr.success("People deleted successfully")
      return response.data; // Success message
    } catch (error) {
      console.error("Error deleting face encoding:", error);
      throw error;
    }
  },
};

export default individuService;
