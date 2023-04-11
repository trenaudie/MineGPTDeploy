import React, { createContext, useContext, useState } from 'react';

interface AuthState {
    authenticated: boolean;
    handleLogout: () => void;
    handleLogin: () => void;
}

const initialState: AuthState = {
    authenticated: false,
    handleLogout: () => { },
    handleLogin: () => { },
};

export const AuthContext = createContext<AuthState>(initialState);

export const AuthProvider: React.FC = ({ children }) => {
    const [authenticated, setAuthenticated] = useState(false);

    const handleLogout = () => {
        console.log('handleLogout called');
        setAuthenticated(false);
        // Perform the logout actions here
    };

    const handleLogin = () => {
        console.log('handleLogin called');
        setAuthenticated(true);
    };

    const value = {
        authenticated,
        handleLogout,
        handleLogin,
    };

    return <AuthContext.Provider value={ value }> { children } < /AuthContext.Provider>;
};

export const useAuthContext = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuthContext must be used within an AuthProvider');
    }
    return context;
};
