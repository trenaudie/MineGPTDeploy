import { useState } from 'react';

interface AuthState {
    authenticated: boolean;
    handleLogout: () => void;
}

export const useAuth = (): AuthState => {
    const [authenticated, setAuthenticated] = useState(false);

    const handleLogout = () => {
        console.log('handleLogout called');
        setAuthenticated(false);
        // Perform the logout actions here
    };

    return {
        authenticated,
        handleLogout,
    };
};
