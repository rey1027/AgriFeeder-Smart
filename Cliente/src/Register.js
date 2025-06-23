import React, { useState } from 'react';
import './style/Register.css';
import Swal from "sweetalert2";
import { FaUser, FaEnvelope, FaLock, FaIdCard } from 'react-icons/fa';
import { HOSTNAME } from './Constant';

function Register({ onRegister, onBackToLogin }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Verificación de campos vacíos
    if (!name || !email || !username || !password) {
      Swal.fire({
        icon: "warning",
        title: "Campos incompletos",
        text: "Por favor, complete todos los campos.",
        timer: 3500,
      });
      return;
    }

    try {
      const response = await fetch(`${HOSTNAME}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        Swal.fire({
          position: "center",
          icon: "success",
          title: "Usuario registrado correctamente",
          text: "Ahora puede iniciar sesión.",
          timer: 3500,
        });
        onBackToLogin(); // Regresa al login
      } else {
        Swal.fire({
          icon: "error",
          title: "Error al registrar",
          text: data.message || "Ha ocurrido un error durante el registro.",
          timer: 3500,
        });
      }
    } catch (err) {
      console.error(err);
      Swal.fire({
        icon: "error",
        title: "Error de conexión",
        text: "No se pudo conectar al servidor.",
        timer: 3500,
      });
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <img src="https://i.ibb.co/ZzZg9c8D/Logo-de-granja-agricultura-org-nico-verde-y-marr-n.png" alt="Logo Ganadero" className="register-logo" />
        <h2>Registro de Usuario</h2>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label><FaIdCard /> Nombre completo:</label>
            <input
              type="text"
              placeholder="Ej: Juan Vega"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label><FaEnvelope /> Correo electrónico:</label>
            <input
              type="email"
              placeholder="Ej: correo@finca.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label><FaUser /> Nombre de usuario:</label>
            <input
              type="text"
              placeholder="Ej: juanv123"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label><FaLock /> Contraseña:</label>
            <input
              type="password"
              placeholder="Crea una contraseña segura"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button type="submit" className="register-button">📋 Registrarse</button>
        </form>
        <button onClick={onBackToLogin} className="back-button">🔙 Volver al Login</button>
      </div>
    </div>
  );
}

export default Register;
