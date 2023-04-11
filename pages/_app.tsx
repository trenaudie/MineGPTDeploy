import '@/styles/globals.css';
import { appWithTranslation } from 'next-i18next';
import type { AppProps } from 'next/app';
import { Inter } from 'next/font/google';
import { Toaster } from 'react-hot-toast';
import { AuthContext, useAuth, useAuthContext } from '@/components/Global/AuthContext';

const inter = Inter({ subsets: ['latin'] });

function App({ Component, pageProps }: AppProps<{}>) {
  const auth = useAuth();

  return (
    <div className={inter.className}>
      <AuthContext.Provider value={auth}>
        <Toaster />
        <Component {...pageProps} />
      </AuthContext.Provider>
    </div>
  );
}

export default appWithTranslation(App);
