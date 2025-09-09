import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  { ignores: ['dist'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
      // Temporarily allow any types in service/API files
      '@typescript-eslint/no-explicit-any': [
        'error',
        {
          'ignoreRestArgs': true
        }
      ],
    },
  },
  // Specific overrides for service files
  {
    files: ['src/services/**/*.ts', 'src/hooks/useApi.ts'],
    rules: {
      '@typescript-eslint/no-explicit-any': 'warn', // Downgrade to warning
    },
  },
  // Temporary overrides for files with many any types
  {
    files: [
      'src/components/**/*.tsx',
      'src/contexts/**/*.tsx', 
      'src/hooks/**/*.ts',
      'src/pages/**/*.tsx',
      'src/types/**/*.ts',
      'src/utils/**/*.ts'
    ],
    rules: {
      '@typescript-eslint/no-explicit-any': 'warn', // Temporarily downgrade to warning
    },
  }
);
