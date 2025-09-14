import React, { useEffect, useRef } from 'react';

const LarkCallback = () => {
  const timeoutRef = useRef(null);

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const token = searchParams.get('token');

    if (token) {
    localStorage.setItem('userStatus', 'login');
    localStorage.setItem('token', token);
    console.log('token', token);

    // ✅ 立即跳转
    window.location.replace('/project');
    } else {
      // Handle the case where the token is not present
      console.error('Lark login callback did not receive a token.');
      // Optionally, redirect to an error page or the login page
      window.location.replace('/login');
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return <div>Loading...</div>;
};

export default LarkCallback;