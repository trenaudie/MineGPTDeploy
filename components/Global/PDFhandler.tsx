import React, { useState, CSSProperties, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { DocumentInitParameters } from 'pdfjs-dist/types/src/display/api';
import { SERVER_ADDRESS } from './Constants';

// Define the CSS styles as a JavaScript object
const styles: { [key: string]: CSSProperties } = {
  pdfContainer: {
    overflowY: 'scroll',
    height: '100vh', // Adjust this value according to your desired container height
    border: '1px solid #ccc',
  },
  page: {
    marginBottom: '1rem',
  },
};

interface PdfViewerProps {
  pdfKey: string | ArrayBuffer | Uint8Array | Blob | File | DocumentInitParameters;
}

const PdfViewer: React.FC<PdfViewerProps> = ({ pdfKey }) => {
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pdfFile, setPdfFile] = useState<Blob | null>(null);
  const pdfUrl = `/pdf/${pdfKey}`;

  console.log("PdfViewer received pdfFile:", pdfUrl);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  useEffect(() => {
    fetch(`${SERVER_ADDRESS}/pdf/${pdfKey}`)
      .then((response) => response.blob())
      .then((blob) => {
        setPdfFile(blob);
      })
      .catch((error) => {
        console.error("Error fetching PDF file:", error);
      });
  }, [pdfKey]);


  return (
    <div style={styles.pdfContainer}>
      <Document
        file={pdfFile}
        onLoadSuccess={onDocumentLoadSuccess}
        options={{ workerSrc: `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js` }}
      >
        {Array.from(new Array(numPages), (el, index) => (
          <div key={`page_${index + 1}`} style={styles.page}>
            <Page pageNumber={index + 1} />
          </div>
        ))}
      </Document>
    </div>
  );
};

export default PdfViewer;
