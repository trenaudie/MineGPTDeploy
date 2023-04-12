// FileDownload.tsx
import React, { FC } from 'react';

interface FileDownloadProps {
    fileName: string;
    displayText: string;
}

const FileDownload: FC<FileDownloadProps> = ({ fileName, displayText }) => {
    const handleDownload = async () => {
        console.log(`${fileName}`)
        const response = await fetch(`http://localhost:5000/download/${fileName}`);
        console.log("document request sent")
        if (response.ok) {
            console.log("document request accepted")
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            console.error('Error fetching the document:', response.statusText);
        }
    };

    return (
        <span style={{ cursor: 'pointer', textDecoration: 'underline' }} onClick={handleDownload}>
            {displayText}
        </span>
    );
};

export default FileDownload;

