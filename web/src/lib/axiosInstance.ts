import { Message } from '@arco-design/web-react';
import { client } from '../client/client.gen';
import { getEnvVar } from '@/utils/env';


function getCurrentProjectID() {
  return localStorage.getItem('projectID');
}


client.instance.interceptors.request.use((config) => {
  config.baseURL = getEnvVar('REACT_APP_API_BASE_URL');
  config.withCredentials = false;

  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  const projectID = getCurrentProjectID();
  if (projectID) {
    config.headers['X-Project-ID'] = projectID;
  }
  return config
});

client.instance.interceptors.response.use((response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 可以跳转登录页面，或清除token等
      console.warn('未授权，请重新登录');
      if (error.response.status === 401) {
        localStorage.removeItem('token');
        Message.loading({
          id: 'login-loading',
          content: '登录过期，请重新登录',
        });

        for (let i = 3; i >= 0; i--) {
          setTimeout(() => {
            Message.loading({
              id: 'login-loading',
              content: `登录过期，请重新登录, ${i}秒后自动跳转`,
            });
          }, (3 - i) * 1000);
        }
        setTimeout(() => {
          window.location.pathname = '/login';
        }, 3000);
      }
    } else if (error.response?.status === 403) {
      if (error.response?.data?.detail) {
        Message.warning(error.response?.data?.detail);
      } else {
        Message.warning('权限不足, 请联系管理员');
      }
    }
    return Promise.reject(error);
  }
);
