import React, { useState } from 'react';
import { FaTractor, FaEye, FaHandsHelping, FaSignOutAlt, FaChartBar } from 'react-icons/fa';
import AutoModeTab from './components/AutoModeTab';
import MonitoringTab from './components/MonitoringTab';
import ManualModeTab from './components/ManualModeTab';
import ReportsTab from './components/ReportsTab';
import './style/PrincipalPage.css';

const PrincipalPage = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState('auto');
  const token = localStorage.getItem('token');

  const handleLogout = () => {
    localStorage.removeItem('token');
    onLogout();
  };

  return (
    <div className="feeder-control">
      <header className="menu-bar">
        <img
          src="https://i.ibb.co/0yXVdpgy/logo.png"
          alt="Logo"
          className='logo'
        />
        <h1> AgroFeeder Smart</h1>
        <button onClick={handleLogout} className="logout-button">
          <FaSignOutAlt /> Cerrar sesión
        </button>
      </header>

      <div className="tabs">
        <button onClick={() => setActiveTab('auto')} className={activeTab === 'auto' ? 'active' : ''}>
          <FaTractor /> Automático
        </button>
        <button onClick={() => setActiveTab('monitoring')} className={activeTab === 'monitoring' ? 'active' : ''}>
          <FaEye /> Monitoreo
        </button>
        <button onClick={() => setActiveTab('manual')} className={activeTab === 'manual' ? 'active' : ''}>
          <FaHandsHelping /> Manual
        </button>
        { /*Botón futuro para reportes*/
        <button onClick={() => setActiveTab('reports')} className={activeTab === 'reports' ? 'active' : ''}>
          <FaChartBar /> Reportes
        </button> 
        }
      </div>

      <main className="tab-content">
        {activeTab === 'auto' && <AutoModeTab />}
        {activeTab === 'monitoring' && <MonitoringTab token={token} onLogout={onLogout} />}
        {activeTab === 'manual' && <ManualModeTab token={token} onLogout={onLogout} />}
        {activeTab === 'reports' && <ReportsTab token={token} onLogout={onLogout}/> }
      </main>
    </div>
  );
};

export default PrincipalPage;
