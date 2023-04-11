import React, { useContext, useState } from 'react';
import { AuthContext } from '../Global/AuthContext';


interface RegisterModalProps {
    onClose: () => void;
    show: boolean;
}

const RegisterModal: React.FC<RegisterModalProps> = ({ onClose, show }) => {
    const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);
    const { authenticated, handleLogout, handleLogin } = useContext(AuthContext);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const formData = new FormData(event.target as HTMLFormElement);
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;
        console.log(`before auth context`)
        console.log(`authenticated = ${authenticated} before submission`)
        // Send the data to the backend
        try {
            const response = await fetch('http://localhost:5000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                }),
            });

            const data = await response.json();
            console.log(data);

            if (response.ok && data.status === 'registration successful!') {
                // Handle successful login (e.g., set user state, redirect, etc.)
                handleLogin()
                onClose(); // Close the LoginModal
            } else if (data.status === 'failed registration') {
                // Handle incorrect login
                setErrorMessage('You are not allowed to access this Website');
            } else {
                // Handle other errors (e.g., show a generic error message)
                setErrorMessage('An error occurred, please try again');
            }
        } catch (error) {
            console.error('Fetch error:', error);
            setErrorMessage('An error occurred, please try again');
        }
    };

    return (
        <div
            className={`fixed inset-0 z-50 flex items-center justify-center ${show ? 'block' : 'hidden'
                }`}
        >
            <div className="bg-black opacity-50 fixed inset-0" onClick={onClose} />
            <div className="bg-white w-full max-w-md m-auto rounded shadow-lg z-50">
                <div className="py-4 px-8 text-black">
                    <h1 className="text-xl font-bold mb-4">Register</h1>
                    <form onSubmit={handleSubmit}>
                        {errorMessage && (
                            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                                {errorMessage}
                            </div>
                        )}
                        <input
                            className="border w-full py-2 px-3 mb-4 rounded text-black"
                            type="email"
                            name="email"
                            placeholder="Email"
                            required
                        />
                        <input
                            className="border w-full py-2 px-3 mb-4 rounded text-black"
                            type="password"
                            name="password"
                            placeholder="Password"
                            required
                        />
                        <input
                            className="border w-full py-2 px-3 mb-4 rounded text-black"
                            type="password"
                            name="confirm_password"
                            placeholder="Confirm Password"
                            required
                        />
                        <button
                            className="w-full py-2 px-3 rounded bg-black text-white font-bold"
                            type="submit"
                        >
                            Register
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default RegisterModal;
