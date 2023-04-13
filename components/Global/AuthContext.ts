import React, { createContext, useContext, useState } from 'react';
import { Docsource } from '@/types/docsource';
import { LoginData } from '@/types/loginData';


interface AuthState {
  docs: Docsource[],
  authenticated: boolean;
  handleLogout: () => void;
  handleLogin: (data:LoginData) => void;
  uploadDocs: (docs: Docsource[]) => void;
}

const initialState: AuthState = {
  authenticated: false,
  docs: [],
  handleLogout: () => { },
  handleLogin: () => { },
  uploadDocs: (docs: Docsource[]) => { },
}

export const AuthContext = createContext<AuthState>(initialState);



// export const useAuthContext = () => {
//   const context = useContext(AuthContext);
//   if (!context) {
//     throw new Error('useAuthContext must be used within an AuthProvider');
//   }
//   return context;
// };
