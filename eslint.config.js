import tseslint from 'typescript-eslint';
export default tseslint.config({ ignores: ['dist/**', '.venv/**', 'node_modules/**', 'playwright-report/**'] }, ...tseslint.configs.recommended, { rules: { '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }], 'no-empty': ['error', { allowEmptyCatch: true }] } });
