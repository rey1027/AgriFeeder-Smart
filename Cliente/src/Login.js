import React, { useState } from 'react';
import './style/Login.css';
import Swal from "sweetalert2";
import { FaUser, FaLock } from 'react-icons/fa';
import { HOSTNAME } from './Constant';

function Login({ onLogin, onShowRegister }) {

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false); // Nuevo estado de carga

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!username || !password) {
      Swal.fire({
        icon: "warning",
        title: "Cuidado!",
        text: "Debes ingresar usuario y contraseña",
        timer: 3000,
      });
      return;
    }

    setLoading(true); // Inicia carga

    try {
      const response = await fetch(`${HOSTNAME}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        Swal.fire({
          icon: "success",
          title: "Inicio de sesión exitoso",
          timer: 2500,
        });

        localStorage.setItem('token', data.token);
        localStorage.setItem('user', username);

        onLogin(username, password, data.token);
      } else {
        Swal.fire({
          icon: "error",
          title: "Error",
          text: data.message || "Credenciales inválidas",
          timer: 3500,
        });
      }

    } catch (err) {
      console.error(err);
      Swal.fire({
        icon: "error",
        title: "Error de conexión",
        text: "No se pudo conectar al servidor",
        timer: 3500,
      });
    }

    setLoading(false); // Finaliza carga
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <img
          src="https://i.ibb.co/ZzZg9c8D/Logo-de-granja-agricultura-org-nico-verde-y-marr-n.png"
          alt="Logo"
          className="login-logo"
        />
        <h2>Agrofeeder Smart</h2>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label><FaUser /> Nombre de usuario:</label>
            <input
              type="text"
              placeholder="Usuario"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          <div className="input-group">
            <label><FaLock /> Contraseña:</label>
            <input
              type="password"
              placeholder="Contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>
          {error && <p className="error-message">{error}</p>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? " Cargando..." : "  Iniciar Sesión"}
          </button>

          <button
            type="button"
            className="register-button"
            onClick={onShowRegister}
            disabled={loading}
          >
           Registrarse
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
