import React from 'react';
import { AuthContext } from '../Global/AuthContext';
import { setSecureCookie } from '../../utils/app/cookieTool'
import { SERVER_ADDRESS } from "../Global/Constants";
import { Docsource } from '@/types/docsource';
import { useContext } from 'react';
import { useState } from 'react';

interface LoginModalProps {
    onClose: () => void;
    show: boolean;
}


const LoginModal: React.FC<LoginModalProps> = ({ onClose, show }) => {
    // ... rest of the LoginModal component code ...
    const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);
    const [authError, setAuthError] = useState<string>('');
    const { authenticated, handleLogout, handleLogin, uploadDocs } = useContext(AuthContext);

    const onFailedAuthentification = () => {
        setAuthError('Password or Email address incorrect');
    }


    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const formData = new FormData(event.target as HTMLFormElement);
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;

        console.log("Sending data:", { email, password });

        // Send the data to the backend
        fetch(`${SERVER_ADDRESS}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password,
            }),

        })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    onFailedAuthentification()
                    throw new Error('An error occurred, please try again');
                }
            })
            .then(data => {
                console.log("Received data:", data);

                if (data.status === 'authenticated') {
                    // Handle successful login (e.g., set user state, redirect, etc.)
                    handleLogin(data);
                    setSecureCookie("access_token", data.access_token);
                    onClose(); // Close the LoginModal
                } else if (data.status === 'incorrect authentification') {
                    // Handle incorrect login
                    setAuthError('Incorrect password or Username');
                } else {
                    // Handle other errors (e.g., show a generic error message)
                    setAuthError('An error occurred, please try again');
                }
            });

    };

    return (
        <div
            className={`fixed inset-0 z-50 flex items-center justify-center ${show ? 'block' : 'hidden'
                }`}
        >
            <div className="bg-black opacity-50 fixed inset-0" onClick={onClose} />
            <div className="bg-white w-full max-w-md m-auto rounded shadow-lg z-50">
                <div className="py-4 px-8 text-black">
                    <h1 className="text-xl font-bold mb-4">Login</h1>
                    <form onSubmit={handleSubmit}>
                        {errorMessage && (
                            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                                {errorMessage}
                            </div>
                        )}
                        {authError && (
                            <p className="text-red-500 text-sm mt-2 mb-4">{authError}</p>
                        )}
                        <input
                            className="border w-full py-2 px-3 mb-4 rounded text-black"
                            type="email"
                            name="email"
                            placeholder="Username"
                            required
                        />
                        <input
                            className="border w-full py-2 px-3 mb-4 rounded text-black"
                            type="password"
                            name="password"
                            placeholder="Password"
                            required
                        />
                        <button
                            className="flex items-center justify-center w-full h-10 px-4 py-2 text-white bg-#17181B border-2 border-white hover:bg-#0f1012 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 rounded transition duration-150 ease-in-out"
                            style={{ backgroundColor: '#17181B' }}
                            type="submit"
                        >
                            Login
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};


export default LoginModal;