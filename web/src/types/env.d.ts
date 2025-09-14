export {};

declare global {
  interface Window {
    env: {
      REACT_APP_API_BASE_URL: string;
      REACT_APP_LARK_CLIENT_ID: string;
      REACT_APP_LARK_REDIRECT_URI: string;
    };
  }
}