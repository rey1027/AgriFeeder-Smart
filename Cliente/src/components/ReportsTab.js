import React, { useEffect, useState } from 'react';
import { HOSTNAME } from '../Constant';
import '../style/ReportsTab.css';

const ReportsTab = ({ token, onLogout }) => {
  const [registros, setRegistros] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRegistros = async () => {
      try {
        const response = await fetch(`${HOSTNAME}/reportes`, {
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
        setRegistros(data.registros || []);
      } catch {
        setError('Error al cargar los reportes.');
      }
    };

    fetchRegistros();
  }, [token, onLogout]);

  return (
    <div className="reports-tab-container">
      <h2 className="tab-title">📑 Reportes de Alimentación</h2>

      {error && <p className="error-message">{error}</p>}

      <div className="table-container">
        <table className="reports-table">
          <thead>
            <tr>
              <th>🗓️ Fecha</th>
              <th>⏰ Hora</th>
              <th>🥣 Raciones</th>
              <th>⚙️ Modo</th>
            </tr>
          </thead>
          <tbody>
            {registros.length > 0 ? (
              registros.map((r, i) => (
                <tr key={i}>
                  <td>{r.fecha}</td>
                  <td>{r.hora}</td>
                  <td>{r.raciones}</td>
                  <td>{r.modo}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" className="text-center">No hay registros disponibles.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ReportsTab;