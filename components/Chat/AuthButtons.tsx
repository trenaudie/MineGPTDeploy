import React from 'react';

interface AuthButtonsProps {
    onLoginClick?: () => void;
    onRegisterClick?: () => void;
}

const AuthButtons: React.FC<AuthButtonsProps> = ({
    onLoginClick,
    onRegisterClick,
}) => {
    return (
        <div className="text-center mt-4">
            <button
                onClick={onRegisterClick}
                className="mr-4 text-white font-bold py-2 px-4 rounded bg-#17181B border-2 border-white hover:bg-#0f1012 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 rounded transition duration-150 ease-in-out"
            >
                Register
            </button>
            <button
                onClick={onLoginClick}
                className="text-white font-bold py-2 px-4 rounded bg-#17181B border-2 border-white hover:bg-#0f1012 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 rounded transition duration-150 ease-in-out"
            >
                Login
            </button>
        </div>
    );
};

export default AuthButtons;
