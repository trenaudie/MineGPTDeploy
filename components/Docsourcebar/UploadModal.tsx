import React from 'react';

const customStyles = {
    overlay: 'fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50',
    content: 'bg-white w-full max-w-md m-auto rounded shadow-lg z-50 py-4 px-8 text-black',
};

interface UploadModalProps {
    show: boolean;
    onClose: () => void;
    onAgree: () => void;
}

const UploadModal: React.FC<UploadModalProps> = ({ show, onClose, onAgree }) => {
    return (
        <div className={`${customStyles.overlay} ${show ? 'block' : 'hidden'}`}>
            <div className={customStyles.content}>
                <h2>Upload Document</h2>
                <p>
                    Veillez bien à n'uploader des documents sur le site avec l'accord de la personne concerné.
                    Nous ne sommes pas responsables des données que vous uploadez vous même sur le site.
                </p>
                <button onClick={onAgree}>Agree</button>
            </div>
            <div
                className="bg-black opacity-50 fixed inset-0 cursor-default"
                onClick={onClose}
            ></div>
        </div>
    );
};

export default UploadModal;
