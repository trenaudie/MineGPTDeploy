import Cookies from 'js-cookie';

export const setSecureCookie = (name: string, value: string) => {
  // Check if the current protocol is HTTPS
  const isSecure = window.location.protocol === 'https:';
  console.log(`setting secure cookie ${name} to ${value} with secure=${isSecure}`)
  Cookies.set(name, value, {
    secure: isSecure,
    sameSite: 'strict', // 'strict' or 'lax', depending on your requirements
    // You can also set other options like 'expires' or 'path'
  });
};

export const getSecureCookie = (name: string) => {
    return Cookies.get(name);
  };
  
  export const removeSecureCookie = (name: string) => {
    Cookies.remove(name);
  };
  
  // Usage:
  // removeSecureCookie('sessionId');
  
  // Usage:
  // const sessionId = getSecureCookie('sessionId');
  
// Usage:
// setSecureCookie('sessionId', receivedSessionId);
