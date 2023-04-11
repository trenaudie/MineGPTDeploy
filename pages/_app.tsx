import '@/styles/globals.css';
import { appWithTranslation } from 'next-i18next';
import type { AppProps } from 'next/app';
import { Inter } from 'next/font/google';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from '@/components/Global/AuthContext';

const inter = Inter({ subsets: ['latin'] });

function App({ Component, pageProps }: AppProps<{}>) {
  return (
    <div className={inter.className}>
      <AuthProvider>
        <Toaster />
        <Component {...pageProps} />
      </AuthProvider>
    </div>
  );
}

export default appWithTranslation(App);
