import { FC } from 'react';

interface LogoutButtonProps {
    text: string;
    icon: React.ReactNode;
    onClick: () => void;
}

export const LogoutButton: FC<LogoutButtonProps> = ({ text, icon, onClick }) => {
    return (
        <button onClick={onClick}>
            {icon}
            {text}
        </button>
    );
};
