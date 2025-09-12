// Node.js script to install dependencies
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Installing Soleva Frontend Dependencies...\n');

// Check if node_modules exists
if (fs.existsSync('node_modules')) {
  console.log('📁 Removing existing node_modules...');
  try {
    execSync('rmdir /s /q node_modules', { stdio: 'inherit', shell: true });
  } catch (error) {
    console.log('⚠️ Could not remove node_modules, continuing...');
  }
}

// Remove package-lock.json
if (fs.existsSync('package-lock.json')) {
  console.log('📄 Removing package-lock.json...');
  fs.unlinkSync('package-lock.json');
}

// Clear npm cache
console.log('🧹 Clearing npm cache...');
try {
  execSync('npm cache clean --force', { stdio: 'inherit' });
} catch (error) {
  console.log('⚠️ Could not clear cache, continuing...');
}

// Install dependencies
console.log('📦 Installing dependencies...');
try {
  execSync('npm install --no-audit --no-fund --legacy-peer-deps', { 
    stdio: 'inherit',
    timeout: 300000 // 5 minutes timeout
  });
  console.log('✅ Dependencies installed successfully!');
} catch (error) {
  console.log('❌ First install attempt failed, trying alternative...');
  try {
    execSync('npm install --force', { 
      stdio: 'inherit',
      timeout: 300000
    });
    console.log('✅ Dependencies installed successfully with --force!');
  } catch (error2) {
    console.error('❌ Failed to install dependencies:', error2.message);
    process.exit(1);
  }
}

// Verify installation
console.log('🔍 Verifying installation...');
if (fs.existsSync('node_modules')) {
  console.log('✅ node_modules directory created');
  
  // Check key packages
  const keyPackages = ['react', 'vite', 'typescript', 'tailwind-merge'];
  let allInstalled = true;
  
  keyPackages.forEach(pkg => {
    if (fs.existsSync(path.join('node_modules', pkg))) {
      console.log(`✅ ${pkg} installed`);
    } else {
      console.log(`❌ ${pkg} missing`);
      allInstalled = false;
    }
  });
  
  if (allInstalled) {
    console.log('\n🎉 All dependencies installed successfully!');
    console.log('\nAvailable commands:');
    console.log('  npm run dev      - Start development server');
    console.log('  npm run build    - Build for production');
    console.log('  npm run preview  - Preview production build');
  } else {
    console.log('\n⚠️ Some packages may be missing. Please check manually.');
  }
} else {
  console.log('❌ node_modules directory not found');
}

console.log('\n✨ Setup completed!');
