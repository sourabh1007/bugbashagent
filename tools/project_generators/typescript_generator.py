"""
Simplified TypeScript Project Generator

Only creates minimal project structure, lets LLM generate actual implementation files.
No dummy test files are created automatically.
"""

import os
import json
from typing import Dict, List, Any
from .base_generator import BaseProjectGenerator


class TypeScriptProjectGenerator(BaseProjectGenerator):
    """Simplified generator for TypeScript projects - no automatic test file generation"""
    
    def __init__(self):
        super().__init__()
        self.language = 'typescript'
    
    def generate_project(self, project_dir: str, product_name: str, scenarios: List[str], generated_content: str, analyzer_output: Dict[str, Any] = None) -> Dict[str, str]:
        """Generate minimal TypeScript project structure - only essential files, no dummy tests"""
        created_files = {}
        
        # Create essential project files for TypeScript
        # 1. Create package.json with TypeScript packages and configured versions
        package_json = self._create_package_json_content(product_name)
        package_json_file = os.path.join(project_dir, "package.json")
        with open(package_json_file, 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)
        created_files["package_json"] = package_json_file
        
        # 2. Create tsconfig.json for TypeScript configuration
        tsconfig_json = self._create_tsconfig_content()
        tsconfig_file = os.path.join(project_dir, "tsconfig.json")
        with open(tsconfig_file, 'w', encoding='utf-8') as f:
            json.dump(tsconfig_json, f, indent=2)
        created_files["tsconfig_json"] = tsconfig_file
        
        # 3. Create jest.config.js for TypeScript testing
        jest_config = self._create_jest_config_content()
        jest_config_file = os.path.join(project_dir, "jest.config.js")
        with open(jest_config_file, 'w', encoding='utf-8') as f:
            f.write(jest_config)
        created_files["jest_config"] = jest_config_file
        
        # 4. Create src directory structure
        src_dir = os.path.join(project_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        created_files["src_directory"] = src_dir
        
        # 5. Create tests directory structure
        tests_dir = os.path.join(project_dir, "tests")
        os.makedirs(tests_dir, exist_ok=True)
        created_files["tests_directory"] = tests_dir
        
        # 6. Create types directory for custom type definitions
        types_dir = os.path.join(project_dir, "types")
        os.makedirs(types_dir, exist_ok=True)
        created_files["types_directory"] = types_dir
        
        # 7. Create .gitignore for TypeScript projects
        gitignore_content = self._create_gitignore_content()
        gitignore_file = os.path.join(project_dir, ".gitignore")
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        created_files["gitignore"] = gitignore_file
        
        # 8. Create README.md with TypeScript-specific instructions
        readme_content = self._create_readme_content(product_name)
        readme_file = os.path.join(project_dir, "README.md")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created_files["readme"] = readme_file
        
        return created_files
    
    def _create_package_json_content(self, product_name: str) -> Dict[str, Any]:
        """Create package.json content with TypeScript-specific dependencies"""
        node_version = self.get_language_version('node')
        jest_version = self.get_language_version('jest')
        typescript_version = self.get_language_version('typescript')
        
        return {
            "name": product_name.lower().replace(' ', '-'),
            "version": "1.0.0",
            "description": f"TypeScript implementation for {product_name}",
            "main": "dist/index.js",
            "types": "dist/index.d.ts",
            "scripts": {
                "build": "tsc",
                "build:watch": "tsc --watch",
                "start": "node dist/index.js",
                "dev": "ts-node src/index.ts",
                "test": "jest",
                "test:watch": "jest --watch",
                "test:coverage": "jest --coverage",
                "lint": "eslint src/**/*.ts",
                "lint:fix": "eslint src/**/*.ts --fix",
                "clean": "rimraf dist"
            },
            "keywords": ["typescript", "testing", product_name.lower()],
            "author": "Bug Bash Copilot",
            "license": "MIT",
            "engines": {
                "node": f">={node_version}"
            },
            "dependencies": {
                # Production dependencies will be added by LLM based on scenarios
            },
            "devDependencies": {
                "typescript": f"^{typescript_version}",
                f"jest": f"^{jest_version}",
                "@types/jest": "^29.5.5",
                "ts-jest": "^29.1.1",
                "@types/node": "^20.8.0",
                "ts-node": "^10.9.1",
                "eslint": "^8.50.0",
                "@typescript-eslint/eslint-plugin": "^6.7.0",
                "@typescript-eslint/parser": "^6.7.0",
                "rimraf": "^5.0.1"
            }
        }
    
    def _create_tsconfig_content(self) -> Dict[str, Any]:
        """Create tsconfig.json content for TypeScript compilation"""
        return {
            "compilerOptions": {
                "target": "ES2020",
                "lib": ["ES2020"],
                "module": "commonjs",
                "declaration": True,
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True,
                "moduleResolution": "node",
                "allowSyntheticDefaultImports": True,
                "experimentalDecorators": True,
                "emitDecoratorMetadata": True,
                "sourceMap": True,
                "baseUrl": ".",
                "paths": {
                    "@/*": ["src/*"],
                    "@types/*": ["types/*"]
                }
            },
            "include": [
                "src/**/*",
                "types/**/*"
            ],
            "exclude": [
                "node_modules",
                "dist",
                "**/*.test.ts",
                "**/*.spec.ts"
            ],
            "ts-node": {
                "esm": True
            }
        }
    
    def _create_jest_config_content(self) -> str:
        """Create jest.config.js content for TypeScript testing"""
        return '''module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: [
    '**/__tests__/**/*.ts',
    '**/?(*.)+(spec|test).ts'
  ],
  transform: {
    '^.+\\.ts$': 'ts-jest'
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts',
    '!src/**/*.spec.ts'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: [
    'text',
    'lcov',
    'html'
  ],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@types/(.*)$': '<rootDir>/types/$1'
  },
  setupFilesAfterEnv: []
};
'''
    
    def _create_gitignore_content(self) -> str:
        """Create .gitignore content for TypeScript projects"""
        return '''# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Build outputs
dist/
build/
*.tsbuildinfo

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# ESLint cache
.eslintcache

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity
'''
    
    def _create_readme_content(self, product_name: str) -> str:
        """Create README.md content for TypeScript projects"""
        return f'''# {product_name}

TypeScript implementation generated by Bug Bash Copilot.

## Prerequisites

- Node.js >= 18.0.0
- npm or yarn

## Installation

```bash
npm install
```

## Development

```bash
# Build the project
npm run build

# Start development mode with hot reload
npm run dev

# Watch mode for continuous building
npm run build:watch
```

## Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## Running the Application

```bash
# Run the built application
npm start

# Or run directly from TypeScript source
npm run dev
```

## Linting

```bash
# Check for linting errors
npm run lint

# Fix linting errors automatically
npm run lint:fix
```

## Project Structure

```
src/           # TypeScript source files
tests/         # Test files
types/         # Custom type definitions
dist/          # Compiled JavaScript output
coverage/      # Test coverage reports
```

## Scripts

- `build`: Compile TypeScript to JavaScript
- `start`: Run the compiled application
- `dev`: Run TypeScript directly with ts-node
- `test`: Run Jest tests
- `lint`: Check code quality with ESLint
'''
