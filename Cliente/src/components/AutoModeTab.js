import React, { useState, useEffect } from 'react';
import { HOSTNAME } from '../Constant';
import '../style/AutoModeTab.css';

const AutoModeTab = ({ token, onLogout }) => {
  const [horaInicio, setHoraInicio] = useState('');
  const [intervalo, setIntervalo] = useState('');
  const [raciones, setRaciones] = useState('');
  const [mensaje, setMensaje] = useState('');

  const [configActual, setConfigActual] = useState(null);

  const obtenerConfiguracion = async () => {
    try {
      const response = await fetch(`${HOSTNAME}/auto-configu`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.status === 401) {
        onLogout();
        return;
      }

      const data = await response.json();
      setConfigActual(data);
    } catch {
      console.error("❌ Error al obtener la configuración actual");
    }
  };

  useEffect(() => {
    obtenerConfiguracion();
  }, []);

  const handleConfigurar = async () => {
    try {
      const response = await fetch(`${HOSTNAME}/auto-config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          hora_inicio: horaInicio,
          intervalo: parseInt(intervalo),
          raciones: parseInt(raciones)
        })
      });

      if (response.status === 401) {
        onLogout();
        return;
      }

      const data = await response.json();
      setMensaje(data.message || '✅ Configuración guardada.');
      obtenerConfiguracion(); // refresca los datos
    } catch {
      setMensaje('❌ Error al guardar configuración.');
    }
  };

  return (
    <div className="auto-tab-container">
      <h2 className="tab-title">Configuración de Modo Automático</h2>

      <div className="form-group">
        <label>🕒 Hora de inicio:</label>
        <input
          type="time"
          value={horaInicio}
          onChange={(e) => setHoraInicio(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>⏱ Intervalo (horas):</label>
        <input
          type="number"
          min="1"
          value={intervalo}
          onChange={(e) => setIntervalo(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>🍽 Raciones por horario:</label>
        <input
          type="number"
          min="1"
          value={raciones}
          onChange={(e) => setRaciones(e.target.value)}
        />
      </div>

      <button className="config-button" onClick={handleConfigurar}>💾 Guardar configuración</button>

      {mensaje && <p className="message">{mensaje}</p>}

      {configActual && (
        <div className="config-actual">
          <h3>⚙️ Configuración actual:</h3>
          <p><strong>Hora de inicio:</strong> {configActual.hora_inicio}</p>
          <p><strong>Intervalo (horas):</strong> {configActual.intervalo}</p>
          <p><strong>Raciones:</strong> {configActual.raciones}</p>
        </div>
      )}
    </div>
  );
};

export default AutoModeTab;
