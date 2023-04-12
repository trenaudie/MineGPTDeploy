import Cookies from 'js-cookie';

const setSecureCookie = (name, value) => {
    Cookies.set(name, value, {
        secure: true,
        sameSite: 'strict', // 'strict' or 'lax', depending on your requirements
        // You can also set other options like 'expires' or 'path'
    });
};

// Usage:
// setSecureCookie('sessionId', receivedSessionId);
