import React, { useEffect, useState } from 'react';
import { HOSTNAME } from '../Constant';
import '../style/MonitoringTab.css';

const MonitoringTab = ({ token, onLogout }) => {
  const [nivel, setNivel] = useState(null);
  const [estado, setEstado] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    fetchEstado();
    const interval = setInterval(fetchEstado, 5000);
    return () => clearInterval(interval);
  }, [token]);

  const fetchEstado = async () => {
    try {
      const response = await fetch(`${HOSTNAME}/estado`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
      });

      if (response.status === 401) {
        onLogout();
        return;
      }

      const data = await response.json();
      setNivel(data.nivel || 0);
      setEstado(data.estado || 'Sin datos');
    } catch {
      setEstado('Error al cargar estado.');
    }
  };

  const nivelCritico = nivel !== null && nivel <= 20;

  const handleRellenar = async () => {
    setIsUpdating(true);
    try {
      const response = await fetch(`${HOSTNAME}/rellenar`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.status === 401) {
        onLogout();
        return;
      }

      if (response.ok) {
        await fetchEstado();  // Refresca estado
      } else {
        alert('Error al rellenar el alimento.');
      }
    } catch {
      alert('No se pudo conectar al servidor.');
    }
    setIsUpdating(false);
  };

  return (
    <div className="monitoring-tab-container">
      <h2 className="tab-title">📊 Monitoreo del Sistema</h2>

      <div className="monitoring-box">
        <p>
          <strong>📦 Nivel de alimento:</strong>{' '}
          <span style={{ color: nivelCritico ? 'red' : 'green', fontWeight: 'bold' }}>
            {nivel !== null ? `${nivel}%` : 'Cargando...'}
          </span>
        </p>

        {nivelCritico && (
          <div className="nivel-alerta">
            ⚠️ <strong>Alerta:</strong> El nivel de alimento es bajo. Por favor, recargue el dispensador.
            <br />
            <button
              className="rellenar-btn"
              onClick={handleRellenar}
              disabled={isUpdating}
            >
              {isUpdating ? 'Rellenando...' : '🔄 Rellenar alimento'}
            </button>
          </div>
        )}

        <p><strong>⚙️ Estado actual:</strong> {estado}</p>
      </div>
    </div>
  );
};

export default MonitoringTab;
