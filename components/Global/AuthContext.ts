import React, { createContext, useContext, useState } from 'react';

interface AuthState {
  authenticated: boolean;
  handleLogout: () => void;
  handleLogin: () => void;
}

const initialState: AuthState = {
  authenticated: false,
  handleLogout: () => {},
  handleLogin: () => {}
};

export const AuthContext = createContext<AuthState>(initialState);

console.log('');


// export const useAuthContext = () => {
//   const context = useContext(AuthContext);
//   if (!context) {
//     throw new Error('useAuthContext must be used within an AuthProvider');
//   }
//   return context;
// };
