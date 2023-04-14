// FileDownload.tsx
import React, { FC } from 'react';
import { SERVER_ADDRESS } from "./Constants";
import { getSecureCookie } from '@/utils/app/cookieTool';

interface FileDownloadProps {
    fileName: string;
    displayText: string;
}

const FileDownload: FC<FileDownloadProps> = ({ fileName, displayText }) => {
    const access_token = getSecureCookie("access_token");
    const handleDownload = async () => {
        const fileNameWithoutPath = fileName.replace("./temp/", "");
        console.log(`${fileNameWithoutPath}`)
        const response = await fetch(`${SERVER_ADDRESS}/download/${fileNameWithoutPath}`,
        {
            method: 'GET',
            headers:{
              'Authorization': `Bearer ${access_token}`
            }
          });
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

