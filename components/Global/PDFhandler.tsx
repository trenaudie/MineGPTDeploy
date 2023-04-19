import React, { useState, CSSProperties } from 'react';
import { Document, Page } from 'react-pdf';
import { DocumentInitParameters } from 'pdfjs-dist/types/src/display/api';

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
  pdfFile: string | ArrayBuffer | Uint8Array | Blob | File | DocumentInitParameters;
}

const PdfViewer: React.FC<PdfViewerProps> = ({ pdfFile }) => {
  const [numPages, setNumPages] = useState<number | null>(null);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  return (
    <div style={styles.pdfContainer}>
      <Document
        file={pdfFile}
        onLoadSuccess={onDocumentLoadSuccess}
        options={{ workerSrc: '/pdf.worker.js' }}
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
