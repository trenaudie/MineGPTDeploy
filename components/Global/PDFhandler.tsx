import React, { useState, CSSProperties, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
<<<<<<< HEAD
import { DocumentInitParameters } from 'pdfjs-dist/types/src/display/api';
import { SERVER_ADDRESS } from './Constants';
=======
import { useEffect } from 'react';
import { PDFDocumentProxy, PDFPageProxy, getDocument } from 'pdfjs-dist/types/src/pdf';

pdfjs.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.7.570/pdf.min.js";
>>>>>>> 5daf2cfcfe577bbaf8b35df713a56cb3ceb58119

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

// interface PdfViewerProps {
//   pdfFile: string | ArrayBuffer | Uint8Array | Blob | File | DocumentInitParameters;
// }

interface PdfViewerProps {
<<<<<<< HEAD
  pdfKey: string | ArrayBuffer | Uint8Array | Blob | File | DocumentInitParameters;
}

const PdfViewer: React.FC<PdfViewerProps> = ({ pdfKey }) => {
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pdfFile, setPdfFile] = useState<Blob | null>(null);
  const pdfUrl = `/pdf/${pdfKey}`;

  console.log("PdfViewer received pdfFile:", pdfUrl);
=======
  pdfFile: string;
}


const PdfViewer: React.FC<PdfViewerProps> = ({ pdfFile }) => {
  const [pdfData, setPdfData] = useState<PDFDocumentProxy>();

  useEffect(() => {
    const decode = (str: string):string => Buffer.from(str, 'base64').toString('binary');

    // Decode the base64 string and load the PDF
    const decodedPdfData = decode(pdfFile);
    const loadingTask = pdfjs.getDocument({ data: decodedPdfData });
    loadingTask.promise.then((pdf:PDFDocumentProxy) => {
      console.log(`typeof pdf ${typeof pdf}`)
      console.log('PDF loaded');
      setPdfData(pdf);
    });
  }, [pdfFile]);

  const [numPages, setNumPages] = useState<number | null>(null);
  console.log('PdfViewer received pdfFile:', pdfFile.substring(0,10));
>>>>>>> 5daf2cfcfe577bbaf8b35df713a56cb3ceb58119

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  const pageNumber = 1;
  return (
    <div style={styles.pdfContainer}>
      {pdfData && (
        <Document
          file={pdfData}
          onLoadSuccess={onDocumentLoadSuccess}
        >
          <div key={`page_${pageNumber}`} style={styles.page}>
            <Page pageNumber={pageNumber} />
          </div>
        </Document>
      )}
    </div>
  );
};

export default PdfViewer;
