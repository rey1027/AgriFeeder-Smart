import React, { useState } from 'react';
import Login from './Login';
import Register from './Register';

function Auth({ onLogin, onRegister }) {
  const [showRegister, setShowRegister] = useState(false);

  const handleShowRegister = () => setShowRegister(true);
  const handleShowLogin = () => setShowRegister(false);

  return (
    <>
      {showRegister ? (
        <Register onRegister={onRegister} onBackToLogin={handleShowLogin} />
      ) : (
        <Login onLogin={onLogin} onShowRegister={handleShowRegister} />
      )}
    </>
  );
}

export default Auth;