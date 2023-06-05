// FileDownload.tsx
import React, { FC, useState } from 'react';
import { SERVER_ADDRESS } from "./Constants";
import { getSecureCookie } from '@/utils/app/cookieTool';
import { ErrorMessageDiv } from '../Chat/ErrorMessageDiv';
import { ErrorMessage } from '@/types/error';
import { VariableModal } from '../Chat/VariableModal';

interface FileDownloadProps {
    fileName: string;
    displayText: string;
}

const FileDownload: FC<FileDownloadProps> = ({ fileName, displayText }) => {
    const [error, setError] = useState<ErrorMessage | null>(null);
    const access_token = getSecureCookie("access_token");
    const handleDownload = async () => {
        const fileNameWithoutPath = fileName.replace("./temp/", "");
        console.log(`${fileNameWithoutPath}`)
        try {
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
              setError({
                title: 'Error fetching document',
                messageLines: [response.statusText],
                code: ` ${response.status}` || null
              });
            }
          } catch (e : any) {
            setError({
              title: 'Error fetching document',
              messageLines: [e.message],
              code: `${e.code}` || null
            });
          } 
};
return (
    <div>
    <span style={{ cursor: 'pointer', textDecoration: 'underline' }} onClick={handleDownload}>
        {displayText}
        
    </span>
    {error && <ErrorMessageDiv error={error}/>}
    </div>
   
);
}
export default FileDownload;

