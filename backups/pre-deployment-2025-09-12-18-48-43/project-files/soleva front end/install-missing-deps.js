#!/usr/bin/env node

/**
 * Install Missing ESLint Dependencies
 * 
 * This script installs the missing ESLint dependencies that are required
 * for the TypeScript ESLint configuration to work properly.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔧 Installing missing ESLint dependencies...');

const packageJsonPath = path.join(__dirname, 'package.json');
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

// Check if we need to install dependencies
const requiredDeps = [
  '@eslint/js',
  'globals', 
  'typescript-eslint'
];

const missingDeps = requiredDeps.filter(dep => 
  !packageJson.devDependencies || !packageJson.devDependencies[dep]
);

if (missingDeps.length === 0) {
  console.log('✅ All required ESLint dependencies are already installed!');
  process.exit(0);
}

console.log(`📦 Installing missing dependencies: ${missingDeps.join(', ')}`);

try {
  // Install the missing dependencies
  const installCommand = `npm install --save-dev ${missingDeps.join(' ')}`;
  console.log(`Running: ${installCommand}`);
  
  execSync(installCommand, { 
    stdio: 'inherit',
    cwd: __dirname 
  });
  
  console.log('✅ Successfully installed missing ESLint dependencies!');
  console.log('🚀 You can now run: npm run lint');
  
} catch (error) {
  console.error('❌ Failed to install dependencies:', error.message);
  console.log('\n💡 Please run manually:');
  console.log(`   npm install --save-dev ${missingDeps.join(' ')}`);
  process.exit(1);
}
