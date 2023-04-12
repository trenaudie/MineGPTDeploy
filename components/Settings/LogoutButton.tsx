import { FC } from 'react';

interface LogoutButtonProps {
    text: string;
    icon: React.ReactNode;
    onClick: () => void;
}

export const LogoutButton: FC<LogoutButtonProps> = ({ text, icon, onClick }) => {
    return (
        <button
            className="flex items-center justify-center w-full h-10 px-4 py-2 text-white bg-#17181B border-2 border-white hover:bg-#0f1012 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 rounded transition duration-150 ease-in-out"
            style={{ backgroundColor: '#17181B' }}
            onClick={onClick}
        >
            {icon}
            <span className="ml-2">{text}</span>
        </button>
    );
};
