import React, { useState, useEffect } from 'react';
import PrincipalPage from './PrincipalPage';
import Auth from './Auth';
import './style/App.css';

const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));

    const handleLogin = (user, pass, token) => setIsLoggedIn(true);
    const handleLogout = () => setIsLoggedIn(false);
    const handleRegister = (data) => {console.log('Registro:', data);};

    return (
        <>
            {isLoggedIn ? (
                <PrincipalPage onLogout={handleLogout} />
            ) : (
                <Auth onLogin={handleLogin} onRegister={handleRegister} />
            )}
        </>
    );
};

export default App;
