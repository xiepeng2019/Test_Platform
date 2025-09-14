export function getEnvVar(key: string, fallback = ''): string {
  if (window?.env?.[key]) {
    return window.env?.[key];
  }
  console.warn(`Missing env var ${key}`);
  return fallback;
}
