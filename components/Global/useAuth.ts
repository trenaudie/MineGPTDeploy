import { useState } from 'react';

interface AuthState {
    authenticated: boolean;
    handleLogout: () => void;
    handleLogin: () => void;
}

export const useAuth = (): AuthState => {
    const [authenticated, setAuthenticated] = useState(true);

    const handleLogout = () => {
        console.log('handleLogout called');
        setAuthenticated(false);
        // Perform the logout actions here
    };

    const handleLogin = () => {
        console.log('handleLogin called');
        setAuthenticated(true);
    };

    return {
        authenticated,
        handleLogout,
        handleLogin
    };
};
