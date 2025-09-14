import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: 'http://localhost:8000/openapi.json',
  output: {
    format: 'prettier',
    path: './src/client',
    lint: 'eslint',
    tsConfigPath: './tsconfig.json',
  },
  plugins: [
    {
      name: '@hey-api/client-axios',
      // runtimeConfigPath: './src/hey-api.ts',
    },
    '@hey-api/schemas',
    {
      dates: true,
      name: '@hey-api/transformers',
    },
    {
      enums: 'javascript',
      name: '@hey-api/typescript',
    },
    {
      name: '@hey-api/sdk',
      transformer: true,
    }
  ],
});