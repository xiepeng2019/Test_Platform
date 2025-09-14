import { getEnvVar } from "./env";

export default (config: { mock?: boolean; setup: () => void }) => {
  const { mock = getEnvVar('NODE_ENV') === 'development', setup } = config;
  if (mock === false) return;
  setup();
};
