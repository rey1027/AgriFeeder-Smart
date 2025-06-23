import React, { useState } from 'react';
import { HOSTNAME } from '../Constant';
import '../style/ManualModeTab.css';

const ManualModeTab = ({ token, onLogout }) => {
  const [porciones, setPorciones] = useState(1);
  const [mensaje, setMensaje] = useState('');

  const handleDispensar = async () => {
    try {
      const response = await fetch(`${HOSTNAME}/manual-feed`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ porciones: parseInt(porciones) })
      });

      if (response.status === 401) {
        onLogout();
        return;
      }

      const data = await response.json();
      setMensaje(data.message || '✅ Dispensado exitosamente.');
    } catch {
      setMensaje('❌ Error al dispensar alimento.');
    }
  };

  return (
    <div className="manual-tab-container">
      <h2 className="tab-title">🖐️ Dispensación Manual</h2>

      <div className="form-group">
        <label>🥣 Cantidad de porciones:</label>
        <input
          type="number"
          min="1"
          max="10"
          value={porciones}
          onChange={(e) => setPorciones(e.target.value)}
        />
      </div>

      <button className="dispense-button" onClick={handleDispensar}>🚜 Dispensar</button>

      {mensaje && <p className="message">{mensaje}</p>}
    </div>
  );
};

export default ManualModeTab;
