import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import toastr from 'toastr';

// ProtectedRoute component with password authentication
const ProtectedRoute = ({ children }) => {
  const [accessibility, setAccessibility] = useState(false); // Controls access
  const [isModalOpen, setModalOpen] = useState(true); // Controls modal visibility
  const [password, setPassword] = useState(""); // Stores the entered password

  // Function to validate the password
  const handlePasswordSubmit = (e) => {
    e.preventDefault(); // Prevent default form submission
    if (password === "12345678") {
      setAccessibility(true); // Access granted
      setModalOpen(false); // Close the modal
    } else {
      toastr.error("Incorrect password!");
    }
  };

  // Show the popup if the user doesn't have access
  if (!accessibility && isModalOpen) {
    return (
      <div style={modalStyles.overlay}>
        <div style={modalStyles.modal}>
          <h2>Password Required</h2>
          <form onSubmit={handlePasswordSubmit}>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={modalStyles.input}
            />
            <button type="submit" style={modalStyles.button}>
              Submit
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Redirect to the home page if access is denied
  if (!accessibility) {
    return <Navigate to="/" />;
  }

  return children;
};

// Modal styles
const modalStyles = {
  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    backgroundColor: "rgba(0, 0, 0, 0.7)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  modal: {
    backgroundColor: "white",
    padding: "20px",
    borderRadius: "8px",
    textAlign: "center",
    maxWidth: "400px",
    width: "100%",
  },
  input: {
    width: "100%",
    padding: "10px",
    marginBottom: "10px",
    borderRadius: "4px",
    border: "1px solid #ccc",
  },
  button: {
    padding: "10px 20px",
    backgroundColor: "#007BFF",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
};

export default ProtectedRoute;
