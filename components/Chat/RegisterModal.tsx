import React, { useContext, useState, useEffect } from 'react';
import { AuthContext } from '../Global/AuthContext';
import { setSecureCookie } from '../../utils/app/cookieTool'
import { SERVER_ADDRESS } from '../Global/Constants';

interface RegisterModalProps {
    onClose: () => void;
    setShowCode: React.Dispatch<React.SetStateAction<boolean>>;
    show: boolean;
    showCode: boolean
}

const RegisterModal: React.FC<RegisterModalProps> = ({ onClose, show, showCode, setShowCode }) => {
    const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);
    const [authError, setAuthError] = useState<string>('');
    const { authenticated, handleLogout, handleLogin } = useContext(AuthContext);
    const [email, setEmail] = useState<string | undefined>(undefined);
    const [password, setPassword] = useState<string | undefined>(undefined);


    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const formData = new FormData(event.target as HTMLFormElement);
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;


        if (password) {
            setEmail(email);
            setPassword(password)

            try {
                const response = await fetch(`${SERVER_ADDRESS}/ask_confirmation_code`, {
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
                if (response.ok && data.status == 'email sent') {
                    setShowCode(true)
                } else {
                    setAuthError("You can only register with your MinesParis student adress.");
                }
            } catch (error) {
                setAuthError("Failure to send email. Please try again");
            }
        } else {
            console.log("you fucked up the passwords")
            setAuthError("The passwords do not match. Please try again")
        }
    }


    const handleSubmitCode = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const formData = new FormData(event.target as HTMLFormElement);

        const confirmation = formData.get("confirmation_code");
        console.log(`authenticated = ${authenticated} before submission`)
        // Send the data to the backend
        try {
            const response = await fetch(`${SERVER_ADDRESS}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    confirmation_code: confirmation,
                }),
            });

            const data = await response.json();
            console.log(data);
            if (response.ok && data.status === 'registration successful!') {
                // Handle successful login (e.g., set user state, redirect, etc.)
                setSecureCookie("access_token", data.access_token);
                onClose(); // Close the LoginModal
            } else if (data.error_code) {
                // Handle error messages from backend
                console.log(data.error_message);
                setErrorMessage(data.error_message);
                
            } else if (data.status === 'failed registration') {
                // Handle incorrect login
                console.log(data.status)
                setAuthError('The confirmation code you provided is incorrect');
            } else if (data.status === "you can only register once") {
                console.log(data.status)
                setAuthError(data.status)}
        } catch (error) {
            setErrorMessage('An error occurred, please try again');
        }
    };

    useEffect(() => {
        console.log('useEffect called because show changed')
        if (!show) {
            setShowCode(false);
            setAuthError('');
            setErrorMessage(undefined);
            onClose();
        }
    }, [show, setShowCode]);

    return (
        <div
            className={`fixed inset-0 z-50 flex items-center justify-center ${show ? 'block' : 'hidden'
                }`}
        >
            <div className="bg-black opacity-50 fixed inset-0" onClick={onClose} />
            <div className="bg-white w-full max-w-md m-auto rounded shadow-lg z-50">
                <div className="py-4 px-8 text-black">
                    <h1 className="text-xl font-bold mb-4">Register</h1>

                    {!showCode && (
                        <form onSubmit={handleSubmit}>
                            {errorMessage && (
                                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                                    {errorMessage}
                                </div>
                            )}
                            {authError && (
                                <p className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{authError}</p>
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
                                className="flex items-center justify-center w-full h-10 px-4 py-2 text-white bg-#17181B border-2 border-white hover:bg-#0f1012 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 rounded transition duration-150 ease-in-out"
                                style={{ backgroundColor: '#17181B' }}
                                type="submit"
                            >
                                Register
                            </button>
                        </form>
                    )}
                    {showCode && (
                        <form onSubmit={handleSubmitCode}>
                            {errorMessage && (
                                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                                    {errorMessage}
                                </div>
                            )}
                            {authError && (
                                <p className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{authError}</p>
                            )}
                            <input
                                className="border w-full py-2 px-3 mb-4 rounded text-black"
                                type="text"
                                name="confirmation_code"
                                placeholder="Enter the 6-digit code"
                                required
                            />
                            <button
                                className="flex items-center justify-center w-full h-10 px-4 py-2 text-white bg-#17181B border-2 border-white hover:bg-#0f1012 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 rounded transition duration-150 ease-in-out"
                                style={{ backgroundColor: '#17181B' }}
                                type="submit"
                            >
                                Submit Code
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RegisterModal;
