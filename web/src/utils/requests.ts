import axios, { AxiosError } from 'axios';
import { getEnvVar } from './env';



export function isAxiosError(obj: any): obj is AxiosError {
  return obj && obj.isAxiosError === true;
}


// 创建 axios 实例
console.log('REACT_APP_API_BASE_URL', getEnvVar('REACT_APP_API_BASE_URL'));
const r = axios.create({
  baseURL: getEnvVar('REACT_APP_API_BASE_URL'),
  timeout: 5000, // 请求超时时间
});

// 请求拦截器
r.interceptors.request.use(
  (config) => {
    // 在发送请求之前做些什么，例如添加 token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // 对请求错误做些什么
    return Promise.reject(error);
  }
);

// 响应拦截器
r.interceptors.response.use(
  (response) => {
    switch (response.status) {
      case 401:
        localStorage.removeItem('token');
        window.location.pathname = '/login';
        break;
      default:
        break;
    }
    return response;
  },
  (error) => {
    // 对响应错误做点什么
    return Promise.reject(error);
  }
);

export default r;