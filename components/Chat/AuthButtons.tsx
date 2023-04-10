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
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-4"
            >
                Register
            </button>
            <button
                onClick={onLoginClick}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
                Login
            </button>
        </div>
    );
};

export default AuthButtons;
