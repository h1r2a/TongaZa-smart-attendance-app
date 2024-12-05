import React from "react";

const ConfirmationModal = ({ show, onConfirm, onCancel, actionType }) => {
  if (!show) return null;

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>{actionType === 'delete' ? 'Êtes-vous sûr de vouloir supprimer cet individu?' : 'Modifier cet individu?'}</h2>
        <div className="modal-actions">
          <button onClick={onCancel}>Annuler</button>
          <button onClick={onConfirm}>Confirmer</button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
