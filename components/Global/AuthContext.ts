import React, { createContext, useContext, useState } from 'react';


export const AuthContext = createContext<AuthState | null>(null);


export const useAuthContext = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuthContext must be used within an AuthProvider');
    }
    return context;
};

interface AuthState {
    authenticated: boolean;
    handleLogout: () => void;
    handleLogin: () => void;
}

export const useAuth = (): AuthState => {
    const [authenticated, setAuthenticated] = useState(false);

    const handleLogout = () => {
        console.log('handleLogout called');
        setAuthenticated(false);
        // Perform the logout actions here
    };

    const handleLogin = () => {
        console.log('handleLogin called')
        setAuthenticated(true)
    }

    return {
        authenticated,
        handleLogout,
        handleLogin,
    };
};
