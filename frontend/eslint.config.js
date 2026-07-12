import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
  },
  {
    // shadcn/ui-generated primitives: vendor code we own but don't
    // hand-author. It legitimately co-exports cva() variant maps
    // alongside components, and uses the pre-17 `import * as React`
    // form as a matter of template convention (unused with the
    // automatic JSX runtime, but harmless).
    files: ['src/components/ui/**/*.jsx'],
    rules: {
      'no-unused-vars': 'off',
      'react-refresh/only-export-components': 'off',
    },
  },
  {
    // Route config, not component modules — Fast Refresh doesn't apply.
    files: ['src/router/**/*.jsx'],
    rules: {
      'react-refresh/only-export-components': 'off',
    },
  },
])
