# Rollup Build Issue Fix

## 🐛 Issue Identified

**Error:** `Cannot find module @rollup/rollup-linux-x64-gnu`

**Root Cause:** This is a known npm bug with optional dependencies when using Rollup's native binaries on Linux platforms in GitHub Actions.

**Reference:** https://github.com/npm/cli/issues/4828

## ✅ Solution Applied

### 1. Updated GitHub Actions Workflow

**File:** `.github/workflows/frontend.yml`

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '22'
    # Disabled npm cache to avoid native dependency issues

- name: Clear npm cache and install dependencies
  run: |
    npm cache clean --force
    # Use npm install instead of npm ci for better optional dependency handling
    npm install
    # Explicitly install latest rollup
    npm install rollup@latest
  env:
    # Force npm to rebuild native dependencies
    npm_config_build_from_source: true
```

### 2. Updated Package Dependencies

**File:** `package.json`

```json
{
  "devDependencies": {
    "rollup": "^4.21.0",  // Added explicit Rollup version
    "vite": "5.4.5"       // Latest compatible Vite version
  }
}
```

### 3. Key Changes Made

1. **Disabled npm cache** - Prevents issues with cached native binaries
2. **Use `npm install` instead of `npm ci`** - Better handling of optional dependencies
3. **Explicit Rollup installation** - Ensures latest version with proper native binaries
4. **Build from source flag** - Forces rebuilding of native dependencies
5. **Clear npm cache** - Starts with clean state

## 🎯 Expected Results

After these changes, the GitHub Actions workflow should:

1. ✅ Use Node.js 22 correctly
2. ✅ Install all dependencies including Rollup native binaries
3. ✅ Pass TypeScript compilation
4. ✅ Pass ESLint checks
5. ✅ Build successfully with Vite/Rollup
6. ✅ Create production-ready build artifacts

## 🔧 Alternative Solutions (if needed)

If the issue persists, here are additional approaches:

### Option A: Use Rollup with specific platform
```bash
npm install @rollup/rollup-linux-x64-gnu --save-dev
```

### Option B: Force platform-specific installation
```yaml
- name: Install platform-specific Rollup
  run: |
    npm install --platform=linux --arch=x64 rollup
```

### Option C: Use Vite without Rollup optimization
```javascript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      // Disable native optimizations
      nativeOptimizations: false
    }
  }
})
```

## 🚀 Verification Steps

1. **Commit and push** the updated workflow and package.json
2. **Check GitHub Actions** - Workflow should now complete successfully
3. **Monitor build logs** - Verify Rollup installation and build process
4. **Test deployment** - Ensure build artifacts are created properly

## 📝 Notes

- This fix addresses a specific npm/Rollup compatibility issue on Linux CI environments
- The solution maintains full build functionality while ensuring compatibility
- Native binary rebuilding may slightly increase build time but ensures reliability
- Future Rollup/npm updates may resolve this issue, allowing us to revert to cached builds

**Status: Ready for testing in GitHub Actions** ✅
